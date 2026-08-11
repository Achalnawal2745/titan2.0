"""
TITAN Security System — Voice ID, Face ID & Passcode Gate
──────────────────────────────────────────────────────────
Security Layers:
  1. STARTUP GATE  : Face OR Voice OR Passcode must pass to open TITAN.
  2. VOICE LOCK    : When ON, only owner voice is processed by mic.
  3. TOGGLE GUARD  : To disable any lock, must re-verify Face OR Voice OR Passcode.
  4. PIN IS SECRET : TITAN AI never sees or knows the passcode.
"""

import hashlib
import os
import sys
import json
import time
import numpy as np
from pathlib import Path

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

try:
    from scipy.signal import spectrogram
    from scipy.fft import dct
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR   = _get_base_dir()
MEMORY_DIR = BASE_DIR / "memory"
VOICE_FILE = MEMORY_DIR / "owner_voice.npy"
FACE_FILE  = MEMORY_DIR / "owner_face.npy"
CONFIG_FILE = MEMORY_DIR / "security_config.json"

MEMORY_DIR.mkdir(parents=True, exist_ok=True)


# ── CONFIG ───────────────────────────────────────────────────────────────────
def _default_config() -> dict:
    return {
        "security_lock": False,      # Single Master Security Lock Switch
        "startup_gate": False,
        "voice_lock": False,
        "face_lock": False,
        "voice_enrolled": False,
        "face_enrolled": False,
        "pin_hash": "",
        "voice_threshold": 0.65,
        "face_threshold": 0.25,
    }

def set_master_security_lock(enable: bool) -> dict:
    cfg = get_security_config()
    cfg["security_lock"] = bool(enable)
    cfg["voice_lock"]    = bool(enable)
    cfg["face_lock"]     = bool(enable)
    cfg["startup_gate"]   = bool(enable)
    save_security_config(cfg)
    return cfg

def get_security_config() -> dict:
    cfg = _default_config()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            cfg.update(saved)
        except Exception:
            pass
    # Sync enrollment flags with file existence
    cfg["voice_enrolled"] = VOICE_GMM_FILE.exists() or VOICE_FILE.exists()
    cfg["face_enrolled"]  = FACE_FILE.exists()
    # Keep master flag in sync with locks
    if "security_lock" not in cfg:
        cfg["security_lock"] = cfg.get("voice_lock", False) or cfg.get("face_lock", False) or cfg.get("startup_gate", False)
    return cfg

def save_security_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


# ── PIN HASHING (never stored as plaintext) ──────────────────────────────────
def _hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.strip().encode("utf-8")).hexdigest()

def verify_pin(pin: str) -> bool:
    """Check pin against stored hash. Returns False if no pin set."""
    cfg = get_security_config()
    stored = cfg.get("pin_hash", "")
    if not stored:
        return False
    return _hash_pin(pin) == stored

def set_pin(pin: str):
    """Store a new PIN as SHA-256 hash."""
    cfg = get_security_config()
    cfg["pin_hash"] = _hash_pin(pin)
    save_security_config(cfg)
    print("[Security] Owner PIN updated.")


VOICE_GMM_FILE = MEMORY_DIR / "owner_voice_gmm.pkl"

def extract_mfcc_frames(pcm_data: bytes, sample_rate: int = 16000) -> np.ndarray | None:
    """Extract CMVN-normalized MFCC+Delta frame sequence for GMM speaker modeling."""
    if not pcm_data or len(pcm_data) < 3200:
        return None
    try:
        audio = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32)
        peak_val = np.max(np.abs(audio))
        if peak_val < 1500:
            return None
        audio = audio / (peak_val + 1e-6)

        if _SCIPY_AVAILABLE:
            f, t, Sxx = spectrogram(audio, fs=sample_rate, nperseg=512, noverlap=256)
            Sxx = np.log(Sxx + 1e-6)
            mfcc = dct(Sxx, type=2, axis=0, norm='ortho')[1:13]  # 12 MFCCs excluding c0
            delta = np.gradient(mfcc, axis=1)
            frames = np.vstack([mfcc, delta]).T  # (N_frames, 24)
            frames = (frames - np.mean(frames, axis=0)) / (np.std(frames, axis=0) + 1e-6)
            return frames
        return None
    except Exception as e:
        print(f"[VoiceID] Frame extraction error: {e}")
        return None


