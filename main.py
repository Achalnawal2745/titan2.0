import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import platform as _platform
import subprocess as _subprocess
import warnings
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false;qt.text.*=false;qt.qpa.window=false"
warnings.filterwarnings("ignore")

try:
    import colorama
    colorama.just_fix_windows_console()
except Exception:
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        hStdOut = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
        kernel32.SetConsoleMode(hStdOut, mode.value | 0x0004)
    except Exception:
        pass

# ── Nuclear: force CREATE_NO_WINDOW on EVERY subprocess call on Windows ───────
# This patches Popen itself, so no per-file flag is needed anywhere.
if _platform.system() == "Windows":
    _OrigPopen = _subprocess.Popen

    class _Popen(_OrigPopen):
        def __init__(self, args, **kw):
            kw["creationflags"] = kw.get("creationflags", 0) | _subprocess.CREATE_NO_WINDOW
            kw.pop("startupinfo", None)   # drop any stale/shared STARTUPINFO
            super().__init__(args, **kw)

    _subprocess.Popen = _Popen
# ─────────────────────────────────────────────────────────────────────────────

import asyncio
import re
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import platform as _platform
import subprocess as _subprocess
import warnings
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false;qt.text.*=false;qt.qpa.window=false"
warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    import colorama
    colorama.just_fix_windows_console()
except Exception:
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        hStdOut = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
        kernel32.SetConsoleMode(hStdOut, mode.value | 0x0004)
    except Exception:
        pass

# ── Nuclear: force CREATE_NO_WINDOW on EVERY subprocess call on Windows ───────
# This patches Popen itself, so no per-file flag is needed anywhere.
if _platform.system() == "Windows":
    _OrigPopen = _subprocess.Popen

    class _Popen(_OrigPopen):
        def __init__(self, args, **kw):
            kw["creationflags"] = kw.get("creationflags", 0) | _subprocess.CREATE_NO_WINDOW
            kw.pop("startupinfo", None)   # drop any stale/shared STARTUPINFO
            super().__init__(args, **kw)

    _subprocess.Popen = _Popen
# ─────────────────────────────────────────────────────────────────────────────

import asyncio
import re
import threading
import queue
import time
import json
import sys
import traceback
from collections import deque
from datetime import datetime
from pathlib import Path

import sounddevice as sd
from google import genai
from google.genai import types
from ui import TitanUI
from memory.memory_manager import (
    load_memory, update_memory, format_memory_for_prompt,
    save_session_summary, pop_last_session,
)

from actions.file_processor import file_processor
from actions.flight_finder     import flight_finder
from actions.open_app          import open_app
from actions.weather_report    import weather_action
from actions.send_message      import send_message
from actions.reminder          import reminder
from actions.computer_settings import computer_settings
from actions.screen_processor  import _capture_camera, _capture_screen
from actions.youtube_video     import youtube_video
from actions.desktop           import desktop_control
from actions.browser_control   import browser_control
from actions.file_controller   import file_controller
from actions.code_helper       import code_helper
from actions.dev_agent         import dev_agent
from actions.web_search        import web_search as web_search_action
from actions.computer_control  import computer_control
from actions.game_updater      import game_updater
from actions.shadow_link       import shadow_link_control
from actions.system_monitor    import SystemMonitor, get_system_status

from actions.proactive         import ProactiveEngine
from actions.background_monitor import (
    add_monitor, remove_monitor, list_monitors, check_all as monitor_check_all,
)
from actions.voice_face_id import (
    voice_face_id, verify_voice, startup_authenticate,
    handle_security_command, get_security_config as get_sec_config,
)
from actions.web_search        import _news as _fetch_news_sync
from memory.config_manager     import (
    get_brief_enabled,
    get_input_device, get_output_device,
    save_input_device, save_output_device,
)
from memory.work_pad           import (
    run_work_pad,
    format_for_prompt as format_pad_for_prompt,
    track_long_task,
    absorb_work_output,
    load_pad,
    _next_step,
)
from task_control import set_ui_hooks
from core.plugin_loader import discover_plugins
from core.skill_registry import discover_skills
from core.exec import run_command, RUN_COMMAND_DECLARATION
from core.agent_loop import main_agent_loop
from core.session_log import session_logger
from core.todo_engine import todo_engine, TODO_WRITE_DECLARATION, TODO_READ_DECLARATION
from core.goal_manager import goal_manager, GOAL_TOOLS_DECLARATIONS
from core.scheduler import scheduler, SCHEDULE_DECLARATION
from core.interaction import interaction_engine, ASK_USER_DECLARATION
from core.plan_mode import plan_mode, PLAN_MODE_DECLARATIONS
from core.jobs import job_registry, JOB_TOOLS_DECLARATIONS
from core.fs_tools import (
    read_file, write_file, str_replace_editor, grep_search, glob_search,
    FS_TOOLS_DECLARATIONS,
)
from core.code_runner import run_python_code, PYTHON_EVAL_DECLARATION
from core.web_tools import web_fetch, WEB_FETCH_DECLARATION
from core.nvidia_brain import run_brain_turn
from core.task_workers import task_workers, TASK_WORKER_DECLARATIONS, running_in_worker
import core.confirm as confirm
import core.audio_devices as audio_devices
from core.undo import undo_last, peek as undo_peek, push_undo, clear as undo_clear
# core.workflow_engine (WORKFLOW_DECLARATION/ralph_loop) and core.subagent_engine
# (SUBAGENT_TOOLS_DECLARATIONS) are intentionally NOT imported anymore. Both were
# earlier, half-built "do complex work" paths that ended up coexisting with
# core.task_workers — workflow_start was pure decoration (ralph_loop just
# returns a string, no actual execution ever happens), and invoke_subagent
# duplicated task_workers.start() under a different name. Having 3 different
# tool names that all mean "do multi-step work", with only some of them
# wired to real execution, is exactly what caused "works sometimes, does
# nothing other times" — the model was picking between them essentially at
# random. task_workers.py is the one real, verification-gated implementation;
# everything now points at it exclusively. See TASK_WORKER_DECLARATIONS below.


def _finalize(raw):
    if raw is None:
        return "⚠️ No result came back from the tool."
    return str(raw).strip() or "Done."


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


BASE_DIR        = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
PROMPT_PATH     = BASE_DIR / "core" / "prompt.txt"

# ── Full-Brain mode ─────────────────────────────────────────────────────
# When True: Gemini Live gets NO tools and NO planning system prompt — it's
# reduced to STT-in/TTS-out. Every user utterance is instead routed to
# core/nvidia_brain.run_brain_turn(), which calls NVIDIA NIM to plan and
# execute tool calls. Gemini only speaks the final text NVIDIA hands back.
# Flip to False (or set "full_brain_mode": false in config/api_keys.json)
# to go back to Gemini deciding + calling tools itself, same as before.
def _full_brain_enabled() -> bool:
    try:
        cfg = json.loads(API_CONFIG_PATH.read_text(encoding="utf-8"))
        return bool(cfg.get("full_brain_mode", False))
    except Exception:
        return False


_SILENT_RELAY_PROMPT = (
    "You are a text-to-speech relay, not an assistant. You have NO tools "
    "and must never claim to have done anything.\n"
    "Rules:\n"
    "1. You will receive messages starting with '[SPEAK_NOW]' — when you "
    "get one, speak that exact text aloud, in your own natural voice/pacing, "
    "without adding new facts, opinions, or offers.\n"
    "2. If you receive audio/speech from the user directly (not a "
    "[SPEAK_NOW] message), do NOT answer it yourself and do NOT guess an "
    "answer. Just stay silent / say a brief neutral filler like 'mm' at "
    "most — a separate planning system is handling the real answer and "
    "will send it to you shortly as [SPEAK_NOW].\n"
    "3. Never invent information. Never call a function. Never say a task "
    "is done unless it appeared inside a [SPEAK_NOW] message."
)
LIVE_MODELS = [
    "models/gemini-2.5-flash-native-audio-preview-12-2025",
    "models/gemini-3.1-flash-live-preview",
    "models/gemini-2.0-flash-live-001",
]
_live_model_idx = 0


def _get_live_model() -> str:
    global _live_model_idx
    return LIVE_MODELS[_live_model_idx % len(LIVE_MODELS)]


def _rotate_live_model() -> str:
    global _live_model_idx
    _live_model_idx += 1
    m = LIVE_MODELS[_live_model_idx % len(LIVE_MODELS)]
    print(f"[TITAN] 🔄 Switching to model: {m}")
    return m


CHANNELS            = 1
SEND_SAMPLE_RATE    = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE          = 512     # 32 ms @ 16 kHz  (was 1024 = 64 ms)

# ── Debug toggle: set True to see VAD / first-audio timings ──
_DEBUG_AUDIO = False          # was True — per-chunk prints stall the event loop
_dbg_chunk_count = 0

# Local VAD — stream speech only, then tell Gemini "user stopped"
# Real speech in your logs is RMS 800–1900. Titan speaker leak is 3000+.
# 18-chunk (~0.6s) end-silence was cutting you mid-sentence → "say that again".
_VAD_START_RMS      = 640.0
_VAD_HOLD_RMS       = 360.0
_VAD_PREROLL        = 8       # ~256 ms before speech start
_VAD_END_SILENCE    = 42      # ~1.34 s quiet → end of turn
_VAD_MIN_SPEECH     = 14      # need ~450 ms of real speech before we may end
_SEND_QUEUE_MAX     = 16
_ECHO_TAIL_S        = 1.25    # swallow speaker tail after Titan stops
_VAD_SUPPRESS_S     = 1.40    # after ESC / interrupt, ignore mic this long
_END_DEBOUNCE_S     = 1.40    # don't send audio_stream_end twice in a row
_AUDIO_MIME         = "audio/pcm;rate=16000"
# Talk-while-working: higher than keyboard/fan, lower than a real sentence.
_VAD_BUSY_START_RMS = 880.0
_VAD_BUSY_HOLD_RMS  = 420.0
_VAD_BUSY_MIN_SPEECH = 16     # ~0.5 s so a click does not cancel the job
_WORK_TOOLS = {
    "file_controller", "run_command", "load_skill", "code_helper",
    "file_processor", "work_pad", "dev_agent", "web_search",
}

# ── Boss / worker power split ────────────────────────────────────────────────
# The BOSS (Gemini Live) owns the voice: listen, triage, speak, and steer
# workers. It keeps every fast one-shot action - "open Chrome", "who is X",
# "what's my CPU at" must stay instant, and routing those through a worker
# would add an NVIDIA round-trip plus worker spawn to a 200 ms task.
#
# The WORKER (core/task_workers.py, NVIDIA brain) owns everything that builds
# something: writing files, running commands, loading skill instructions,
# planning, verifying. It has strictly MORE power than the boss - the only
# thing it cannot do is speak.
#
# This split is the enforcement mechanism, not a suggestion. Previously
# prompt.txt merely asked the boss to hand off complex work, so whenever the
# boss felt capable it would call write_file + run_command itself, skip the
# skill entirely, and emit a bare default-template deck. Removing those tools
# from the boss makes handoff the only physically available path.
WORKER_ONLY_TOOLS = {
    # instruction loading - the boss cannot act on skills, so it must not hold
    # them (and the old deferred-load path bound the skill to the WRONG
    # transcript, starting workers with tasks like the single word "no")
    "load_skill",
    # authoring / execution
    "write_file", "str_replace_editor", "run_command", "python_eval",
    "code_helper", "dev_agent", "file_processor", "file_controller",
    "game_updater",
    # planning + completion gating (already worker-scoped, listed for clarity)
    "task_set_plan", "verify_task_result",
    "enter_plan_mode", "exit_plan_mode", "set_goal", "complete_goal",
}

def _dbg(tag: str, msg: str):
    if _DEBUG_AUDIO:
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{ts}] [{tag}] {msg}")

def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def get_live_clock() -> str:
    """True local wall clock from this PC — not the frozen session-start time."""
    now = datetime.now().astimezone()
    off = now.strftime("%z")
    off_h = f"{off[:3]}:{off[3:]}" if off else ""
    tz = now.tzname() or "local"
    return (
        f"LIVE PC CLOCK (do not guess — this is the real time right now)\n"
        f"Date: {now.strftime('%A, %B %d, %Y')}\n"
        f"Time: {now.strftime('%I:%M:%S %p')}  ({now.strftime('%H:%M:%S')})\n"
        f"Timezone: {tz} (UTC{off_h})\n"
        f"ISO: {now.isoformat(timespec='seconds')}"
    )


def _load_system_prompt() -> str:
    prompt_text = ""
    try:
        prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        prompt_text = (
            "You are TITAN, an advanced AI assistant. "
            "Be concise, direct, and always use the provided tools to complete tasks. "
            "Never simulate or guess results — always call the appropriate tool."
        )
    try:
        from actions.file_controller import _windows_shell_folder
        desk_p = _windows_shell_folder("Desktop") or (Path.home() / "Desktop")
        down_p = _windows_shell_folder("Downloads") or (Path.home() / "Downloads")
        docs_p = _windows_shell_folder("Documents") or (Path.home() / "Documents")
        prompt_text += (
            f"\n\nUSER DIRECTORIES (ALWAYS use these exact paths when saving or finding files):\n"
            f"- Desktop: {str(desk_p).replace(chr(92), '/')}\n"
            f"- Downloads: {str(down_p).replace(chr(92), '/')}\n"
            f"- Documents: {str(docs_p).replace(chr(92), '/')}\n"
            f"Never invent paths like 'E:/auto/shadowos/Desktop' — the real Desktop is at {str(desk_p).replace(chr(92), '/')}.\n"
        )
    except Exception:
        pass

    try:
        pad_txt = format_pad_for_prompt()
        if pad_txt:
            prompt_text += "\n\n" + pad_txt
    except Exception:
        pass

    try:
        job_txt = format_job_for_prompt()
        if job_txt:
            prompt_text += "\n\n" + job_txt
    except Exception:
        pass

    prompt_text += (
        "\n\nTASK CHECKLIST PROTOCOL: Use `todo_write` as your dynamic checklist to plan and track multi-step tasks. "
        "When starting a complex task (documents, presentations, multi-step code), call `todo_write` (action='set_plan', title='...', steps=['step 1', 'step 2', ...]) "
        "to break down what needs to be done. As you finish each step, call `todo_write` (action='update_step', step_id=N, status='completed') "
        "so the live checklist on the Workpad is always updated for sir.\n"
    )

    prompt_text += (
        "\n\nCLOCK RULE: The date/time printed at session start goes STALE. "
        "Whenever the user asks the time, date, today, tomorrow, or you need the time for a reminder, "
        "you MUST call get_clock first and speak THAT result. Never invent or remember the time.\n"
    )

    prompt_text += (
        "\n\nREASONING RULE: You respond fast and directly for normal conversation and tool calls — "
        "do not overthink simple requests. But if the user asks for something that genuinely needs "
        "multi-step planning, comparison, or reasoning through constraints (e.g. scheduling, strategy, "
        "complex decisions, multi-part math), call the deep_think tool instead of answering off the cuff. "
        "Briefly tell the user you're thinking it through first, then call deep_think and speak its result "
        "naturally in your own voice — don't read it robotically."
    )

    prompt_text += (
        "\n\nMID-TASK TALK: If sir talks while a tool is running, the job STOPS and does not save. "
        "You will then hear what he said. Follow THAT. "
        "stop / wait / don't touch → do not call the same tool again. "
        "A specific change ('don't touch the cover', 'change the title') → only that change. "
        "Do not restart the old job unless he says continue.\n"
        "DOC QUALITY: Professional/academic reports = Times New Roman 12pt 1.5 ON THE TEMPLATE "
        "(via the docx skill). NEVER a generic navy/Segoe AI report. After write, verify formatting and fonts.\n"
        "STEP-BY-STEP WORKFLOW:\n"
        "For any complex, creative, or multi-step request (documents, presentations, analysis, coding):\n"
        "1. First Plan on Workpad: Call `todo_write` (action='set_plan', title='...', steps=[...]) to break down the task.\n"
        "2. Execute Step-by-Step: Systematically execute each step using your real tools (load_skill, run_command, file_controller).\n"
        "3. Mark Progress: Update step statuses via `todo_write` (action='update_step', step_id=N, status='completed').\n"
        "4. Verify & Deliver: Confirm that the output is ready before reporting to sir.\n"
    )

    prompt_text += (
        "\n\nCOMPLETION HONESTY — THIS IS A HARD RULE, NOT A STYLE PREFERENCE:\n"
        "Never say a file/task is done, saved, updated, ready, improved, or 'तैयार है' / 'बना दिया है' "
        "unless a tool call (run_command, file_controller, etc.) actually ran and SUCCEEDED in "
        "*this same turn or the immediately preceding one*. Saying it's done without that is a lie to sir, "
        "not politeness — never do it, even if he sounds impatient or angry.\n"
        "If work is not actually finished yet: say plainly that you are calling the tool now, then CALL IT — "
        "in the same turn. Do not respond with only reassurance ('थोड़ा समय लगेगा', 'प्रक्रिया चल रही है', "
        "'कर रहा हूँ') with no tool call behind it. A turn with no tool call and no new information is a "
        "wasted turn sir can hear — if you are not ready to speak the real answer, you are ready to call a tool.\n"
        "If sir asks 'did you actually do something' / 'kuch kiya kya' / 'दिख नहीं रहा': answer honestly from "
        "the ACTUAL last tool result, not from what you said earlier. If the last real attempt failed or you "
        "never called the tool, say so directly ('माफ़ कीजिए sir, अभी तक नहीं बना — अभी बनाता हूँ') and then "
        "immediately call the tool — don't apologize in words only and stall again.\n"
        "Every one of your spoken turns about an in-progress file job must either (a) contain a tool call, or "
        "(b) report the exit_code/result of a tool call that just ran. Never a bare reassurance sentence with "
        "neither.\n"
    )

    return prompt_text