def extract_voice_embedding(pcm_data: bytes, sample_rate: int = 16000) -> np.ndarray | None:
    """Legacy voice embedding fallback."""
    frames = extract_mfcc_frames(pcm_data, sample_rate)
    if frames is None:
        return None
    feat = np.concatenate([np.mean(frames, axis=0), np.std(frames, axis=0)])
    norm = np.linalg.norm(feat)
    return feat / norm if norm > 0 else None


# ── RAM CACHING FOR ZERO LATENCY ──────────────────────────────────────────────
_OWNER_VOICE_GMM_CACHE = None

def get_owner_voice_gmm():
    global _OWNER_VOICE_GMM_CACHE
    if _OWNER_VOICE_GMM_CACHE is not None:
        return _OWNER_VOICE_GMM_CACHE
    if VOICE_GMM_FILE.exists():
        try:
            import pickle
            with open(VOICE_GMM_FILE, 'rb') as f:
                _OWNER_VOICE_GMM_CACHE = pickle.load(f)
            print("[VoiceID] Loaded GMM owner voice model into RAM cache.")
            return _OWNER_VOICE_GMM_CACHE
        except Exception:
            pass
    return None

def clear_voice_ram_cache():
    global _OWNER_VOICE_GMM_CACHE
    _OWNER_VOICE_GMM_CACHE = None


_VOICE_GATE_BUFFER = bytearray()

def clear_voice_gate_buffer():
    global _VOICE_GATE_BUFFER
    _VOICE_GATE_BUFFER.clear()

def verify_voice(pcm_data: bytes) -> bool:
    """
    Real-time zero-latency voice gate for continuous mic stream.
    Accumulates rolling speech buffer to evaluate GMM score stably.
    """
    global _VOICE_GATE_BUFFER
    cfg = get_security_config()
    if not cfg.get("voice_lock"):
        return True

    gmm = get_owner_voice_gmm()
    if gmm is None:
        return True

    if pcm_data:
        _VOICE_GATE_BUFFER.extend(pcm_data)
        # Keep rolling 0.5 second of audio (16000 bytes = 8000 samples @ 16kHz int16)
        if len(_VOICE_GATE_BUFFER) > 16000:
            _VOICE_GATE_BUFFER = _VOICE_GATE_BUFFER[-16000:]

    # Pass through until buffer has at least 0.25s (8000 bytes) of audio
    if len(_VOICE_GATE_BUFFER) < 8000:
        return True

    frames = extract_mfcc_frames(bytes(_VOICE_GATE_BUFFER))
    if frames is None:
        return True

    try:
        score = float(gmm.score(frames))
        matched = score > -48.0
        if not matched:
            print(f"[VoiceID] ⛔ Unrecognized speaker ignored (GMM score: {score:.2f} < -48.0)")
        return matched
    except Exception:
        return True


def _verify_voice_sample(pcm_data: bytes) -> bool:
    """One-shot voice verification using GMM log-likelihood score."""
    if not VOICE_GMM_FILE.exists():
        return False
    frames = extract_mfcc_frames(pcm_data)
    if frames is None:
        return False
    try:
        import pickle
        with open(VOICE_GMM_FILE, 'rb') as f:
            gmm = pickle.load(f)
        score = float(gmm.score(frames))
        matched = score > -38.0
        print(f"[VoiceID] GMM voice verification score: {score:.2f} (threshold: -38.0) -> {'MATCH ✅' if matched else 'REJECT ❌'}")
        return matched
    except Exception as e:
        print(f"[VoiceID] GMM score error: {e}")
        return False


# ── FACE FEATURE EXTRACTION (YuNet DNN — OpenCV 5.0) ────────────────────────
YUNET_MODEL = MEMORY_DIR / "face_detection_yunet.onnx"

def _get_face_detector(w: int, h: int):
    """Create YuNet face detector for given image dimensions."""
    model_path = str(YUNET_MODEL)
    if not YUNET_MODEL.exists():
        return None
    return cv2.FaceDetectorYN.create(model_path, "", (w, h), 0.6, 0.3, 5000)

def extract_face_embedding(image_bytes: bytes) -> np.ndarray | None:
    """Extract 128-dim facial embedding from image bytes using YuNet DNN."""
    if not _CV2_AVAILABLE or not image_bytes:
        return None
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None

        h, w, _ = img.shape
        detector = _get_face_detector(w, h)
        if detector is None:
            print("[FaceID] YuNet model not found at", YUNET_MODEL)
            return None

        _, faces = detector.detect(img)
        if faces is None or len(faces) == 0:
            print("[FaceID] No face detected in frame.")
            return None

        # Extract face ROI from first detected face
        face = faces[0]
        x, y, fw, fh = int(face[0]), int(face[1]), int(face[2]), int(face[3])
        # Clamp to image bounds
        x, y = max(0, x), max(0, y)
        fw = min(fw, w - x)
        fh = min(fh, h - y)
        if fw < 10 or fh < 10:
            return None

        face_roi = cv2.cvtColor(img[y:y+fh, x:x+fw], cv2.COLOR_BGR2GRAY)
        face_roi = cv2.resize(face_roi, (128, 128))

        # Normalized histogram embedding
        hist, _ = np.histogram(face_roi, bins=128, range=(0, 256))
        feat = hist.astype(np.float32)
        norm = np.linalg.norm(feat)
        return feat / norm if norm > 0 else None
    except Exception as e:
        print(f"[FaceID] Extraction error: {e}")
        return None


def _verify_face_live() -> bool:
    """Capture multiple webcam frames with auto-exposure warmup and verify face."""
    if not _CV2_AVAILABLE or not FACE_FILE.exists():
        return False
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False

        # Camera auto-exposure warmup (discard 5 initial dark frames)
        for _ in range(5):
            cap.read()
            time.sleep(0.04)

        owner_feat = np.load(FACE_FILE)
        best_similarity = 0.0

        # Sample across 5 frames over 0.5s
        for _ in range(5):
            ret, frame = cap.read()
            if ret and frame is not None:
                _, buf = cv2.imencode('.jpg', frame)
                feat = extract_face_embedding(buf.tobytes())
                if feat is not None:
                    sim = float(np.dot(feat, owner_feat))
                    if sim > best_similarity:
                        best_similarity = sim
            time.sleep(0.05)
        cap.release()

        cfg = get_security_config()
        thresh = cfg.get("face_threshold", 0.25)
        print(f"[FaceID] Best similarity score across frames: {best_similarity:.3f} (threshold: {thresh})")
        return best_similarity >= thresh
    except Exception as e:
        print(f"[FaceID] Live verify error: {e}")
        return False


def verify_face(image_bytes: bytes) -> bool:
    """Verify face from provided image bytes."""
    cfg = get_security_config()
    if not cfg.get("face_lock") or not FACE_FILE.exists():
        return True

    feat = extract_face_embedding(image_bytes)
    if feat is None:
        return False
    try:
        owner_feat = np.load(FACE_FILE)
        similarity = float(np.dot(feat, owner_feat))
        thresh = cfg.get("face_threshold", 0.25)
        return similarity >= thresh
    except Exception:
        return True


# ── ENROLLMENT ───────────────────────────────────────────────────────────────
def enroll_owner(voice_data: bytes = None, face_image: bytes = None) -> str:
    """Enroll owner's voice and/or face embeddings and automatically activate locks."""
    results = []
    cfg = get_security_config()

    if voice_data:
        frames = extract_mfcc_frames(voice_data)
        if frames is not None and len(frames) >= 10:
            try:
                from sklearn.mixture import GaussianMixture
                gmm = GaussianMixture(n_components=4, covariance_type='diag', random_state=42)
                gmm.fit(frames)
                import pickle
                with open(VOICE_GMM_FILE, 'wb') as f:
                    pickle.dump(gmm, f)
                clear_voice_ram_cache()
                cfg["voice_enrolled"] = True
                results.append("Voice enrolled successfully! 🎙✓")
            except Exception as e:
                results.append(f"Voice training error: {e}")
        else:
            results.append("Could not extract voice. Speak clearly into mic for 3 seconds.")

    if face_image:
        f_feat = extract_face_embedding(face_image)
        if f_feat is not None:
            np.save(FACE_FILE, f_feat)
            cfg["face_enrolled"] = True
            results.append("Face enrolled successfully! 📸✓")
        else:
            results.append("Could not detect face. Look directly at camera.")

    save_security_config(cfg)
    return "\n".join(results) if results else "Provide voice or face data for enrollment."