_CTRL_RE = re.compile(r"<ctrl\d+>", re.IGNORECASE)

def _looks_tool_error(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    head = t[:90].lower()
    return (
        t.startswith("❌")
        or head.startswith("error")
        or " failed" in head
        or "traceback" in t.lower()
        or "unexpected" in head
        or "got an unexpected" in t.lower()
    )

def _clean_transcript(text: str) -> str:    
    text = _CTRL_RE.sub("", text)
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)
    return text.strip()

TOOL_DECLARATIONS = [
    {
        "name": "ui_automation",
        "description": (
            "Interacts with Windows desktop apps programmatically via Windows Accessibility UIA tree "
            "WITHOUT moving or stealing the user's physical mouse. "
            "Actions: 'click' (click button/element), 'type' (paste text into input box), "
            "'get_text' (read text from element), 'dump_tree' (inspect UI accessibility tree)."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "click | type | get_text | dump_tree"},
                "app_name": {"type": "STRING", "description": "Target application name (e.g. 'Calculator', 'Notepad', 'Chrome')"},
                "element_name": {"type": "STRING", "description": "Title or button label to interact with (e.g. 'Seven', 'Edit', 'Submit')"},
                "text": {"type": "STRING", "description": "Text to type into an edit box or search query for dump_tree"},
                "index": {"type": "INTEGER", "description": "Index if multiple elements match the same name (default 0)"}
            },
            "required": ["action", "app_name"]
        }
    },
    {
        "name": "open_app",
        "description": (
            "Opens any application on the computer. "
            "Use this whenever the user asks to open, launch, or start any app, "
            "website, or program. Always call this tool — never just say you opened it."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {
                    "type": "STRING",
                    "description": "Exact name of the application (e.g. 'WhatsApp', 'Chrome', 'Spotify')"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "web_search",
        "description": (
            "Searches the web. Use for ANY question about current facts, events, prices, "
            "or topics — always prefer this over guessing. "
            "Modes: 'search' (default), 'news' (latest headlines on a topic), "
            "'research' (deep comprehensive answer), 'price' (product cost lookup), "
            "'compare' (side-by-side comparison of items)."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query":  {"type": "STRING", "description": "Search query or topic"},
                "mode":   {"type": "STRING", "description": "search | news | research | price | compare"},
                "items":  {"type": "ARRAY",  "items": {"type": "STRING"}, "description": "Items to compare (compare mode)"},
                "aspect": {"type": "STRING", "description": "Comparison aspect: price | specs | reviews | features"},
            },
            "required": ["query"]
        }
    },
    {
        "name": "system_status",
        "description": (
            "Returns real-time system metrics: CPU usage, RAM, GPU load, CPU temperature, "
            "uptime, and process count. Use when the user asks about computer performance, "
            "temperature, memory, or resource usage."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {},
        }
    },
    {
        "name": "set_titan_microphone",
        "description": "Mutes or unmutes TITAN's own microphone. Call this when the user says 'mute yourself', 'stop listening', 'unmute yourself', or 'start listening'. This controls TITAN only, not the Windows system volume.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "muted": {"type": "BOOLEAN", "description": "True to stop TITAN listening; false to resume listening."}
            },
            "required": ["muted"]
        }
    },
    {
        "name": "undo_last_action",
        "description": (
            "Reverses the most recent reversible action TITAN performed (a setting change, "
            "a mic mute, etc). Call this the instant the user says 'undo', 'undo that', 'put "
            "it back', or 'go back'. Runs immediately — never ask for confirmation first."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "peek_only": {
                    "type": "BOOLEAN",
                    "description": "True to just report what WOULD be undone, without doing it (e.g. user asks 'what can you undo').",
                }
            },
        }
    },
    {
        "name": "set_titan_audio_device",
        "description": (
            "Lists or switches which microphone or speakers TITAN uses. Call with action='list' "
            "when the user asks what microphones/speakers are available, or action='set' with "
            "kind and device_name to switch TITAN to a specific device. The change applies the "
            "next time TITAN reconnects (usually within a few seconds)."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "'list' or 'set'"},
                "kind": {"type": "STRING", "description": "'input' (microphone) or 'output' (speakers)"},
                "device_name": {"type": "STRING", "description": "Exact device name from the list — required for action='set'."},
            },
            "required": ["action"]
        }
    },

    {
        "name": "get_clock",
        "description": (
            "Returns this PC's LIVE local date, time, weekday and timezone RIGHT NOW. "
            "MUST be called for any time/date question or when computing reminder times. "
            "Never guess the time from memory or from the session-start clock."
        ),
        "parameters": {"type": "OBJECT", "properties": {}, "required": []}
    },
    TODO_WRITE_DECLARATION,
    TODO_READ_DECLARATION,
    SCHEDULE_DECLARATION,
    *GOAL_TOOLS_DECLARATIONS,
    ASK_USER_DECLARATION,
    *PLAN_MODE_DECLARATIONS,
    *JOB_TOOLS_DECLARATIONS,
    *TASK_WORKER_DECLARATIONS,
    *FS_TOOLS_DECLARATIONS,
    PYTHON_EVAL_DECLARATION,
    WEB_FETCH_DECLARATION,
    {
        "name": "weather_report",
        "description": "Gives the weather report to user",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING", "description": "City name"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "send_message",
        "description": "Sends a text message via WhatsApp, Telegram, or other messaging platform.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "receiver":     {"type": "STRING", "description": "Recipient contact name"},
                "message_text": {"type": "STRING", "description": "The message to send"},
                "platform":     {"type": "STRING", "description": "Platform: WhatsApp, Telegram, etc."}
            },
            "required": ["receiver", "message_text", "platform"]
        }
    },
    {
        "name": "reminder",
        "description": "Sets a timed reminder using Task Scheduler.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "date":    {"type": "STRING", "description": "Date in YYYY-MM-DD format"},
                "time":    {"type": "STRING", "description": "Time in HH:MM format (24h)"},
                "message": {"type": "STRING", "description": "Reminder message text"}
            },
            "required": ["date", "time", "message"]
        }
    },
    {
        "name": "youtube_video",
        "description": (
            "Controls YouTube. Use for: playing videos, summarizing a video's content, "
            "getting video info, or showing trending videos."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "play | summarize | get_info | trending (default: play)"},
                "query":  {"type": "STRING", "description": "Search query for play action"},
                "save":   {"type": "BOOLEAN", "description": "Save summary to Notepad (summarize only)"},
                "region": {"type": "STRING", "description": "Country code for trending e.g. TR, US"},
                "url":    {"type": "STRING", "description": "Video URL for get_info action"},
            },
            "required": []
        }
    },
    {
        "name": "screen_process",
        "description": (
            "Captures the screen or webcam image and lets you analyze it. "
            "MUST be called when user asks what is on screen, what you see, "
            "look at camera, analyze my screen, etc. "
            "You have NO visual ability without this tool. "
            "After the image is captured it is sent directly to you — describe what you see and answer the user's question. "
            "When using camera: the live view stays open until user says close it or calls close_camera."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "angle": {"type": "STRING", "description": "'screen' to capture display, 'camera' for webcam. Default: 'screen'"},
                "text":  {"type": "STRING", "description": "The question or instruction about the captured image"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "close_camera",
        "description": (
            "Closes the live camera view shown on screen. "
            "Call when user says: close camera, stop camera, turn off camera, "
            "kamerayı kapat, kapat, creepy, etc."
        ),
        "parameters": {"type": "OBJECT", "properties": {}, "required": []}
    },
    {
        "name": "computer_settings",
        "description": (
            "Controls the computer: volume, brightness, window management, keyboard shortcuts, "
            "typing text on screen, closing apps, fullscreen, dark mode, WiFi, restart, shutdown, "
            "scrolling, tab management, zoom, screenshots, lock screen, refresh/reload page. "
            "Use for ANY single computer control command."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "The action to perform"},
                "description": {"type": "STRING", "description": "Natural language description of what to do"},
                "value":       {"type": "STRING", "description": "Optional value: volume level, text to type, etc."}
            },
            "required": []
        }
    },
    {
        "name": "browser_control",
        "description": (
            "Controls any web browser. Use for: opening websites, searching the web, "
            "clicking elements, filling forms, scrolling, screenshots, navigation, any web-based task. "
            "Simple open/search requests launch the user's own browser normally (their real profile "
            "and logged-in accounts); interactive actions (click, type, fill_form...) attach an "
            "automation browser. "
            "Always pass the 'browser' parameter when the user specifies a browser (e.g. 'open in Edge', "
            "'use Firefox', 'open Chrome'). Multiple browsers can run simultaneously."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "go_to | search | click | type | scroll | fill_form | smart_click | smart_type | get_text | get_url | press | new_tab | close_tab | screenshot | back | forward | reload | switch | list_browsers | close | close_all"},
                "browser":     {"type": "STRING", "description": "Target browser: chrome | edge | firefox | opera | operagx | brave | vivaldi | safari. Omit to use the currently active browser."},
                "url":         {"type": "STRING", "description": "URL for go_to / new_tab action"},
                "query":       {"type": "STRING", "description": "Search query for search action"},
                "engine":      {"type": "STRING", "description": "Search engine: google | bing | duckduckgo | yandex (default: google)"},
                "selector":    {"type": "STRING", "description": "CSS selector for click/type"},
                "text":        {"type": "STRING", "description": "Text to click or type"},
                "description": {"type": "STRING", "description": "Element description for smart_click/smart_type"},
                "direction":   {"type": "STRING", "description": "up | down for scroll"},
                "amount":      {"type": "INTEGER", "description": "Scroll amount in pixels (default: 500)"},
                "key":         {"type": "STRING", "description": "Key name for press action (e.g. Enter, Escape, F5)"},
                "path":        {"type": "STRING", "description": "Save path for screenshot"},
                "incognito":   {"type": "BOOLEAN", "description": "Open in private/incognito mode"},
                "clear_first": {"type": "BOOLEAN", "description": "Clear field before typing (default: true)"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "file_controller",
        "description": "Manages files and folders: list, create, delete, move, copy, rename, read, write, find, disk usage.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "list | create_file | create_folder | delete | move | copy | rename | read | write | find | largest | disk_usage | organize_desktop | info"},
                "path":        {"type": "STRING", "description": "File/folder path or shortcut: desktop, downloads, documents, home"},
                "destination": {"type": "STRING", "description": "Destination path for move/copy"},
                "new_name":    {"type": "STRING", "description": "New name for rename"},
                "content":     {"type": "STRING", "description": "Content for create_file/write"},
                "name":        {"type": "STRING", "description": "File name to search for"},
                "extension":   {"type": "STRING", "description": "File extension to search (e.g. .pdf)"},
                "count":       {"type": "INTEGER", "description": "Number of results for largest"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "desktop_control",
        "description": "Controls the desktop: wallpaper, organize, clean, list, stats.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "wallpaper | wallpaper_url | organize | clean | list | stats | task"},
                "path":   {"type": "STRING", "description": "Image path for wallpaper"},
                "url":    {"type": "STRING", "description": "Image URL for wallpaper_url"},
                "mode":   {"type": "STRING", "description": "by_type or by_date for organize"},
                "task":   {"type": "STRING", "description": "Natural language desktop task"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "code_helper",
        "description": "Writes, edits, explains, runs, or builds code files.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "write | edit | explain | run | build | auto (default: auto)"},
                "description": {"type": "STRING", "description": "What the code should do or what change to make"},
                "language":    {"type": "STRING", "description": "Programming language (default: python)"},
                "output_path": {"type": "STRING", "description": "Where to save the file"},
                "file_path":   {"type": "STRING", "description": "Path to existing file for edit/explain/run/build"},
                "code":        {"type": "STRING", "description": "Raw code string for explain"},
                "args":        {"type": "STRING", "description": "CLI arguments for run/build"},
                "timeout":     {"type": "INTEGER", "description": "Execution timeout in seconds (default: 30)"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "dev_agent",
        "description": "Builds complete multi-file projects from scratch: plans, writes files, installs deps, opens VSCode, runs and fixes errors.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "description":  {"type": "STRING", "description": "What the project should do"},
                "language":     {"type": "STRING", "description": "Programming language (default: python)"},
                "project_name": {"type": "STRING", "description": "Optional project folder name"},
                "timeout":      {"type": "INTEGER", "description": "Run timeout in seconds (default: 30)"},
            },
            "required": ["description"]
        }
    },
    {
        "name": "computer_control",
        "description": "FALLBACK raw mouse/keyboard control. ALWAYS USE 'ui_automation' FIRST for clicking or typing in desktop apps (Notepad, Calculator, Word) so the mouse is NOT hijacked. Use computer_control ONLY for global hotkeys, scrolling, or raw fallback mouse movement.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "type | smart_type | click | double_click | right_click | hotkey | press | scroll | move | copy | paste | screenshot | wait | clear_field | focus_window | screen_find | screen_click | random_data | user_data"},
                "text":        {"type": "STRING", "description": "Text to type or paste"},
                "x":           {"type": "INTEGER", "description": "X coordinate"},
                "y":           {"type": "INTEGER", "description": "Y coordinate"},
                "keys":        {"type": "STRING", "description": "Key combination e.g. 'ctrl+c'"},
                "key":         {"type": "STRING", "description": "Single key e.g. 'enter'"},
                "direction":   {"type": "STRING", "description": "up | down | left | right"},
                "amount":      {"type": "INTEGER", "description": "Scroll amount (default: 3)"},
                "seconds":     {"type": "NUMBER",  "description": "Seconds to wait"},
                "title":       {"type": "STRING",  "description": "Window title for focus_window"},
                "description": {"type": "STRING",  "description": "Element description for screen_find/screen_click"},
                "type":        {"type": "STRING",  "description": "Data type for random_data"},
                "field":       {"type": "STRING",  "description": "Field for user_data: name|email|city"},
                "clear_first": {"type": "BOOLEAN", "description": "Clear field before typing (default: true)"},
                "path":        {"type": "STRING",  "description": "Save path for screenshot"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "shadow_link",
        "description": (
            "Controls the user's REAL open Chrome browser tab via the Shadow-Link extension bridge. "
            "Use for: getting current Chrome tab URL, navigating open Chrome tab, clicking web elements, "
            "typing text into Chrome inputs, scrolling, and extracting page content."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":   {"type": "STRING", "description": "get_url | navigate | click | type | scroll | extract"},
                "url":      {"type": "STRING", "description": "Target URL for navigate"},
                "text":     {"type": "STRING", "description": "Text to type into input or search"},
                "selector": {"type": "STRING", "description": "CSS selector for click"}
            },
            "required": []
        }
    },
    {
        "name": "game_updater",
        "description": (
            "THE ONLY tool for ANY Steam or Epic Games request. "
            "Use for: installing, downloading, updating games, listing installed games, "
            "checking download status, scheduling updates. "
            "ALWAYS call directly for any Steam/Epic/game request. "
            "NEVER use browser_control or web_search for Steam/Epic."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":    {"type": "STRING",  "description": "update | install | list | download_status | schedule | cancel_schedule | schedule_status (default: update)"},
                "platform":  {"type": "STRING",  "description": "steam | epic | both (default: both)"},
                "game_name": {"type": "STRING",  "description": "Game name (partial match supported)"},
                "app_id":    {"type": "STRING",  "description": "Steam AppID for install (optional)"},
                "hour":      {"type": "INTEGER", "description": "Hour for scheduled update 0-23 (default: 3)"},
                "minute":    {"type": "INTEGER", "description": "Minute for scheduled update 0-59 (default: 0)"},
                "shutdown_when_done": {"type": "BOOLEAN", "description": "Shut down PC when download finishes"},
            },
            "required": []
        }
    },
    {
        "name": "flight_finder",
        "description": "Searches Google Flights and speaks the best options.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "origin":      {"type": "STRING",  "description": "Departure city or airport code"},
                "destination": {"type": "STRING",  "description": "Arrival city or airport code"},
                "date":        {"type": "STRING",  "description": "Departure date (any format)"},
                "return_date": {"type": "STRING",  "description": "Return date for round trips"},
                "passengers":  {"type": "INTEGER", "description": "Number of passengers (default: 1)"},
                "cabin":       {"type": "STRING",  "description": "economy | premium | business | first"},
                "save":        {"type": "BOOLEAN", "description": "Save results to Notepad"},
            },
            "required": ["origin", "destination", "date"]
        }
    },
    {
        "name": "manage_monitor",
        "description": (
            "Add, remove, or list background monitoring topics. "
            "TITAN checks these topics once a day and alerts the user when there is a new development. "
            "Use 'add' when the user says 'monitor X', 'track X', 'follow X'. "
            "Use 'remove' when the user says 'stop monitoring X'. "
            "Use 'list' when the user asks what is being monitored. "
            "Do NOT add crypto, financial, or trading topics."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type":        "STRING",
                    "description": "add | remove | list",
                },
                "topic": {
                    "type":        "STRING",
                    "description": "Topic to monitor or stop monitoring (e.g. 'space exploration', 'AI news')",
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "voice_face_id",
        "description": (
            "Voice ID and Face ID Security System. "
            "Use action='enroll_face' to capture webcam and register owner face. "
            "Use action='enroll_voice' to record 3s of mic and register owner voice. "
            "Use action='status' to check security status. "
            "Use action='toggle' with enable=True to turn ON locks (voice/face/gate). "
            "Use action='toggle' with enable=False to turn OFF locks (requires face verification). "
            "You do NOT know the passcode. Never make up rules about passcode format. "
            "For passcode setup, tell user to type 'set pin XXXX' in the UI input box."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "enroll_face | enroll_voice | status | toggle"
                },
                "mode": {
                    "type": "STRING",
                    "description": "voice | face | gate | both (for toggle action)"
                },
                "enable": {
                    "type": "BOOLEAN",
                    "description": "True to turn ON lock, False to turn OFF lock (requires face auth)"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "shutdown_titan",
        "description": (
            "Shuts down the assistant completely. "
            "Call this when the user expresses intent to end the conversation, "
            "close the assistant, say goodbye, or stop Titan. "
            "The user can say this in ANY language."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {},
        }
    },
    {
    "name": "file_processor",
    "description": (
        "Processes any file that the user has uploaded or dropped onto the interface. "
        "Use this when the user refers to an uploaded file and wants an action on it. "
        "Supports: images (describe/ocr/resize/compress/convert), "
        "PDFs (summarize/extract_text/to_word), "
        "Word docs & text files (summarize/fix/reformat/translate), "
        "CSV/Excel (analyze/stats/filter/sort/convert), "
        "JSON/XML (validate/format/analyze), "
        "code files (explain/review/fix/optimize/run/document/test), "
        "audio (transcribe/trim/convert/info), "
        "video (trim/extract_audio/extract_frame/compress/transcribe/info), "
        "archives (list/extract), "
        "presentations (summarize/extract_text). "
        "ALWAYS call this tool when a file has been uploaded and the user gives a command about it. "
        "If the user's command is ambiguous, pick the most logical action for that file type."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "file_path": {
                "type": "STRING",
                "description": "Full path to the uploaded file. Leave empty to use the currently uploaded file."
            },
            "action": {
                "type": "STRING",
                "description": (
                    "What to do with the file. Examples by type:\n"
                    "image: describe | ocr | resize | compress | convert | info\n"
                    "pdf: summarize | extract_text | to_word | info\n"
                    "docx/txt: summarize | fix | reformat | translate_hint | word_count | to_bullet\n"
                    "csv/excel: analyze | stats | filter | sort | convert | info\n"
                    "json: validate | format | analyze | to_csv\n"
                    "code: explain | review | fix | optimize | run | document | test\n"
                    "audio: transcribe | trim | convert | info\n"
                    "video: trim | extract_audio | extract_frame | compress | transcribe | info | convert\n"
                    "archive: list | extract\n"
                    "pptx: summarize | extract_text | analyze"
                )
            },
            "instruction": {
                "type": "STRING",
                "description": "Free-form instruction if action doesn't cover it. E.g. 'translate this to Turkish', 'find all email addresses'"
            },
            "format": {
                "type": "STRING",
                "description": "Target format for conversion. E.g. 'mp3', 'pdf', 'csv', 'png'"
            },
            "width":     {"type": "INTEGER", "description": "Target width for image resize"},
            "height":    {"type": "INTEGER", "description": "Target height for image resize"},
            "scale":     {"type": "NUMBER",  "description": "Scale factor for image resize (e.g. 0.5)"},
            "quality":   {"type": "INTEGER", "description": "Quality 1-100 for image/video compress"},
            "start":     {"type": "STRING",  "description": "Start time for trim: seconds or HH:MM:SS"},
            "end":       {"type": "STRING",  "description": "End time for trim: seconds or HH:MM:SS"},
            "timestamp": {"type": "STRING",  "description": "Timestamp for video frame extraction HH:MM:SS"},
            "column":    {"type": "STRING",  "description": "Column name for CSV filter/sort"},
            "value":     {"type": "STRING",  "description": "Filter value for CSV filter"},
            "condition": {"type": "STRING",  "description": "Filter condition: equals|contains|gt|lt"},
            "ascending": {"type": "BOOLEAN", "description": "Sort order for CSV sort (default: true)"},
            "save":      {"type": "BOOLEAN", "description": "Save result to file (default: true)"},
            "destination": {"type": "STRING", "description": "Output folder for archive extract"},
        },
        "required": []
    }
},
    {
        "name": "deep_think",
        "description": (
            "Use ONLY when you need to reason/plan through something yourself before answering out loud — "
            "e.g. 'plan my exam schedule for the next 2 weeks', 'work out the best strategy considering X and Y', "
            "complex math, or multi-constraint decisions. This does NOT execute any tools, write files, or run "
            "commands — it only thinks and hands you back text to speak. If the task actually needs real work "
            "done (files created, commands run, multi-step execution) use start_task_worker instead, not this. "
            "Do NOT use for simple facts, small talk, or anything you can already answer directly. "
            "Tell the user briefly that you're thinking it through before calling this."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "task": {
                    "type": "STRING",
                    "description": "The full question or planning task to reason through, with all relevant context/constraints included."
                }
            },
            "required": ["task"]
        }
    },
    {
        "name": "save_memory",
        "description": (
            "Save an important personal fact about the user to long-term memory. "
            "Call this silently whenever the user reveals something worth remembering: "
            "name, age, city, job, preferences, hobbies, relationships, projects, or future plans. "
            "Do NOT call for: weather, reminders, searches, or one-time commands. "
            "Do NOT announce that you are saving — just call it silently. "
            "Values must be in English regardless of the conversation language."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category": {
                    "type": "STRING",
                    "description": (
                        "identity — name, age, birthday, city, job, language, nationality | "
                        "preferences — favorite food/color/music/film/game/sport, hobbies | "
                        "projects — active projects, goals, things being built | "
                        "relationships — friends, family, partner, colleagues | "
                        "wishes — future plans, things to buy, travel dreams | "
                        "notes — habits, schedule, anything else worth remembering"
                    )
                },
                "key":   {"type": "STRING", "description": "Short snake_case key (e.g. name, favorite_food, sister_name)"},
                "value": {"type": "STRING", "description": "Concise value in English (e.g. Achal, pizza, older sister)"},
            },
            "required": ["category", "key", "value"]
        }
    },
    RUN_COMMAND_DECLARATION,
]