# ── STARTUP AUTHENTICATION GATE ──────────────────────────────────────────────
def startup_authenticate(pin_input: str = None,
                          voice_data: bytes = None,
                          face_check: bool = False) -> bool:
    """
    Startup gate: returns True if ANY ONE of these passes:
      1. PIN matches
      2. Voice matches
      3. Face matches (live webcam)
    Returns True immediately if startup_gate is disabled or no enrollment exists.
    """
    cfg = get_security_config()

    # If startup gate is not enabled, pass through
    if not cfg.get("startup_gate"):
        return True

    # If nothing is enrolled yet, pass through
    if not cfg["voice_enrolled"] and not cfg["face_enrolled"] and not cfg.get("pin_hash"):
        return True

    # Check PIN
    if pin_input and verify_pin(pin_input):
        print("[Security] Startup auth: PIN verified ✅")
        return True

    # Check Voice
    if voice_data and _verify_voice_sample(voice_data):
        print("[Security] Startup auth: Voice verified ✅")
        return True

    # Check Face (live webcam capture)
    if face_check and _verify_face_live():
        print("[Security] Startup auth: Face verified ✅")
        return True

    return False


# ── TOGGLE GUARD — re-authenticate before disabling locks ────────────────────
def _guard_toggle_off(pin: str = None) -> bool:
    """
    When someone tries to turn OFF a security lock, verify identity first.
    Must pass at least ONE of: Face (live) OR PIN.
    Voice is not checked here because someone could be using a recording.
    """
    # Try face first (live webcam)
    if _verify_face_live():
        print("[Security] Toggle guard: Face verified ✅")
        return True

    # Try PIN
    if pin and verify_pin(pin):
        print("[Security] Toggle guard: PIN verified ✅")
        return True

    return False