# --- Plugin system ---


class TitanLive:

    def __init__(self, ui: TitanUI):
        self.ui             = ui
        self._asst_name     = "TITAN"   # updated each session from config
        self.session              = None
        self.audio_in_queue       = None
        self.out_queue            = None
        self._loop                = None
        self._is_speaking         = False
        self._speaking_lock       = threading.Lock()
        self._phone_active        = False   # True while phone mic is streaming; pauses PC mic
        self._pending_vision       = None    # (img_bytes, mime_type, question, angle) to inject after tool response
        self._vision_cam_active    = False   # True if camera was opened for vision → auto-close after response
        self._vision_close_pending = False   # True after vision injected; next turn_complete closes camera
        self._vision_last_time     = 0.0     # monotonic time of last screen_process call (cooldown guard)
        self._vision_busy          = False   # True while a vision capture/inject cycle is in flight
        self._interrupted          = False   # True while draining audio after user interrupt
        self.ui.on_text_command   = self._on_text_command
        self.ui.on_remote_clicked = self._make_remote_key
        self.ui.on_interrupt      = self.interrupt
        try:
            set_ui_hooks(
                log=lambda m: self.ui.write_log(m if str(m).startswith("SYS:") else f"SYS: {m}"),
                status=lambda title, body: self.ui.show_content(title, body),
            )
        except Exception:
            pass
        self._turn_done_event: asyncio.Event | None = None
        self._dashboard     = None
        self._briefing_sent    = False          # morning briefing fires once per process
        self._enhanced_live    = True           # affective dialog + proactive audio
        self._sys_monitor      = SystemMonitor()  # persistent cooldown state
        self._proactive        = ProactiveEngine()
        self._last_user_speech = time.monotonic()  # updated on every user utterance
        self._session_log: list[str] = []          # conversation turns for end-of-session summary
        self._tool_busy          = False
        self._tool_lock          = None          # asyncio.Lock, created in run()
        self._busy_vad           = {"in_speech": False, "silence": 0, "voiced": 0}
        self._midtask_pcm        = bytearray()
        self._pending_midtask    = b""
        self._speak_ended_at     = 0.0
        self._vad_end_t          = 0.0           # for ⚡ first-audio timing
        self._first_audio_logged = False
        self._play_stream        = None
        self._drop_model_audio   = False         # ESC / interrupt: discard incoming audio
        self._vad_suppress_until = 0.0
        self._last_stream_end    = 0.0
        self._speak_started_at   = 0.0           # when Titan started playing this utterance
        self._action_ledger: list[dict] = []
        self._full_brain          = True   # actual value set per-connect in _build_config()
        self._nvidia_history: list[dict] = []   # OpenAI-format running history for full-brain mode
        self._last_user_request = ""
        self._last_user_request_at = 0.0
        self._pending_live_skill = ""
        # A Gemini Live turn must not keep executing after it hands a complex
        # job to the durable worker.  It will receive the worker-start result
        # and can acknowledge it, but the worker owns the actual task.
        self._live_turn_delegated = False
        self._all_tool_declarations: list[dict] = []   # Gemini-format decls, reused for NVIDIA schema
        self._brain_lock: asyncio.Lock | None = None   # serializes full-brain turns, created on the running loop
        self._mute_brain_filler   = False   # True while suppressing playback of Gemini's own filler reply in full-brain mode
        self._expect_brain_turn_complete = False   # True from the moment we inject [SPEAK_NOW] until its turn_complete arrives
        try:
            self.plugin_registry = discover_plugins(
                BASE_DIR / "plugins",
                core_tool_names={t["name"] for t in TOOL_DECLARATIONS},
                logger=lambda m: self.ui.write_log(f"SYS: {m}"),
            )
        except Exception as e:
            print(f"[Plugins] init error: {e}")
            self.plugin_registry = None

        try:
            self.skill_registry = discover_skills(
                [BASE_DIR / "skills"],
                logger=lambda m: self.ui.write_log(f"SYS: {m}"),
            )
        except Exception as e:
            print(f"[Skills] init error: {e}")
            self.skill_registry = None

    def _log_action(self, name: str, args: dict) -> None:
        self._action_ledger.append({
            "tool": name,
            "args": {k: v for k, v in (args or {}).items() if k not in ("python_code", "code", "image_bytes")},
            "time": datetime.now().strftime("%H:%M:%S"),
        })
        self._action_ledger[:] = self._action_ledger[-30:]

    def _make_remote_key(self):
        """Called from Qt main thread when user presses Remote Control."""
        if self._dashboard is None:
            self.ui.write_log(
                "SYS: Dashboard unavailable. "
                "Run: pip install fastapi \"uvicorn[standard]\" cryptography"
            )
            return None
        key    = self._dashboard.new_key()
        url    = self._dashboard.get_url()
        manual = self._dashboard.get_manual_url()
        return url, key, f"{url}/auto-login?key={key}", manual

    def _on_text_command(self, text: str):
        # ── Security command interception (PIN never reaches TITAN AI) ──
        sec_result = handle_security_command(text)
        if sec_result is not None:
            self.ui.write_log(f"[Security] {sec_result}")
            return

        if not self._loop or not self.session:
            self.ui.write_log("SYS: Session connecting or not active yet.")
            return

        async def _send_text():
            try:
                self._last_user_request = text
                self._last_user_request_at = time.monotonic()
                self._live_turn_delegated = False
                # Reset interrupt and audio-drop flags so model response is accepted
                self._interrupted = False
                self._drop_model_audio = False
                with self._speaking_lock:
                    self._is_speaking = False
                # In full-brain mode Gemini is only the speech relay. Text
                # commands must therefore enter the same planner used for
                # transcribed voice, rather than asking the relay to answer.
                if self._full_brain:
                    await self._run_full_brain_turn(text)
                    return
                # Close any active mic stream turn so Gemini processes text immediately
                self._qput_audio({"kind": "end"})
                if self._turn_done_event:
                    self._turn_done_event.clear()
                self.ui.set_state("THINKING")
                print(f"[TITAN] ⌨️ Text command sending: '{text}'")
                try:
                    await self.session.send_client_content(
                        turns=[types.Content(parts=[types.Part.from_text(text=text)], role="user")],
                        turn_complete=True,
                    )
                except Exception:
                    await self.session.send_client_content(
                        turns={"parts": [{"text": text}]},
                        turn_complete=True,
                    )
                print(f"[TITAN] ⌨️ Text command sent successfully: '{text}'")
            except Exception as e:
                print(f"[TextCommand] Error sending text command: {e}")
                self.ui.write_log(f"ERR: Text command error: {e}")

        asyncio.run_coroutine_threadsafe(_send_text(), self._loop)

    def set_speaking(self, value: bool):
        with self._speaking_lock:
            was = self._is_speaking
            self._is_speaking = value
        if value and not was:
            # Titan just started talking — drop leftover mic so it cannot
            # clog the websocket or barge-in on itself.
            self._speak_started_at = time.monotonic()
            print("[TITAN] Speaker playback started")
            self._flush_out_queue()
            self.ui.set_state("SPEAKING")
        elif not value:
            self._speak_ended_at = time.monotonic()
            if not self.ui.muted:
                self.ui.set_state("LISTENING")

    def _flush_out_queue(self) -> None:
        q = self.out_queue
        if not q:
            return
        n = 0
        while True:
            try:
                q.get_nowait()
                n += 1
            except Exception:
                break
        if n:
            print(f"[TITAN] 🎤 Flushed {n} leftover mic chunks")

    def _qput_audio(self, item: dict) -> None:
        """Never block the mic callback. If the queue is full, drop oldest."""
        q = self.out_queue
        loop = self._loop
        if not q or not loop:
            return

        def _do():
            try:
                if q.full():
                    try:
                        q.get_nowait()
                    except Exception:
                        return
                q.put_nowait(item)
            except Exception:
                pass

        try:
            loop.call_soon_threadsafe(_do)
        except Exception:
            pass

    def _flag_task_stop(self, reason: str = "") -> None:
        """User talked (or ESC) while a tool is writing — do not save/overwrite."""
        try:
            from task_control import request_cancel
            request_cancel(reason)
        except Exception:
            pass

    def _reset_midtask(self) -> None:
        self._busy_vad = {"in_speech": False, "silence": 0, "voiced": 0}
        self._midtask_pcm = bytearray()

    def _on_midtask_chunk(self, data: bytes, rms: float) -> None:
        """Listen while a tool runs. Do NOT send to Gemini until the tool returns."""
        st = self._busy_vad
        if not st["in_speech"]:
            if rms >= _VAD_BUSY_START_RMS:
                st["in_speech"] = True
                st["silence"] = 0
                st["voiced"] = 1
                self._midtask_pcm = bytearray(data)
                self._flag_task_stop("mic")
                print(f"[TITAN] 🛑 speech during task RMS={rms:.0f} — will not save if still writing")
            return
        self._midtask_pcm.extend(data)
        if rms >= _VAD_BUSY_HOLD_RMS:
            st["voiced"] = st.get("voiced", 0) + 1
            st["silence"] = 0
        else:
            st["silence"] += 1
            if st["silence"] >= _VAD_END_SILENCE and st.get("voiced", 0) >= _VAD_BUSY_MIN_SPEECH:
                self._pending_midtask = bytes(self._midtask_pcm)
                self._midtask_pcm = bytearray()
                st.update({"in_speech": False, "silence": 0, "voiced": 0})
                print(f"[TITAN] 🛑 captured {len(self._pending_midtask)} bytes during task")
            elif st["silence"] >= _VAD_END_SILENCE:
                self._midtask_pcm = bytearray()
                st.update({"in_speech": False, "silence": 0, "voiced": 0})

    def interrupt(self, flush_mic: bool = False) -> None:
        """Hard stop: mute speaker NOW, drop leftover Gemini audio, ignore echo."""
        now = time.monotonic()
        with self._speaking_lock:
            self._is_speaking = False
        self._interrupted = True
        self._drop_model_audio = True
        # Safety net for full-brain mode ONLY: if this interrupt cut off a
        # [SPEAK_NOW] reply before its own turn_complete arrived,
        # _expect_brain_turn_complete would otherwise stay stuck True
        # forever. Gated behind self._full_brain because _mute_brain_filler
        # is only ever un-set inside the full-brain code path — setting it
        # True here unconditionally (my bug, previous round) meant that in
        # NORMAL mode, the very first barge-in permanently muted all future
        # Gemini audio for the rest of the session with nothing left to
        # un-mute it. That's why it went silent and stayed silent.
        if getattr(self, "_full_brain", False):
            self._expect_brain_turn_complete = False
            self._mute_brain_filler = True
        self._speak_ended_at = now
        self._vad_suppress_until = now + _VAD_SUPPRESS_S
        # ESC mutes the speaker. It does NOT stop the worker job.

        # Kill PortAudio buffer so ESC actually silences the speaker
        stream = self._play_stream
        if stream is not None:
            try:
                stream.abort()
            except Exception:
                pass
            try:
                stream.start()
            except Exception:
                pass

        q = self.audio_in_queue
        if q:
            drained = 0
            while True:
                try:
                    q.get_nowait()
                    drained += 1
                except Exception:
                    break
            if drained:
                print(f"[TITAN] ✋ Interrupted — {drained} speaker chunks discarded")

        oq = self.out_queue
        if flush_mic and oq:
            mic_drained = 0
            while True:
                try:
                    oq.get_nowait()
                    mic_drained += 1
                except Exception:
                    break
            if mic_drained:
                print(f"[TITAN] 🎤 Flushed {mic_drained} pending mic chunks")

        if flush_mic:
            try:
                from actions.voice_face_id import _VOICE_GATE_BUFFER
                _VOICE_GATE_BUFFER.clear()
            except Exception:
                pass

        if self._turn_done_event:
            self._turn_done_event.clear()

        if self.ui and not self.ui.muted:
            try:
                self.ui.set_state("LISTENING")
            except Exception:
                pass

    def speak(self, text: str):
        if not self._loop or not self.session:
            return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns={"parts": [{"text": text}]},
                turn_complete=True
            ),
            self._loop
        )

    def speak_error(self, tool_name: str, error: str):
        short = str(error)[:120]
        self.ui.write_log(f"ERR: {tool_name} — {short}")
        self.speak(f"Sir, {tool_name} encountered an error. {short}")

    @staticmethod
    def _realtime_input_config():
        """Manual activity only if the SDK has ActivityStart. Else slow server VAD."""
        start_cls = getattr(types, "ActivityStart", None)
        if start_cls is not None:
            try:
                return types.RealtimeInputConfig(
                    automatic_activity_detection=types.AutomaticActivityDetection(
                        disabled=True,
                    )
                )
            except Exception:
                pass
        try:
            return types.RealtimeInputConfig(
                automatic_activity_detection=types.AutomaticActivityDetection(
                    disabled=False,
                    start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
                    end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_LOW,
                    prefix_padding_ms=40,
                    silence_duration_ms=1400,
                )
            )
        except Exception:
            return None

    def _build_config(self) -> types.LiveConnectConfig:
        from datetime import datetime

        # Load customization from config
        try:
            _cfg = json.loads(open(API_CONFIG_PATH, encoding="utf-8").read())
            self._asst_name = (_cfg.get("assistant_name") or "TITAN").strip()
            _user_name = (_cfg.get("user_name") or "").strip()
        except Exception:
            self._asst_name = "TITAN"
            _user_name = ""

        memory     = load_memory()
        mem_str    = format_memory_for_prompt(memory)
        sys_prompt = _load_system_prompt()

        now      = datetime.now()
        time_str = now.strftime("%A, %B %d, %Y — %I:%M %p")
        time_ctx = (
            f"[SESSION-START CLOCK — may be stale]\n"
            f"Session opened around: {time_str}\n"
            f"If the user asks the time/date, call get_clock. Do not use this stamp.\n\n"
        )

        # Identity injection — overrides any hardcoded name in prompt.txt
        _addr = (f"ADDRESS: Always call the user '{_user_name}'."
                 if _user_name
                 else "ADDRESS: When speaking Turkish → always say \"efendim\". "
                      "When speaking English → say \"sir\". Never mix languages.")
        identity_ctx = (
            f"[IDENTITY]\n"
            f"Your name is {self._asst_name}. "
            f"Always refer to yourself as {self._asst_name}.\n"
            f"{_addr}\n\n"
        )

        parts = [time_ctx, identity_ctx]
        if mem_str:
            parts.append(mem_str)
        try:
            pad_txt = format_pad_for_prompt()
            if pad_txt:
                parts.append(pad_txt)
        except Exception:
            pass
        parts.append(sys_prompt)

        all_tools = list(TOOL_DECLARATIONS)
        if getattr(self, "plugin_registry", None):
            try:
                all_tools.extend(self.plugin_registry.get_tool_declarations())
            except Exception:
                pass
        if getattr(self, "skill_registry", None) and len(self.skill_registry) > 0:
            try:
                skill_index = self.skill_registry.index_for_prompt()
                if skill_index:
                    parts.append(skill_index)
                all_tools.append(self.skill_registry.get_tool_declaration())
                all_tools.append(self.skill_registry.get_search_tool_declaration())
            except Exception:
                pass

        # Stash the FULL set for workers (core/task_workers.py) and the NVIDIA
        # full-brain loop. Workers must keep strictly more power than the boss.
        self._all_tool_declarations = all_tools

        # The boss only ever sees the fast, speakable subset. See
        # WORKER_ONLY_TOOLS for why this is a hard filter and not a prompt rule.
        boss_tools = [
            d for d in all_tools
            if (d.get("name") if isinstance(d, dict) else getattr(d, "name", None))
            not in WORKER_ONLY_TOOLS
        ]
        _removed = len(all_tools) - len(boss_tools)
        print(f"[TITAN] Tool split: boss={len(boss_tools)} tools, "
              f"worker={len(all_tools)} tools ({_removed} worker-only)")

        self._full_brain = _full_brain_enabled()
        if self._full_brain:
            # Gemini Live becomes a pure STT/TTS relay: no tools, no
            # planning prompt — see _SILENT_RELAY_PROMPT + _run_full_brain_turn().
            live_system_instruction = _SILENT_RELAY_PROMPT
            live_tools_kwarg = []   # no function_declarations at all
            # Mute by default: any auto-reply Gemini generates from raw
            # user speech (unavoidable — VAD triggers generation regardless
            # of the prompt) stays silent until _run_full_brain_turn()
            # explicitly unmutes it for the [SPEAK_NOW] answer.
            self._mute_brain_filler = True
        else:
            live_system_instruction = "\n".join(parts)
            live_tools_kwarg = [{"function_declarations": boss_tools}]

        cfg_kwargs = dict(
            response_modalities=["AUDIO"],
            output_audio_transcription={},
            input_audio_transcription={},
            system_instruction=live_system_instruction,
            tools=live_tools_kwarg,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Charon"
                    )
                )
            ),
            # ── Latency fix #1: kill "thinking" before it speaks ──────────────
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
                include_thoughts=False,
            ),
        )
        _rt = self._realtime_input_config()
        if _rt is not None:
            cfg_kwargs["realtime_input_config"] = _rt
        # Long sessions (sliding window compression so sessions never 1011-crash)
        try:
            cfg_kwargs["context_window_compression"] = types.ContextWindowCompressionConfig(
                sliding_window=types.SlidingWindow(),
                trigger_tokens=25000,
            )
        except Exception:
            pass
        # Live voice upgrades: session resumption, context compression, affective dialog
        try:
            cfg_kwargs["session_resumption"] = types.SessionResumptionConfig()
        except Exception:
            pass
        if getattr(self, "_enhanced_live", True):
            try:
                cfg_kwargs["enable_affective_dialog"] = True
            except Exception:
                pass
        return types.LiveConnectConfig(**cfg_kwargs)

    async def _run_deep_think(self, task: str) -> str:
        """
        One-off call to a standard (non-live) Gemini model with full thinking
        enabled. This runs OUTSIDE the live session, so it never blocks the
        mic/audio pipeline — the live session stays fast for everything else,
        and only this specific tool call pays the "thinking" latency cost,
        on purpose, for tasks that actually need it.
        """
        try:
            memory  = load_memory()
            mem_str = format_memory_for_prompt(memory)

            prompt = (
                "You are TITAN's reasoning module. Think through this carefully "
                "and give a clear, well-structured, spoken-friendly answer "
                "(it will be read aloud, so keep formatting simple — no markdown tables). "
                f"\n\nContext about the user:\n{mem_str}\n\nTask:\n{task}"
            )

            client = genai.Client(
                api_key=_get_api_key(),
                http_options={"api_version": "v1beta"},
            )

            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=False,
                        thinking_budget=-1,  # Full dynamic deep reasoning (no artificial token limit)
                    ),
                ),
            )

            answer = (response.text or "").strip()
            return answer or "I thought about it but couldn't come up with a clear answer — could you rephrase the task?"

        except Exception as e:
            print(f"[DeepThink] ❌ {e}")
            return f"I ran into an issue while thinking that through: {e}"

    async def _deliver_midtask_speech(self) -> None:
        """After a tool returns, give Gemini the words the user said during it."""
        st = self._busy_vad
        if st.get("in_speech") and st.get("voiced", 0) >= _VAD_BUSY_MIN_SPEECH and self._midtask_pcm:
            self._pending_midtask = bytes(self._midtask_pcm)
        pcm = self._pending_midtask or b""
        self._pending_midtask = b""
        self._reset_midtask()
        try:
            from task_control import clear_cancel
            clear_cancel()
        except Exception:
            pass
        if not pcm or not self.session:
            return
        print(f"[TITAN] 🎤 delivering mid-task speech ({len(pcm)} bytes)")
        try:
            await self.session.send_client_content(
                turns={"parts": [{"text": (
                    "[SYSTEM] User spoke WHILE you were working. "
                    "If the tool said STOPPED, the file was NOT saved. "
                    "Their voice follows. Obey it. "
                    "stop / wait / don't touch → do not call the same tool again. "
                    "A specific change → only that change. "
                    "Do not restart the old job unless they say continue."
                )}]},
                turn_complete=False,
            )
        except Exception as e:
            print(f"[TITAN] midtask text: {e}")
        start_cls = getattr(types, "ActivityStart", None)
        end_cls = getattr(types, "ActivityEnd", None)
        try:
            if start_cls is not None:
                await self.session.send_realtime_input(activity_start=start_cls())
            step = 4096
            for i in range(0, len(pcm), step):
                await self.session.send_realtime_input(
                    audio=types.Blob(data=pcm[i:i + step], mime_type=_AUDIO_MIME)
                )
            if end_cls is not None:
                await self.session.send_realtime_input(activity_end=end_cls())
            else:
                await self.session.send_realtime_input(audio_stream_end=True)
        except Exception as e:
            print(f"[TITAN] midtask audio: {e}")

    def _looks_like_noise(self, text: str) -> bool:
        """Filters out mic false-triggers before they burn an NVIDIA call.
        Real Gemini transcripts of silence/background noise commonly come
        back as bracketed placeholders like '[noise]', '<noise>', '...',
        or near-empty strings — not real speech."""
        t = text.strip().strip(".").strip()
        if len(t) < 2:
            return True
        stripped = t.strip("[]<>() ").lower()
        if stripped in ("noise", "silence", "music", "inaudible", "unclear", "blank_audio"):
            return True
        return False

    async def _run_full_brain_turn(self, user_text: str) -> None:
        """Full-brain mode entry point: NVIDIA plans + calls tools, Gemini
        Live only speaks the final result. Triggered from _receive_audio()
        when a user turn's transcript is finalized (sc.turn_complete).

        Two things this guards against, both seen in real sessions:
          1. Overlap — if a second turn fires while one is still running
             (e.g. a stray VAD trigger), concurrent tasks would interleave
             writes into the shared self._nvidia_history and corrupt the
             tool_call/tool_response pairing NVIDIA expects. A lock forces
             turns to run one at a time; a turn that arrives mid-brain is
             dropped (not queued) since queuing would mean answering a
             stale question seconds later.
          2. Gemini talking over itself — Gemini Live auto-generates SOME
             reply the instant VAD marks turn_complete, regardless of the
             "silent relay" system prompt (prompting can't fully suppress
             that, it's the API's own turn-boundary behaviour). We can't
             stop it from generating, but we CAN stop it from being heard:
             self._mute_brain_filler mutes PLAYBACK ONLY of that auto-reply
             (a dedicated flag — NOT self._drop_model_audio, which is also
             checked on the send side to suppress activity_end after an
             ESC interrupt; reusing it here would silently stop us from
             ever telling Gemini a user turn ended, breaking transcription).
             Un-muted only for the turn we ourselves inject below.
        """
        if not user_text or not user_text.strip():
            return
        if self._looks_like_noise(user_text):
            print(f"[NvidiaBrain] ignoring noise-like transcript: {user_text!r}")
            return

        if self._brain_lock is None:
            self._brain_lock = asyncio.Lock()
        if self._brain_lock.locked():
            print(f"[NvidiaBrain] already thinking — dropping overlapping turn: {user_text!r}")
            return

        async with self._brain_lock:
            # Mute whatever filler Gemini's own auto-reply generates for
            # this raw-speech turn; only the [SPEAK_NOW] reply should play.
            self._mute_brain_filler = True
            self.ui.set_state("THINKING")
            try:
                answer = await run_brain_turn(
                    user_text=user_text,
                    history=self._nvidia_history,
                    tool_executor=self._execute_tool_by_name,
                    gemini_tool_declarations=self._all_tool_declarations,
                    system_prompt=(
                        _load_system_prompt()
                        + "\n\n"
                        + (self.skill_registry.index_for_prompt() if getattr(self, "skill_registry", None) else "")
                        + "\n\nFULL-BRAIN EXECUTION CONTRACT:\n"
                        + f"You are {self._asst_name}, the deliberate task-planning brain. "
                        "First classify every request yourself: answer or act directly when it is a simple "
                        "one-step request; for work that needs multiple actions, real file changes, research, "
                        "or verification, create a checklist plan first. Select and load the relevant skill "
                        "before acting whenever one matches. A loaded skill is authoritative: follow its "
                        "required approach, tools, validation, and quality checks rather than substituting "
                        "a simpler generic implementation. Then execute each real step and verify the "
                        "deliverable before claiming success. Do not use a checklist just for show, and do not "
                        "plan simple requests unnecessarily. Do not merely describe what you could do. "
                        "For underspecified creative work, ask only for details that materially change "
                        "the result; otherwise proceed using sensible professional defaults. Your final "
                        "answer is spoken aloud, so make it short, natural, and honest."
                    ),
                )
            except Exception as e:
                print(f"[NvidiaBrain] turn failed: {e}")
                traceback.print_exc()
                answer = "I hit an error reaching the planning model, sir — please check the NVIDIA API key and try again."

            session = self.session
            if not session:
                self._mute_brain_filler = True
                return
            try:
                # Unmute right before injecting — this is the ONLY generation
                # in full-brain mode that should actually reach the speaker.
                # DO NOT re-mute here: send_client_content() returns as soon
                # as the message is SENT, not after Gemini finishes streaming
                # the spoken reply back (that arrives seconds later as
                # separate response.data/turn_complete events in the recv
                # loop). Re-muting right after this await — which the old
                # code did in a `finally` block — silenced the real answer
                # before it ever played. We stay unmuted until the recv
                # loop sees THIS turn's turn_complete (flag set below) and
                # re-arms muting there instead. See _receive_audio().
                self._expect_brain_turn_complete = True
                self._mute_brain_filler = False
                await session.send_client_content(
                    turns={"parts": [types.Part.from_text(text=f"[SPEAK_NOW] {answer}")]},
                    turn_complete=True,
                )
            except Exception as e:
                print(f"[NvidiaBrain] failed to hand answer back to Gemini Live: {e}")
                self._expect_brain_turn_complete = False
                self._mute_brain_filler = True

    async def _dispatch_tools(self, tool_call) -> None:
        """Run tools without blocking the websocket receive loop."""
        if self._tool_lock is None:
            self._tool_lock = asyncio.Lock()
        async with self._tool_lock:
            try:
                from task_control import clear_cancel
                clear_cancel()
            except Exception:
                pass
            self._pending_midtask = b""
            self._reset_midtask()
            self._tool_busy = True
            interrupted = False
            try:
                fn_responses = []
                for fc in tool_call.function_calls:
                    print(f"[TITAN] 📞 {fc.name}")
                    fr = await self._execute_tool(fc)
                    fn_responses.append(fr)
                if self.session:
                    await self.session.send_tool_response(
                        function_responses=fn_responses
                    )
                    names = [getattr(fc, "name", "") for fc in tool_call.function_calls]
                    try:
                        from task_control import is_cancelled
                        interrupted = bool(is_cancelled()) or bool(self._pending_midtask) or bool(self._busy_vad.get("in_speech"))
                    except Exception:
                        interrupted = bool(self._pending_midtask)

            except Exception as e:
                print(f"[TITAN] ❌ tool dispatch: {e}")
                traceback.print_exc()
            finally:
                self._tool_busy = False
            await self._deliver_midtask_speech()

    async def _execute_tool(self, fc) -> types.FunctionResponse:
        """Gemini-Live path: unwrap the SDK's FunctionCall object and hand off
        to the shared dispatcher, then re-wrap as a Gemini FunctionResponse."""
        result = await self._execute_tool_by_name(fc.name, dict(fc.args or {}), call_id=fc.id)
        return types.FunctionResponse(id=fc.id, name=fc.name, response={"result": result})

    def _start_worker_for_request(self, task: str, role: str = "executor") -> str:
        """Start one durable worker only after a final user transcript exists."""
        if not task or self._looks_like_noise(task):
            return "No valid user task is available."
        catalog = self.skill_registry.index_for_prompt() if getattr(self, "skill_registry", None) else ""
        worker = task_workers.start(
            task, self._execute_tool_by_name, self._all_tool_declarations, catalog, role=role
        )
        self._live_turn_delegated = True
        return f"Task transferred to persistent worker {worker.id}."

    async def _execute_tool_by_name(self, name: str, raw_args: dict, call_id: str = "brain") -> str:
        """Shared tool dispatcher — the ONLY place tool names get routed to
        real implementations. Callable from two places:
          1. _execute_tool() above, for the Gemini-Live path (fc.name/fc.args).
          2. core/nvidia_brain.py's agent loop, directly by (name, args) —
             NVIDIA decides the tool call, this function still does the work.
        Returns the plain result string (not a FunctionResponse) so both
        callers can wrap it however their protocol needs.
        """
        # Do not let the short-lived voice turn race the durable worker after a
        # successful handoff.  `brain` calls originate inside that worker and
        # are deliberately exempt. Also exempt the message/interrupt tools so
        # the user can still steer or cancel a running worker mid-flight.
        if (
            call_id != "brain"
            and self._live_turn_delegated
            and name not in {
                "task_worker_status", "send_task_worker_message", "interrupt_task_worker",
                "set_titan_microphone", "shutdown_titan",
            }
        ):
            return "This task was delegated to its persistent worker. Do not run more task tools in this live turn. Tell the user it is working."

        # Hard power split. These tools are stripped from the boss's declared
        # tool list in _build_config(), but a model can still hallucinate a call
        # to a tool it was never given - so refuse at the dispatcher too, and
        # name the correct path instead of just erroring.
        if call_id != "brain" and not running_in_worker() and name in WORKER_ONLY_TOOLS:
            print(f"[TITAN] ⛔ boss attempted worker-only tool: {name}")
            return (
                f"'{name}' is worker-only and is not available in a live voice turn. "
                "Anything that creates or edits a file, runs a command, or needs skill "
                "instructions must be handed to a worker: call start_task_worker with the "
                "user's COMPLETE request, including every detail and constraint they gave."
            )

        # DeepSeek Pre-Execute Pipeline (Path Expansion & Arg Sanitization)
        args = main_agent_loop.pre_step(name, raw_args)

        print(f"[TITAN] 🔧 {name}  {args}")
        self.ui.set_state("THINKING")

        if name == "save_memory":
            category = args.get("category", "notes")
            key      = args.get("key", "")
            value    = args.get("value", "")
            if key and value:
                update_memory({category: {key: {"value": value}}})
                print(f"[Memory] 💾 save_memory: {category}/{key} = {value}")
            if not self.ui.muted:
                self.ui.set_state("LISTENING")
            return "Memory saved. Do not repeat what you just said."

        loop   = asyncio.get_event_loop()
        result = "Done."

        try:
            if name == "todo_write":
                action = args.get("action", "")
                if action == "set_plan":
                    result = todo_engine.set_plan(args.get("title", "Plan"), args.get("steps", []))
                elif action == "update_step":
                    result = todo_engine.update_step(args.get("step_id", 1), args.get("status", "in_progress"), args.get("details", ""))
                else:
                    result = f"Unknown todo action: {action}"

            elif name == "todo_read":
                result = todo_engine.get_summary()

            elif name == "schedule":
                dur = float(args.get("duration_seconds", 10))
                prompt = args.get("prompt", "Reminder")
                result = scheduler.add_timer(prompt, dur)

            elif name == "set_goal":
                desc = args.get("description", "")
                rounds = int(args.get("max_rounds", 10))
                result = goal_manager.set_goal(desc, rounds)

            elif name == "complete_goal":
                outcome = args.get("outcome", "Done")
                result = goal_manager.complete_goal(outcome)

            elif name == "ask_user_question":
                    q = args.get("question", "")
                    header = args.get("header", "")
                    options = args.get("options", [])
                    if running_in_worker():
                        # Worker cannot speak. Hand the question to the boss and
                        # block THIS worker (not the voice loop) until answered.
                        result = await task_workers.ask_boss(q, options)
                    else:
                        result = interaction_engine.ask(q, header=header, options=options)

            elif name == "answer_worker_question":
                    result = task_workers.answer_question(
                        args.get("worker_id", ""), args.get("answer", "")
                    )


            elif name == "enter_plan_mode":
                goal = args.get("goal", "")
                result = plan_mode.enter_plan_mode(goal)

            elif name == "exit_plan_mode":
                summary = args.get("summary", "")
                result = plan_mode.exit_plan_mode(summary)

            elif name == "job_list":
                result = json.dumps(job_registry.list_jobs(), indent=2)

            elif name == "job_output":
                jid = args.get("job_id", "")
                result = job_registry.read_output(jid)

            elif name == "job_kill":
                jid = args.get("job_id", "")
                reason = args.get("reason", "Cancelled by user")
                result = job_registry.kill_job(jid, reason)

            elif name == "read_file":
                p = args.get("path", "")
                offset = int(args.get("offset_lines", 1))
                max_l = int(args.get("max_lines", 250))
                result = read_file(p, offset_lines=offset, max_lines=max_l)

            elif name == "write_file":
                p = args.get("path", "")
                content = args.get("content", "")
                result = write_file(p, content)

            elif name == "str_replace_editor":
                p = args.get("path", "")
                old_s = args.get("old_str", "")
                new_s = args.get("new_str", "")
                result = str_replace_editor(p, old_s, new_s)

            elif name == "grep_search":
                q = args.get("query", "")
                spath = args.get("search_path", ".")
                is_re = bool(args.get("is_regex", False))
                result = grep_search(q, search_path=spath, is_regex=is_re)

            elif name == "glob_search":
                pat = args.get("pattern", "")
                spath = args.get("search_path", ".")
                result = glob_search(pat, search_path=spath)

            elif name == "python_eval":
                code = args.get("code", "")
                tout = int(args.get("timeout", 30))
                result = json.dumps(run_python_code(code, timeout=tout), indent=2)

            elif name == "web_fetch":
                url = args.get("url", "")
                max_c = int(args.get("max_chars", 12000))
                result = await loop.run_in_executor(None, lambda: web_fetch(url, max_chars=max_c))

            elif name == "open_app":
                r = await loop.run_in_executor(None, lambda: open_app(parameters=args, response=None, player=self.ui))
                result = r or f"Opened {args.get('app_name')}."

            elif name == "weather_report":
                r = await loop.run_in_executor(None, lambda: weather_action(parameters=args, player=self.ui))
                result = r or "Weather delivered."

            elif name == "browser_control":
                r = await loop.run_in_executor(None, lambda: browser_control(parameters=args, player=self.ui))
                result = r or "Done."

            elif name == "file_controller":
                r = await loop.run_in_executor(None, lambda: file_controller(parameters=args, player=self.ui))
                result = r or "Done."

            elif name == "send_message":
                r = await loop.run_in_executor(None, lambda: send_message(parameters=args, response=None, player=self.ui, session_memory=None))
                result = r or f"Message sent to {args.get('receiver')}."

            elif name == "reminder":
                r = await loop.run_in_executor(None, lambda: reminder(parameters=args, response=None, player=self.ui))
                result = r or "Reminder set."

            elif name == "youtube_video":
                r = await loop.run_in_executor(None, lambda: youtube_video(parameters=args, response=None, player=self.ui))
                result = r or "Done."

            elif name == "screen_process":
                import time as _t_mod
                _now = _t_mod.monotonic()
                _cooldown = 4.0  # seconds — covers echo window after speaking ends
                if self._vision_busy or (_now - self._vision_last_time) < _cooldown:
                    _wait = max(0, _cooldown - (_now - self._vision_last_time))
                    print(f"[Vision] ⏳ Cooldown active ({_wait:.1f}s remaining) — ignoring duplicate call")
                    result = "Vision is still processing the previous request. I will not call this again."
                else:
                    self._vision_busy      = True
                    self._vision_last_time = _now
                    angle     = args.get("angle", "screen").lower()
                    user_text = args.get("text", "What do you see?")
                    if angle == "camera":
                        img_b, mime_t = await loop.run_in_executor(None, _capture_camera)
                        self.ui.start_camera_stream()
                        self._vision_cam_active = True
                        print(f"[Vision] 📷 Camera: {len(img_b):,} bytes")
                        _stall = "camera"
                    else:
                        img_b, mime_t = await loop.run_in_executor(None, _capture_screen)
                        print(f"[Vision] 🖥️  Screen: {len(img_b):,} bytes")
                        _stall = "screen"
                    self._pending_vision = (img_b, mime_t, user_text, angle)
                    result = (
                        f"[VISION_ACTIVE] {_stall.capitalize()} captured. "
                        f"Immediately say ONE short natural sentence in the user's own language, "
                        f"telling them you are looking at their {_stall} right now. "
                        f"Do NOT describe or guess content — the actual image arrives in the NEXT message."
                    )

            elif name == "close_camera":
                self.ui.stop_camera_stream()
                result = "Camera closed."

            elif name == "computer_settings":
                r = await loop.run_in_executor(None, lambda: computer_settings(parameters=args, response=None, player=self.ui))
                result = r or "Done."

            elif name == "desktop_control":
                r = await loop.run_in_executor(None, lambda: desktop_control(parameters=args, player=self.ui))
                result = r or "Done."

            elif name == "code_helper":
                r = await loop.run_in_executor(None, lambda: code_helper(parameters=args, player=self.ui, speak=self.speak))
                result = r or "Done."

            elif name == "dev_agent":
                r = await loop.run_in_executor(None, lambda: dev_agent(parameters=args, player=self.ui, speak=self.speak))
                result = r or "Done."

            elif name == "web_search":
                r = await loop.run_in_executor(None, lambda: web_search_action(parameters=args, player=self.ui))
                result = r or "Done."
                # Mirror results to the on-screen content panel
                _mode = args.get("mode", "search")
                if r and not r.startswith("No results") and not r.startswith("Search failed"):
                    _query = args.get("query") or ", ".join(args.get("items", []))
                    _label = f"{_mode.upper()} — {_query[:38]}" if _query else _mode.upper()
                    self.ui.show_content(_label, r)
            elif name == "file_processor":
                if not args.get("file_path") and self.ui.current_file:
                    args["file_path"] = self.ui.current_file
                r = await loop.run_in_executor(
                    None,
                    lambda: file_processor(parameters=args, player=self.ui, speak=self.speak)
                )
                result = r or "Done."

            elif name == "ui_automation":
                from actions import ui_automation as uia
                action = args.get("action", "click")
                app_name = args.get("app_name", "")
                element_name = args.get("element_name", "")
                text = args.get("text", "")
                index = args.get("index", 0)

                if action == "click":
                    r = await loop.run_in_executor(None, lambda: uia.ui_click(app_name, element_name, index))
                elif action == "type":
                    r = await loop.run_in_executor(None, lambda: uia.ui_type(app_name, element_name, text))
                elif action == "get_text":
                    r = await loop.run_in_executor(None, lambda: uia.ui_get_text(app_name, element_name))
                elif action == "dump_tree":
                    r = await loop.run_in_executor(None, lambda: uia.ui_dump_tree(app_name, search_query=text))
                else:
                    r = f"Unknown action: {action}"
                result = r or "Done."

            elif name == "computer_control":
                r = await loop.run_in_executor(None, lambda: computer_control(parameters=args, player=self.ui))
                result = r or "Done."

            elif name == "game_updater":
                r = await loop.run_in_executor(None, lambda: game_updater(parameters=args, player=self.ui, speak=self.speak))
                result = r or "Done."

            elif name == "flight_finder":
                r = await loop.run_in_executor(None, lambda: flight_finder(parameters=args, player=self.ui))
                result = r or "Done."

            elif name == "shadow_link":
                r = await loop.run_in_executor(None, lambda: shadow_link_control(parameters=args))
                result = r or "Done."

            elif name == "voice_face_id":
                r = await loop.run_in_executor(None, lambda: voice_face_id(parameters=args, player=self.ui))
                result = r or "Done."

            elif name == "system_status":
                r = await loop.run_in_executor(None, get_system_status)
                result = str(r)


            elif name == "get_clock":
                result = get_live_clock()

            elif name == "work_pad":
                r = await loop.run_in_executor(None, lambda: run_work_pad(args))
                result = str(r)
                try:
                    md = (r or {}).get("markdown") if isinstance(r, dict) else None
                    if md:
                        self.ui.show_content("WORK PAD", md)
                except Exception:
                    pass

            elif name == "deep_think":
                task = args.get("task", "").strip()
                if not task:
                    result = "No task provided to think through."
                else:
                    result = await self._run_deep_think(task)

            elif name == "start_task_worker":
                task = args.get("task", "").strip()
                role = args.get("role", "executor").strip() or "executor"
                # Route through the same helper the load_skill auto-delegation
                # path uses (_start_worker_for_request), instead of duplicating
                # the raw task_workers.start() call here. That helper also
                # sets self._live_turn_delegated = True — calling task_workers
                # .start() directly (the old code) skipped that, so a worker
                # calling this tool explicitly (rather than via the load_skill
                # trigger) never armed the "don't also try this yourself"
                # guard, letting the live turn duplicate/race the worker.
                result = self._start_worker_for_request(task, role=role)

            elif name == "task_worker_status":
                result = json.dumps(task_workers.list(), indent=2)

            elif name == "send_task_worker_message":
                wid = args.get("worker_id", "")
                msg = args.get("message", "")
                result = task_workers.send_message(wid, msg)

            elif name == "interrupt_task_worker":
                wid = args.get("worker_id", "")
                result = task_workers.interrupt(wid)

            elif name == "task_set_plan":
                result = await task_workers.set_plan(args.get("steps", []))

            elif name == "verify_task_result":
                result = await task_workers.verify_current(
                    args.get("outputs", []), args.get("summary", "")
                )

            elif name == "manage_monitor":
                action = args.get("action", "").lower().strip()
                topic  = args.get("topic", "").strip()
                if action == "add" and topic:
                    result = await asyncio.to_thread(add_monitor, topic)
                elif action == "remove" and topic:
                    result = await asyncio.to_thread(remove_monitor, topic)
                elif action == "list":
                    topics = await asyncio.to_thread(list_monitors)
                    result = ("Monitoring: " + ", ".join(topics)) if topics else "No topics are being monitored."
                else:
                    result = "Specify action (add/remove/list) and a topic."

            elif name == "shutdown_titan":
                # Genuinely irreversible — gate behind a real button press instead
                # of trusting the model's own "confirmed=yes". See core/confirm.py.
                async def _do_shutdown():
                    await self._save_session_summary()
                    if self.session:
                        try:
                            await self.session.send_client_content(
                                turns={"parts": [{"text": "Say a brief natural goodbye to the user."}]},
                                turn_complete=True,
                            )
                        except Exception:
                            pass
                    await asyncio.sleep(1.5)
                    undo_clear()
                    import os as _os
                    _os._exit(0)

                def _run_shutdown():
                    if self._loop:
                        asyncio.run_coroutine_threadsafe(_do_shutdown(), self._loop)
                    return "Shutdown started."

                assistant_name = self.ui.assistant_name or "TITAN"
                result = confirm.request(
                    key="shutdown_titan",
                    title=f"Shut down {assistant_name}?",
                    detail="This ends the current session completely.",
                    run=_run_shutdown,
                )

            elif name == "set_titan_microphone":
                muted = bool(args.get("muted", True))
                was_muted = self.ui.muted
                self.ui.muted = muted
                if was_muted != muted:
                    def _undo_mute(prev=was_muted):
                        self.ui.muted = prev
                        return "TITAN microphone unmuted." if not prev else "TITAN microphone muted."
                    push_undo(f"TITAN microphone {'muted' if muted else 'unmuted'}", _undo_mute)
                result = "TITAN microphone muted." if muted else "TITAN microphone active."

            elif name == "undo_last_action":
                if bool(args.get("peek_only", False)):
                    label = undo_peek()
                    result = f"The last reversible action was: {label}." if label else "There is nothing to undo right now."
                else:
                    result = await loop.run_in_executor(None, undo_last)

            elif name == "set_titan_audio_device":
                action = str(args.get("action", "list")).lower()
                kind = str(args.get("kind", "input")).lower()
                if kind not in ("input", "output"):
                    kind = "input"
                if action == "set":
                    dev_name = str(args.get("device_name", "")).strip()
                    if kind == "input":
                        save_input_device(dev_name)
                    else:
                        save_output_device(dev_name)
                    result = (
                        f"{'Microphone' if kind == 'input' else 'Speaker'} set to "
                        f"'{dev_name or 'system default'}'. This takes effect on TITAN's next reconnect."
                    )
                else:
                    devices = await loop.run_in_executor(None, lambda: audio_devices.list_devices(kind))
                    result = (
                        f"Available {'microphones' if kind == 'input' else 'speakers'}: "
                        + (", ".join(devices) if devices else "none found — using system default")
                    )

            elif name == "search_skills":
                query = args.get("query", "").strip()
                if getattr(self, "skill_registry", None):
                    result = await loop.run_in_executor(
                        None, lambda: self.skill_registry.search_for_tool(query)
                    )
                else:
                    result = "Skill registry is not available."

            elif name == "load_skill":
                # No deferred-handoff branch here any more. The old code did NOT
                # load the skill in a live turn: it stashed the name and bound it
                # to whatever transcript arrived next, so an interjection ("no",
                # "wait") became the worker's task and the worker failed with
                # "I don't understand your instruction". load_skill is now
                # worker-only (WORKER_ONLY_TOOLS) and always really loads.
                skill_name = args.get("skill_name", "").strip()
                if getattr(self, "skill_registry", None):
                    result = await loop.run_in_executor(
                        None, lambda: self.skill_registry.load(skill_name)
                    )
                else:
                    result = "Skill registry is not available."

            elif name == "run_command":
                cmd = args.get("cmd", "")
                cwd = args.get("cwd") or str(BASE_DIR)  # default to project root, not the
                                                          # process's arbitrary launch cwd —
                                                          # this is what made relative skill
                                                          # script paths break silently.
                timeout = int(args.get("timeout") or 30)
                if not cmd:
                    result = "No command provided."
                else:
                    # NOTE: run_command() itself now auto-swaps a bare "python"
                    # for the resolved sandbox/project interpreter internally
                    # (see core/exec.py's _resolve_python) — no need to do that
                    # swap here too.
                    _cmd = cmd
                    r = await loop.run_in_executor(
                        None, lambda: run_command(_cmd, cwd=cwd, timeout=timeout)
                    )
                    self._log_action(name, args)
                    result = (
                        f"exit_code={r['exit_code']}\n"
                        f"stdout:\n{r['stdout'][-4000:]}\n"
                        f"stderr:\n{r['stderr'][-2000:]}"
                    )
                    # Show the user what TITAN just ran — this is the whole
                    # point of the workspace overlay: visibility without
                    # them needing to type anything or open it manually.
                    try:
                        fname = _cmd.split()[-1] if isinstance(_cmd, str) else str(_cmd)
                        code_preview = ""
                        try:
                            script_path = _cmd.split()[-1] if isinstance(_cmd, str) else ""
                            if script_path and Path(script_path).is_file():
                                code_preview = Path(script_path).read_text(encoding="utf-8", errors="ignore")[:6000]
                        except Exception:
                            pass
                        self.ui._editor_sig.emit(
                            Path(fname).name, code_preview,
                            f"$ {cmd}\n{r['stdout']}\n{r['stderr']}",
                        )
                    except Exception:
                        pass

            elif getattr(self, "plugin_registry", None) and self.plugin_registry.has(name):
                r = await loop.run_in_executor(
                    None,
                    lambda: self.plugin_registry.run(name, args, player=self.ui, session_memory=None),
                )
                result = r or "Done."

            else:
                result = f"Unknown tool: {name}"

            result = _finalize(result)
            self._log_action(name, args)

        except Exception as e:
            result = f"Tool '{name}' failed: {e}"
            traceback.print_exc()
            try:
                self.ui.write_log(f"ERR: {name} — {str(e)[:120]}")
            except Exception:
                pass

        if name in _WORK_TOOLS:
            try:
                absorb_work_output(name, args, result)
            except Exception as e:
                print(f"[WorkPad] absorb: {e}")
            # Do NOT append KEEP WORKING / resume brief. That made Titan
            # start leftover pad jobs (speedtest, format PDF) in a loop.
            if _looks_tool_error(str(result)):
                result = (
                    str(result)
                    + "\n\n[FIX THIS] Only retry if THIS tool is what the user just asked for. "
                    "Do not start a different leftover job."
                )

        # DeepSeek Post-Execute Pipeline (Error Guard, Spill Engine & Event Logging)
        step_result = main_agent_loop.post_step(name, args, result)
        result = step_result["content"]
        session_logger.record_event("tool_call", {
            "tool": name,
            "args": args,
            "result": str(result)[:300],
            "ok": step_result["ok"],
            "was_spilled": step_result.get("was_spilled", False),
        })

        if not self.ui.muted:
            self.ui.set_state("LISTENING")

        print(f"[TITAN] 📤 {name} → {str(result)[:80]}")
        return result

    async def _send_realtime(self):
        """Push mic packets the instant they arrive. No 12-second backlog."""
        print("[TITAN] 📡 Send loop started")
        while True:
            item = await self.out_queue.get()
            session = self.session
            if not session or not item:
                continue
            kind = item.get("kind", "audio")
            try:
                if kind == "activity_start":
                    start_cls = getattr(types, "ActivityStart", None)
                    if start_cls is not None:
                        try:
                            await session.send_realtime_input(activity_start=start_cls())
                            print("[TITAN] 📡 activity_start")
                        except Exception as e:
                            print(f"[TITAN] ⚠️ activity_start: {e}")
                elif kind == "audio":
                    data = item.get("data")
                    if not data:
                        continue
                    await session.send_realtime_input(
                        audio=types.Blob(
                            data=data,
                            mime_type=_AUDIO_MIME,
                        )
                    )
                    self._user_audio_sent_at = time.monotonic()
                elif kind == "end":
                    # ESC / interrupt must NOT trigger a new Gemini reply
                    if self._drop_model_audio or self._interrupted:
                        print("[TITAN] 📡 skip audio_stream_end (interrupted)")
                        continue
                    now = time.monotonic()
                    if (now - self._last_stream_end) < _END_DEBOUNCE_S:
                        print("[TITAN] 📡 skip audio_stream_end (debounce)")
                        continue
                    end_cls = getattr(types, "ActivityEnd", None)
                    sent = False
                    if end_cls is not None:
                        try:
                            await session.send_realtime_input(activity_end=end_cls())
                            sent = True
                            print("[TITAN] 📡 activity_end")
                        except Exception as e:
                            print(f"[TITAN] ⚠️ activity_end: {e}")
                    if not sent:
                        await session.send_realtime_input(audio_stream_end=True)
                        print("[TITAN] 📡 audio_stream_end")
                    self._last_stream_end = now
                    self._vad_end_t = now
                    self._first_audio_logged = False
                    _dbg("SEND", "turn end (local VAD)")
            except Exception as e:
                print(f"[TITAN] ⚠️ send_realtime: {e}")

    async def _listen_audio(self):
        print("[TITAN] 🎤 Mic started")
        try:
            import numpy as np
        except Exception:
            np = None

        preroll: deque = deque(maxlen=_VAD_PREROLL)
        state = {"in_speech": False, "silence": 0, "voiced": 0, "started_at": 0.0}

        def _rms(indata) -> float:
            if np is None:
                return 0.0
            try:
                arr = indata.reshape(-1) if hasattr(indata, "reshape") else np.frombuffer(indata, dtype=np.int16)
                if arr.size == 0:
                    return 0.0
                return float(np.sqrt(np.mean(arr.astype(np.float32) ** 2)))
            except Exception:
                return 0.0

        def _reset_vad():
            state["in_speech"] = False
            state["silence"] = 0
            state["voiced"] = 0
            state["started_at"] = 0.0
            preroll.clear()

        def callback(indata, frames, time_info, status):
            with self._speaking_lock:
                titan_speaking = self._is_speaking

            if self.ui.muted or self._phone_active:
                return

            rms = _rms(indata)
            now = time.monotonic()

            echo_gate = (
                titan_speaking
                or (now - self._speak_ended_at) < _ECHO_TAIL_S
                or now < self._vad_suppress_until
            )
            if echo_gate:
                # Never count speaker bleed as "user just spoke"
                if state["in_speech"] and state.get("voiced", 0) >= _VAD_MIN_SPEECH:
                    started = state.get("started_at") or 0.0
                    if started and started < (self._speak_started_at or now):
                        self._qput_audio({"kind": "end"})
                        print("[TITAN] 🎤 speech end (Titan started talking)")
                _reset_vad()
                return

            # Talking is for the BOSS. It must NOT auto-kill the worker.
            # Only echo (Titan's own speaker) is gated. Hello / stop / pause
            # go to Gemini; the boss then calls job_board stop|pause|go_ahead.

            if rms >= _VAD_START_RMS:
                self._last_user_speech = now

            data = indata.tobytes()
            packet = {"kind": "audio", "data": data, "rms": rms}

            if not state["in_speech"]:
                preroll.append(packet)
                if rms >= _VAD_START_RMS:
                    state["in_speech"] = True
                    state["silence"] = 0
                    state["voiced"] = 1
                    state["started_at"] = now
                    # New real utterance — allow Gemini audio again
                    self._interrupted = False
                    self._drop_model_audio = False
                    _dbg("VAD", f"speech start RMS={rms:.0f}")
                    print(f"[TITAN] 🎤 speech start RMS={rms:.0f}")
                    self._qput_audio({"kind": "activity_start"})
                    for p in preroll:
                        self._qput_audio(p)
                    preroll.clear()
            else:
                self._qput_audio(packet)
                if rms >= _VAD_HOLD_RMS:
                    state["voiced"] = state.get("voiced", 0) + 1
                    state["silence"] = 0
                else:
                    state["silence"] += 1
                    if (
                        state["silence"] >= _VAD_END_SILENCE
                        and state.get("voiced", 0) >= _VAD_MIN_SPEECH
                    ):
                        self._qput_audio({"kind": "end"})
                        _reset_vad()
                        _dbg("VAD", "speech end")
                        print("[TITAN] 🎤 speech end")
                    elif state["silence"] >= _VAD_END_SILENCE:
                        # Click / echo / short noise — close open activity turn
                        self._qput_audio({"kind": "end"})
                        _reset_vad()

        try:
            in_device = audio_devices.resolve(get_input_device(), "input")
            with sd.InputStream(
                samplerate=SEND_SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
                blocksize=CHUNK_SIZE,
                device=in_device,
                callback=callback,
            ):
                print("[TITAN] 🎤 Mic stream open")
                while True:
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[TITAN] ❌ Mic: {e}")
            raise

    async def _receive_audio(self):
        print("[TITAN] 👂 Recv started")
        out_buf, in_buf = [], []

        try:
            while True:
                async for response in self.session.receive():

                    if response.data:
                        if self._drop_model_audio or self._mute_brain_filler:
                            continue
                        # Gate the mic the instant audio arrives — don't wait
                        # for the play loop, or speaker echo (RMS 3000+) becomes "user speech".
                        self.set_speaking(True)
                        if self._vad_end_t and not self._first_audio_logged:
                            dt = time.monotonic() - self._vad_end_t
                            print(f"[TITAN] ⚡ first audio in {dt:.2f}s")
                            self._first_audio_logged = True
                            self._vad_end_t = 0.0
                        if self._turn_done_event and self._turn_done_event.is_set():
                            self._turn_done_event.clear()
                        _audio_data = response.data
                        _SLICE = 2400
                        for _i in range(0, len(_audio_data), _SLICE):
                            self.audio_in_queue.put_nowait(_audio_data[_i : _i + _SLICE])

                    if response.server_content:
                        sc = response.server_content

                        # Server barge-in is almost always Titan's own speaker.
                        # Only honour it if we actually sent USER mic recently.
                        if getattr(sc, "interrupted", False):
                            heard_user = (time.monotonic() - self._user_audio_sent_at) < 1.6
                            with self._speaking_lock:
                                is_spk = self._is_speaking
                            if heard_user and not is_spk:
                                _dbg("RECV", "✋ Gemini barge-in signal received")
                                print("[TITAN] ✋ Gemini Live detected user barge-in — stopping speech")
                                self.interrupt()
                            else:
                                print("[TITAN] 🔇 ignore barge-in (echo / Titan still speaking)")

                        if sc.output_transcription and sc.output_transcription.text and not self._mute_brain_filler:
                            txt = _clean_transcript(sc.output_transcription.text)
                            if txt and txt != (out_buf[-1] if out_buf else ""):
                                out_buf.append(txt)
                                _dbg("RECV", f"TITAN says: '{txt[:60]}'")

                        if sc.input_transcription and sc.input_transcription.text:
                            txt = _clean_transcript(sc.input_transcription.text)
                            if txt:
                                with self._speaking_lock:
                                    is_spk = self._is_speaking
                                if is_spk or (time.monotonic() - self._speak_ended_at) < _ECHO_TAIL_S:
                                    print(f"[TITAN] 🔇 ignore heard-while-speaking (echo): '{txt[:40]}'")
                                else:
                                    _dbg("RECV", f"👤 Gemini heard you say: '{txt}'")
                                    if self._looks_like_noise(txt):
                                        # Streaming transcription can emit one broken character
                                        # before the real sentence. Drop it silently.
                                        pass
                                    else:
                                        in_buf.append(txt)
                                        self._last_user_speech = time.monotonic()

                        if sc.turn_complete:
                            # ESC drops audio for the current turn only. Re-arm it at the
                            # server turn boundary so a short/quiet next command can speak.
                            if self._interrupted or self._drop_model_audio:
                                self._interrupted = False
                                self._drop_model_audio = False
                            if self._turn_done_event:
                                self._turn_done_event.set()

                            # Re-arm muting exactly here — this turn_complete is
                            # for the [SPEAK_NOW] answer we just finished playing,
                            # so it's now safe to mute Gemini's next raw-speech
                            # filler again without cutting off the real answer.
                            if self._expect_brain_turn_complete:
                                self._expect_brain_turn_complete = False
                                self._mute_brain_filler = True

                            full_in = " ".join(in_buf).strip()
                            if full_in and not self._looks_like_noise(full_in):
                                self._last_user_request = full_in
                                self._last_user_request_at = time.monotonic()
                                self._live_turn_delegated = False
                                self.ui.write_log(f"You: {full_in}")
                                self._session_log.append(f"User: {full_in}")
                                if self._dashboard:
                                    asyncio.create_task(self._dashboard.broadcast({
                                        "type": "log", "speaker": "user",
                                        "text": full_in,
                                        "ts": datetime.now().isoformat(),
                                    }))
                                # Full-brain mode: Gemini has no tools and was told to
                                # stay silent on raw speech — NVIDIA does the actual
                                # planning/tool work, then we hand its answer back to
                                # Gemini (as [SPEAK_NOW]) to voice. Don't trigger this
                                # for our own injected [SPEAK_NOW] echoes.
                                if getattr(self, "_full_brain", False) and not full_in.startswith("[SPEAK_NOW]"):
                                    asyncio.create_task(self._run_full_brain_turn(full_in))
                                # NOTE: the old `elif self._pending_live_skill:` rescue
                                # branch lived here. It started a worker using THIS
                                # transcript for a load_skill call made during a PREVIOUS
                                # one, so a one-word interjection became the task. The
                                # boss now hands off explicitly via start_task_worker
                                # with the full request text instead.
                            in_buf = []

                            full_out = " ".join(out_buf).strip()
                            if full_out:
                                self.ui.write_log(f"{self._asst_name}: {full_out}")
                                self._session_log.append(f"{self._asst_name}: {full_out}")
                                if self._dashboard:
                                    asyncio.create_task(self._dashboard.broadcast({
                                        "type": "log", "speaker": "titan",
                                        "text": full_out,
                                        "ts": datetime.now().isoformat(),
                                    }))
                            out_buf = []

                            # Vision injection: model finished tool-response turn → now send the image
                            if self._pending_vision and self.session:
                                from google.genai import types as _gtypes
                                img_b, mime_t, question, angle = self._pending_vision
                                self._pending_vision = None
                                print(f"[Vision] 📤 {len(img_b):,} bytes (angle={angle}) → main session")
                                img_part = _gtypes.Part.from_bytes(data=img_b, mime_type=mime_t)
                                text_part = _gtypes.Part.from_text(text=question) if isinstance(question, str) else question
                                await self.session.send_client_content(
                                    turns={"parts": [img_part, text_part]},
                                    turn_complete=True,
                                )
                                # Mark next turn_complete behaviour depending on angle
                                if self._vision_cam_active:
                                    # Camera: keep busy until TITAN finishes speaking the answer
                                    self._vision_cam_active    = False
                                    self._vision_close_pending = True
                                else:
                                    # Screen-only: no camera to close; release busy flag now
                                    self._vision_busy = False
                            elif self._vision_close_pending:
                                # This turn_complete IS the vision answer — close camera + release busy flag
                                self._vision_close_pending = False
                                self._vision_busy = False
                                async def _cam_close():
                                    await asyncio.sleep(2.0)
                                    self.ui.stop_camera_stream()
                                asyncio.create_task(_cam_close())

                    if response.tool_call:
                        # Do NOT block the receive loop — that stalls the
                        # websocket, backs up mic send, and causes 1011 errors.
                        asyncio.create_task(self._dispatch_tools(response.tool_call))
        except Exception as e:
            print(f"[TITAN] ❌ Recv: {e}")
            traceback.print_exc()
            raise

    async def _play_audio(self):
        print("[TITAN] 🔊 Play started")

        out_device = audio_devices.resolve(get_output_device(), "output")
        stream = sd.RawOutputStream(
            samplerate=RECEIVE_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
            device=out_device,
        )
        stream.start()
        self._play_stream = stream

        try:
            while True:
                try:
                    chunk = await asyncio.wait_for(
                        self.audio_in_queue.get(),
                        timeout=0.1
                    )
                except asyncio.TimeoutError:
                    if (
                        self._turn_done_event
                        and self._turn_done_event.is_set()
                        and self.audio_in_queue.empty()
                    ):
                        self.set_speaking(False)
                        self._turn_done_event.clear()
                    continue

                if self._interrupted or self._drop_model_audio:
                    # Discard anything still in the play queue
                    q = self.audio_in_queue
                    if q:
                        while True:
                            try:
                                q.get_nowait()
                            except Exception:
                                break
                    self.set_speaking(False)
                    continue

                self.set_speaking(True)

                # ~80 ms batches so ESC stops the speaker quickly
                batch = bytearray(chunk)
                while len(batch) < 3840:
                    try:
                        batch.extend(self.audio_in_queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break

                if self._interrupted or self._drop_model_audio:
                    self.set_speaking(False)
                    continue

                try:
                    if stream.stopped:
                        try:
                            stream.start()
                        except Exception:
                            pass
                    await asyncio.to_thread(stream.write, bytes(batch))
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    err = str(e)
                    # The Python executor is already going away (normally
                    # because the Qt application is closing).  Retrying only
                    # produces a stream of identical errors against a dead UI.
                    if "cannot schedule new futures after shutdown" in err.lower():
                        break
                    if "stopped" in err.lower() or "-9983" in err:
                        try:
                            stream.start()
                        except Exception:
                            pass
                        self.set_speaking(False)
                        continue
                    print(f"[TITAN] ⚠️ play write: {err[:120]}")
                    self.set_speaking(False)
                    continue
        except Exception as e:
            print(f"[TITAN] ❌ Play: {e}")
            # Never crash the whole session because the speaker hiccuped
            await asyncio.sleep(0.2)
        finally:
            self._play_stream = None
            self.set_speaking(False)
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass

    # ── Morning briefing ────────────────────────────────────────────────────────

    async def _send_startup_briefing(self) -> None:
        """
        Two-phase briefing optimized for speed:
          Phase 1 — instant greeting (no tools) → speech starts in <1s
          Phase 2 — news pre-fetched in a background thread while Phase 1 plays,
                    delivered as ready text (no Gemini tool-call round-trip) and
                    shown on the UI content panel. Waits for turn_complete event
                    instead of a fixed sleep so there is no unnecessary gap.
        """
        memory   = load_memory()
        identity = memory.get("identity", {})

        def _val(k: str) -> str:
            e = identity.get(k, {})
            return (e.get("value", "") if isinstance(e, dict) else str(e)).strip()

        lang = _val("language")
        name = _val("name")
        time_str = datetime.now().strftime("%H:%M")

        # Start fetching news immediately — runs in parallel while phase 1 plays
        loop = asyncio.get_event_loop()
        news_future = loop.run_in_executor(None, _fetch_news_sync, "top world news today")

        await asyncio.sleep(0.3)
        if not self.session:
            return

        # ── Phase 1: instant greeting ─────────────────────────────────────────
        lang_clause = f" Respond in {lang}." if lang else ""
        name_clause = f" Address the user as {name}." if name else ""

        # Inject last session context if available — pop removes it so it's never repeated
        last = await asyncio.to_thread(pop_last_session)
        session_clause = ""
        if last:
            try:
                _delta = (datetime.now() - datetime.strptime(last["date"], "%Y-%m-%d")).days
                _when  = "earlier today" if _delta == 0 else ("yesterday" if _delta == 1 else f"{_delta} days ago")
            except Exception:
                _when = "last time"
            session_clause = (
                f" Also briefly and naturally mention that {_when}: {last['summary']}"
            )

        # Ask only. Do NOT start the job. Auto-start was the task-loop bug.
        pending_clause = ""
        try:
            pad = load_pad()
            open_jobs = [j for j in (pad.get("jobs") or []) if j.get("status") in ("active", "paused")]
            if open_jobs:
                j = open_jobs[0]
                nxt = _next_step(j)
                step_txt = f" Next step would be: {nxt.get('text')}." if nxt else ""
                pending_clause = (
                    f" Also briefly ASK if they want you to continue the unfinished job "
                    f"'{j.get('title') or j.get('id')}'.{step_txt} "
                    f"Do not start it. Do not call any tools for it."
                )
        except Exception:
            pass

        p1 = (
            f"Greet the user warmly, mention it is {time_str}, and say you are fetching today's news now.{session_clause}{pending_clause} "
            f"Keep it to 3 short sentences max. Do not call any tools.{lang_clause}{name_clause}"
        )

        # Clear the turn-done event so we can wait for Phase 1 to finish
        if self._turn_done_event:
            self._turn_done_event.clear()

        await self.session.send_client_content(
            turns={"parts": [{"text": p1}]},
            turn_complete=True,
        )
        self.ui.write_log("SYS: Briefing phase 1 (greeting) sent.")

        # ── Phase 2: fire as soon as Phase 1 audio is done ───────────────────
        async def _deliver_news():
            try:
                lang_str = f" Respond in {lang}." if lang else ""

                # Wait for news fetch (already running) and Phase 1 turn-complete
                # in parallel — whichever takes longer determines the wait time
                news_done   = asyncio.wrap_future(news_future)
                turn_waited = False
                if self._turn_done_event:
                    try:
                        await asyncio.wait_for(self._turn_done_event.wait(), timeout=6.0)
                        turn_waited = True
                    except asyncio.TimeoutError:
                        pass

                # Extra buffer: turn_complete fires when Gemini finishes *generating*
                # Phase 1, but audio may still be playing.  Waiting a beat here
                # prevents Phase 2 audio from arriving while Phase 1 is mid-sentence
                # (which sounds like a "repeated first response" to the user).
                if turn_waited:
                    await asyncio.sleep(0.8)
                else:
                    await asyncio.sleep(1.0)

                try:
                    news_text = await asyncio.wait_for(news_done, timeout=4.0)
                except Exception:
                    news_text = ""

                if not self.session or kind == "progress":
                    return

                if news_text and len(news_text) > 60:
                    # Show on UI content panel immediately
                    self.ui.show_content("NEWS — top world news today", news_text)

                    p2 = (
                        f"[BRIEFING] Here are today's top news headlines:\n{news_text}\n\n"
                        "Pick ONE headline, summarise it in one sentence, then say the full list "
                        f"is displayed on screen. Do not call any tools.{lang_str}"
                    )
                else:
                    p2 = (
                        "News headlines could not be fetched right now. "
                        f"Let the user know briefly.{lang_str}"
                    )

                await self.session.send_client_content(
                    turns={"parts": [{"text": p2}]},
                    turn_complete=True,
                )
                self.ui.write_log("SYS: Briefing phase 2 (news) sent.")
            except Exception as e:
                print(f"[Briefing] Phase 2 error: {e}")
                self.ui.write_log(f"SYS: Briefing phase 2 failed: {e}")

        asyncio.create_task(_deliver_news())

    # ── Session memory ──────────────────────────────────────────────────────────

    async def _save_session_summary(self) -> None:
        """Summarise the current session in 1-2 sentences and save to long_term.json."""
        log = self._session_log
        if len(log) < 3:          # need at least one exchange to be worth saving
            return
        self._session_log = []    # reset immediately so the next session starts clean

        memory = load_memory()
        lang_entry = memory.get("identity", {}).get("language", {})
        lang = (lang_entry.get("value", "") if isinstance(lang_entry, dict) else str(lang_entry)).strip()
        lang = lang or "English"

        convo = "\n".join(log[-40:])   # cap at last 40 turns to stay within token budget
        prompt = (
            f"Summarize this conversation in 1-2 sentences in {lang}. "
            "Focus on what the user accomplished or discussed. "
            "Output ONLY the summary text, nothing else:\n\n" + convo
        )
        try:
            from google import genai as _genai
            client = _genai.Client(api_key=_get_api_key())
            resp   = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
            )
            summary = (resp.text or "").strip()
            if summary:
                save_session_summary(summary, lang)
        except Exception as e:
            print(f"[Memory] ⚠️ Session summary failed: {e}")

    # ── System monitor ──────────────────────────────────────────────────────────

    async def _run_system_monitor(self) -> None:
        """Background task: records hardware alerts without interrupting voice."""
        while True:
            await asyncio.sleep(30)
            alert = await asyncio.to_thread(self._sys_monitor.check)
            if not alert:
                continue
            try:
                self.ui.write_log(f"SYS: {str(alert)[:160]}")
            except Exception:
                pass

            # Hardware warnings stay in the log. Injecting them as a new
            # model turn can cut across voice playback and user commands.
            continue

            if not self.session:
                continue
            with self._speaking_lock:
                speaking = self._is_speaking
            recent = (time.monotonic() - getattr(self, "_last_user_speech", 0.0)) < 45
            if speaking or recent or self._tool_busy:
                continue

            # RAM / memory alerts: log only. Do not make Titan talk.
            a = str(alert).upper()
            if "RAM" in a or "MEMORY" in a or "SYSTEM_ALERT" in a or "रैम" in str(alert):
                continue

            try:
                await self.session.send_client_content(
                    turns={"parts": [{"text": alert}]},
                    turn_complete=True,
                )
            except Exception as e:
                print(f"[Monitor] ⚠️ Could not send alert: {e}")

    # ── Background monitor ──────────────────────────────────────────────────────

    async def _run_background_monitor(self) -> None:
        """Check user-configured topics once per day; speak alerts when new headlines appear."""
        await asyncio.sleep(300)          # wait 5 min after startup before first check
        while True:
            if self.session:
                # Don't interrupt if user spoke recently or TITAN is mid-sentence
                with self._speaking_lock:
                    speaking = self._is_speaking
                recent_speech = (time.monotonic() - self._last_user_speech) < 30
                if not speaking and not recent_speech and not self._tool_busy:
                    try:
                        alerts = await asyncio.to_thread(monitor_check_all)
                        memory = load_memory()
                        lang_e = memory.get("identity", {}).get("language", {})
                        lang   = (lang_e.get("value", "") if isinstance(lang_e, dict) else str(lang_e)).strip() or "English"
                        for alert in alerts:
                            msg = (
                                f"{alert}\n\n"
                                f"Inform the user about this development naturally in {lang}. "
                                "One brief sentence only."
                            )
                            await self.session.send_client_content(
                                turns={"parts": [{"text": msg}]},
                                turn_complete=True,
                            )
                            self.ui.write_log(f"SYS: Monitor alert sent.")
                            await asyncio.sleep(6)   # gap between consecutive alerts
                    except Exception as e:
                        print(f"[Monitor] ⚠️ Background check error: {e}")
            await asyncio.sleep(1800)     # check every 30 minutes

    # ── Proactive mode ──────────────────────────────────────────────────────────


    async def _watch_worker(self) -> None:
        """Boss inbox: worker events appear on screen; done/failed notify the model."""
        while True:
            await asyncio.sleep(0.45)
            try:
                events = await task_workers.pop_events()
            except Exception:
                events = []
            if not events:
                continue
            for ev in events:
                kind = ev.get("kind")
                worker = ev.get("worker") or {}
                did = worker.get("task") or ""
                report = worker.get("result") or worker.get("error") or ""
                if kind == "progress":
                    self.ui.write_log(f"SYS: [Worker {worker.get('id', '')}] running {ev.get('tool', '')}")
                    continue
                elif kind == "state":
                    self.ui.write_log(f"SYS: [Worker {worker.get('id', '')}] {ev.get('message', '')}")
                    continue
                elif kind == "tool_result":
                    self.ui.write_log(f"SYS: [Worker {worker.get('id', '')}] {ev.get('tool', '')} finished")
                    continue
                elif kind == "question":
                    # The worker is blocked. Make the boss speak the question,
                    # then relay the user's reply via answer_worker_question.
                    wid = worker.get("id", "")
                    q = ev.get("question", "")
                    opts = ev.get("options") or []
                    self.ui.write_log(f"SYS: [Worker {wid}] asks: {q}")
                    if not self.session:
                        continue
                    opt_txt = f" Options: {', '.join(str(o) for o in opts)}." if opts else ""
                    msg = (
                        f"[WORKER_QUESTION] Worker {wid} is blocked and needs one decision "
                        f"from the user. Ask the user this, briefly and in their language: "
                        f"\"{q}\".{opt_txt} When they reply, immediately call "
                        f"answer_worker_question with worker_id='{wid}' and their answer. "
                        "Do not attempt the task yourself."
                    )
                    try:
                        await self.session.send_client_content(
                            turns={"parts": [{"text": msg}]}, turn_complete=True,
                        )
                    except Exception as e:
                        print(f"[WORKER] inject question: {e}")
                    continue
                # completed/failed/interrupted: show the ACTUAL outcome (result
                # or error), not the original task text. Logging `did` here
                # (the old code) meant every failure just re-printed what you
                # asked for, with zero information about why it failed.
                try:
                    label = report if report else did[:140]
                    self.ui.write_log(f"SYS: [Worker] {kind} — {label[:200]}")
                except Exception:
                    pass

                if not self.session:
                    continue

                if kind == "completed":
                    msg = (
                        f"[WORKER_EVENT] Task finished: {did}. Worker report: {report}. "
                        "Inform the user truthfully in one brief sentence; do not add claims beyond the report."
                    )
                    try:
                        await self.session.send_client_content(
                            turns={"parts": [{"text": msg}]},
                            turn_complete=True,
                        )
                    except Exception as e:
                        print(f"[WORKER] inject done: {e}")
                elif kind == "failed":
                    msg = f"[WORKER_EVENT] Task failed: {did}. Worker error: {report}. Inform the user truthfully in one brief sentence."
                    try:
                        await self.session.send_client_content(
                            turns={"parts": [{"text": msg}]},
                            turn_complete=True,
                        )
                    except Exception as e:
                        print(f"[WORKER] inject failed: {e}")
                elif kind == "interrupted":
                    msg = f"[WORKER_EVENT] Task stopped: {did}. Tell the user it was interrupted and did not finish."
                    try:
                        await self.session.send_client_content(
                            turns={"parts": [{"text": msg}]},
                            turn_complete=True,
                        )
                    except Exception as e:
                        print(f"[WORKER] inject interrupted: {e}")

    async def _run_proactive_mode(self) -> None:
        """
        Background task: periodically checks if the user has been silent long enough,
        then hands time + memory context to Gemini so it can decide what (if anything)
        to say proactively. No hardcoded rules — Gemini makes the call.
        """
        while True:
            await asyncio.sleep(60)   # evaluate once per minute

            if not self.session:
                continue

            with self._speaking_lock:
                speaking = self._is_speaking
            if speaking or self._tool_busy:
                continue

            if not self._proactive.should_trigger(self._last_user_speech):
                continue

            self._proactive.mark_triggered()

            try:
                memory       = await asyncio.to_thread(load_memory)
                monitors     = await asyncio.to_thread(list_monitors)
                recent_turns = self._session_log[-8:] if self._session_log else []
                prompt = self._proactive.build_prompt(
                    memory       = memory,
                    monitors     = monitors or None,
                    recent_turns = recent_turns or None,
                )
                await self.session.send_client_content(
                    turns={"parts": [{"text": prompt}]},
                    turn_complete=True,
                )
                self.ui.write_log("SYS: Proactive check-in.")
            except Exception as e:
                print(f"[Proactive] ⚠️ {e}")

    # ── Phone audio relay ────────────────────────────────────────────────────────

    async def _relay_phone_audio(self) -> None:
        """Forward phone mic PCM chunks from dashboard queue into the Gemini Live session."""
        q = self._dashboard._phone_audio_queue
        while True:
            try:
                chunk = await asyncio.wait_for(q.get(), timeout=1.0)
            except asyncio.TimeoutError:
                # No audio for 1 s → phone mic inactive, give PC mic back
                self._phone_active = False
                continue
            self._phone_active = True   # phone is streaming — silence PC mic
            with self._speaking_lock:
                speaking = self._is_speaking
            if speaking or self.ui.muted:
                continue
            if isinstance(chunk, dict) and chunk.get("data"):
                data = chunk["data"]
            elif isinstance(chunk, (bytes, bytearray)):
                data = bytes(chunk)
            else:
                continue
            if self._tool_busy:
                try:
                    self._on_midtask_chunk(bytes(data), 999.0)
                except Exception:
                    pass
                continue
            self._qput_audio({"kind": "audio", "data": data, "rms": 999.0})

    def _on_phone_connected(self) -> None:
        self.ui.write_log("SYS: Phone connected via Remote Dashboard.")
        self.ui.notify_phone_connected()

    # ── dashboard command relay ─────────────────────────────────────────────

    async def _process_dashboard_commands(self) -> None:
        while True:
            try:
                text = await asyncio.wait_for(
                    self._dashboard._command_queue.get(), timeout=0.5
                )
                if not text:
                    continue
                # Wait up to 8s for session to become ready after a wake
                for _ in range(80):
                    if self.session:
                        break
                    await asyncio.sleep(0.1)
                if self.session:
                    await self.session.send_client_content(
                        turns={"parts": [{"text": text}]},
                        turn_complete=True,
                    )
                    self.ui.write_log(f"[Web]: {text}")
                else:
                    print(f"[Dashboard] Dropped command (no session): {text}")
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                print(f"[Dashboard] Command error: {e}")
                await asyncio.sleep(0.5)

    # ── main loop ───────────────────────────────────────────────────────────

    async def run(self):
        self._loop = asyncio.get_event_loop()

        # Start dashboard (optional — needs: pip install fastapi "uvicorn[standard]" cryptography)
        try:
            from dashboard.server import DashboardServer
            self._dashboard = DashboardServer()
            self._dashboard.set_connect_callback(self._on_phone_connected)
            asyncio.create_task(self._dashboard.serve())
            # Runs for the whole lifetime, not just inside an active session
            asyncio.create_task(self._process_dashboard_commands())
        except Exception as e:
            print(f"[Dashboard] Disabled: {e}")
            self._dashboard = None

        # Start ShadowBridge for Chrome extension
        try:
            import socket
            _port_free = False
            try:
                with socket.create_connection(("127.0.0.1", 8002), timeout=0.3):
                    print("[ShadowBridge] Port 8002 already in use — reusing existing bridge")
            except (ConnectionRefusedError, OSError):
                _port_free = True

            if _port_free:
                local_bridge = Path(__file__).resolve().parent / "shadow_bridge.py"
                if not local_bridge.exists():
                    shadow_dir = Path(__file__).resolve().parent.parent
                    if str(shadow_dir) not in sys.path:
                        sys.path.insert(0, str(shadow_dir))
                from shadow_bridge import ShadowBridge
                self._shadow_bridge = ShadowBridge()
                asyncio.create_task(self._shadow_bridge.start())
            else:
                self._shadow_bridge = None
        except Exception as e:
            print(f"[ShadowBridge] Disabled: {e}")
            self._shadow_bridge = None

        while True:
            try:
                print("[TITAN] Connecting...")
                self.ui.set_state("THINKING")
                config = self._build_config()

                # Fresh client on every reconnect — avoids stale HTTP session state
                client = genai.Client(
                    api_key=_get_api_key(),
                    http_options={"api_version": "v1beta"}
                )

                async with (
                    client.aio.live.connect(model=_get_live_model(), config=config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    self.session          = session
                    self.audio_in_queue   = asyncio.Queue()
                    self.out_queue        = asyncio.Queue(maxsize=_SEND_QUEUE_MAX)
                    self._turn_done_event = asyncio.Event()
                    self._tool_lock       = asyncio.Lock()
                    self._tool_busy       = False

                    # Reset transient state that must not carry over from a previous session
                    self._pending_vision       = None
                    self._vision_cam_active    = False
                    self._vision_close_pending = False
                    self._vision_busy          = False
                    self._vision_last_time     = 0.0
                    self._interrupted          = False
                    self._vad_end_t            = 0.0
                    self._first_audio_logged   = False
                    self._interrupted          = False
                    self._drop_model_audio     = False
                    self._vad_suppress_until   = 0.0
                    self._last_stream_end      = 0.0
                    self._user_audio_sent_at   = 0.0
                    self._speak_started_at     = 0.0
                    self._pending_midtask      = b""
                    self._reset_midtask()
                    try:
                        from task_control import clear_cancel
                        clear_cancel()
                    except Exception:
                        pass

                    print("[TITAN] Connected.")
                    self.ui.set_state("LISTENING")
                    self.ui.write_log("SYS: TITAN online.")

                    if self._dashboard:
                        await self._dashboard.broadcast({"type": "status", "state": "active"})

                    tg.create_task(self._send_realtime())
                    tg.create_task(self._listen_audio())
                    tg.create_task(self._receive_audio())
                    tg.create_task(self._play_audio())
                    tg.create_task(self._run_system_monitor())
                    tg.create_task(self._run_background_monitor())
                    tg.create_task(self._run_proactive_mode())
                    tg.create_task(self._watch_worker())
                    if self._dashboard:
                        tg.create_task(self._relay_phone_audio())

                    # Morning briefing — fires once per process launch (if enabled)
                    if not self._briefing_sent and get_brief_enabled():
                        self._briefing_sent = True
                        tg.create_task(self._send_startup_briefing())

            except KeyboardInterrupt:
                raise
            except SystemExit:
                raise
            except BaseException as e:
                # Catches both Exception and BaseExceptionGroup (Python 3.11+
                # TaskGroup raises BaseExceptionGroup when tasks are cancelled
                # externally, which `except Exception` would miss, letting the
                # exception escape the while-loop and causing asyncio.run() to
                # start shutdown — resulting in "executor after shutdown" errors).
                err_str = str(e)
                # Network / server timeout errors — log cleanly without dumping full stack trace
                is_net_err = any(k in err_str for k in (
                    "TimeoutError", "timed out", "getaddrinfo", "CancelledError",
                    "ConnectionRefusedError", "OSError", "Cannot connect",
                    "1011", "1007", "1006", "1000", "Internal error", "ConnectionClosedError", "APIError",
                ))

                # Auto-rotate model on audio content type rejection
                if "CONTENT_TYPE_AUDIO" in err_str or "not supported for this model" in err_str:
                    _rotate_live_model()
                    self._conn_backoff = 3  # Reset backoff for new model

                print(f"[TITAN] Exception ({type(e).__name__}): {e}")
                if not is_net_err:
                    traceback.print_exc()
                if is_net_err:
                    _conn_backoff = min(getattr(self, "_conn_backoff", 3) * 2, 60)
                    self._conn_backoff = _conn_backoff
                    self.ui.write_log(
                        f"NET: Bağlantı kurulamadı — {_conn_backoff}s sonra tekrar deneniyor. "
                        "(VPN gerekiyor olabilir)"
                    )
                else:
                    self._conn_backoff = 3
            finally:
                self.session = None
                # Only save if there was a real conversation (≥3 turns)
                if len(self._session_log) >= 3:
                    asyncio.create_task(self._save_session_summary())

            self.set_speaking(False)
            self.ui.set_state("SLEEPING")

            if self._dashboard:
                await self._dashboard.broadcast({"type": "status", "state": "sleeping"})

            delay = getattr(self, "_conn_backoff", 3)
            print(f"[TITAN] Reconnecting in {delay}s...")
            await asyncio.sleep(delay)

def main():
    ui = TitanUI("face.png")

    # Wire the confirmation gate to the HUD (thread-safe show/hide/log callbacks).
    # Nothing here blocks — see core/confirm.py.
    confirm.bind(ui.show_confirm_banner, ui.hide_confirm_banner, ui.write_log)

    # Tell audio_devices which sample rates the streams actually use, then warm
    # its device-list cache on a background thread so the first "what mics do
    # I have" question doesn't stall on sd.query_devices().
    audio_devices.configure(SEND_SAMPLE_RATE, RECEIVE_SAMPLE_RATE)
    audio_devices.prefetch()

    def runner():
        ui.wait_for_api_key()

        # ── STARTUP AUTHENTICATION GATE ──
        sec_cfg = get_sec_config()
        # Startup gate ONLY runs if Master Security Lock is explicitly turned ON!
        if sec_cfg.get("security_lock", False) and sec_cfg.get("startup_gate", False):
            # Skip lock screen if nothing is enrolled yet
            if not sec_cfg.get("voice_enrolled") and not sec_cfg.get("face_enrolled") and not sec_cfg.get("pin_hash"):
                print("[Security] 🔓 No security enrolled yet — passing through startup gate.")
            else:
                print("[Security] 🔒 Startup gate active — authenticating owner...")
                ui.write_log("[Security] 🔒 Lock screen active — authentication required.")

                authenticated = ui.show_lock_screen_dialog()

                if not authenticated:
                    print("[Security] ⛔ Authentication cancelled or failed — exiting TITAN.")
                    sys.exit(0)
                else:
                    print("[Security] ✅ Owner authenticated — starting TITAN.")
                    ui.write_log("[Security] ✅ Identity verified. TITAN online.")

        titan = TitanLive(ui)
        try:
            asyncio.run(titan.run())
        except KeyboardInterrupt:
            print("\n🔴 Shutting down...")

    threading.Thread(target=runner, daemon=True).start()
    ui.root.mainloop()

if __name__ == "__main__":
    main()