# ── TITAN TOOL ENTRY POINT ───────────────────────────────────────────────────
def voice_face_id(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """
    Tool entry point for TITAN AI.
    
    Actions:
        "enroll_face"   — Capture webcam and save owner face
        "enroll_voice"  — Record 3s mic and save owner voice
        "status"        — Show security status (PIN is NEVER shown)
        "toggle"        — Enable/disable locks
            mode: "voice" | "face" | "gate" | "both"
            enable: True (ON) or False (OFF — requires face verification)
    
    IMPORTANT: TITAN AI never receives or knows the PIN value.
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    cfg    = get_security_config()

    if player:
        player.write_log(f"[Security] {action}")

    # ── STATUS ──
    if action == "status":
        v_status = ("✅ Active" if cfg["voice_lock"] else "🔓 Off") if cfg["voice_enrolled"] else "❌ Not enrolled"
        f_status = ("✅ Active" if cfg["face_lock"]  else "🔓 Off") if cfg["face_enrolled"]  else "❌ Not enrolled"
        gate     = "✅ Enabled" if cfg.get("startup_gate") else "🔓 Off"
        pin_set  = "✅ Set" if cfg.get("pin_hash") else "❌ Not set"
        return (
            f"🛡️ TITAN SECURITY STATUS:\n"
            f"  • Startup Gate : {gate}\n"
            f"  • Voice Lock   : {v_status}\n"
            f"  • Face Lock    : {f_status}\n"
            f"  • Passcode     : {pin_set}\n"
            f"  • Owner        : Achal Nawal"
        )

    # ── ENROLL FACE (open visual camera window on UI) ──
    elif action in ("enroll_face", "register_face", "enroll face"):
        if player and hasattr(player, "show_face_enroll_dialog"):
            player.show_face_enroll_dialog()
            return "📸 Opening camera preview window on screen. Look at the camera and click CAPTURE FACE!"
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "❌ Cannot open webcam. Make sure camera is connected."
            time.sleep(0.5)
            ret, frame = cap.read()
            cap.release()
            if not ret or frame is None:
                return "❌ Failed to capture frame from webcam."
            _, buf = cv2.imencode('.jpg', frame)
            result = enroll_owner(face_image=buf.tobytes())
            if player and hasattr(player, "refresh_security_ui"):
                player.refresh_security_ui()
            return f"📸 {result}"
        except Exception as e:
            return f"❌ Face enrollment error: {e}"

    # ── ENROLL VOICE (3s mic recording) ──
    elif action in ("enroll_voice", "register_voice", "enroll voice"):
        if player:
            player.write_log("[Security] 🎙 Recording voice for 3 seconds...")
        try:
            import sounddevice as sd
            duration = 3
            sr = 16000
            print("[Security] 🎙 Recording 3 seconds of voice...")
            audio = sd.rec(int(duration * sr), samplerate=sr,
                           channels=1, dtype='int16', blocking=True)
            pcm_data = audio.tobytes()
            result = enroll_owner(voice_data=pcm_data)
            if player and hasattr(player, "refresh_security_ui"):
                player.refresh_security_ui()
            return f"🎙 {result}"
        except Exception as e:
            return f"❌ Voice enrollment error: {e}"

    # ── TOGGLE ──
    elif action == "toggle":
        enable = params.get("enable", True)
        cfg = get_security_config()

        # TURNING ON — allowed freely if enrolled
        if enable:
            if not cfg["voice_enrolled"] and not cfg["face_enrolled"] and not cfg.get("pin_hash"):
                return "Please enroll your face/voice or set a passcode first before turning on security."
            set_master_security_lock(True)
            if player and hasattr(player, "refresh_security_ui"):
                player.refresh_security_ui()
            return "🔒 Master Security Lock is now ENABLED!"

        # TURNING OFF — requires face re-authentication!
        else:
            face_ok = _verify_face_live()
            if face_ok:
                set_master_security_lock(False)
                if player and hasattr(player, "refresh_security_ui"):
                    player.refresh_security_ui()
                return "🔓 Face verified! Master Security Lock is now DISABLED."

            # Face failed — need passcode via UI
            return (
                "⚠️ AUTHENTICATION REQUIRED\n"
                "Face verification failed. Please enter your passcode in the TITAN UI input box to disable the lock.\n"
                "Type: unlock <your passcode>"
            )

    return f"Unknown security action: {action}"


# ── UI PASSCODE COMMANDS (called from main.py text input, NOT from TITAN AI) ─
def handle_security_command(text: str) -> str | None:
    """
    Parse typed text commands from the UI input box.
    These commands are processed BEFORE reaching TITAN AI,
    so TITAN never sees the passcode.
    
    Commands:
        set pin XXXX       — Set owner passcode
        unlock XXXX        — Emergency unlock with passcode
        disable lock XXXX  — Disable locks with passcode verification
    """
    t = text.strip().lower()

    # SET PIN
    if t.startswith("set pin "):
        pin = text.strip()[8:].strip()
        if len(pin) < 4:
            return "PIN must be at least 4 characters."
        set_pin(pin)
        return "🔒 Owner passcode set!"

    # UNLOCK / EMERGENCY OVERRIDE
    if t.startswith("unlock ") or t.startswith("override "):
        pin = text.strip().split(" ", 1)[1].strip()
        if verify_pin(pin):
            cfg = get_security_config()
            cfg["voice_lock"]   = False
            cfg["face_lock"]    = False
            cfg["startup_gate"] = False
            save_security_config(cfg)
            return "🔓 Emergency unlock successful! All locks disabled."
        return "❌ Incorrect passcode."

    # DISABLE LOCK WITH PIN
    if t.startswith("disable lock "):
        pin = text.strip()[13:].strip()
        if verify_pin(pin):
            cfg = get_security_config()
            cfg["voice_lock"] = False
            cfg["face_lock"]  = False
            save_security_config(cfg)
            return "🔓 Locks disabled via passcode verification."
        return "❌ Incorrect passcode. Locks remain active."

    return None  # Not a security command

