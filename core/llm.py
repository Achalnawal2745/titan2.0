"""
core/llm.py — Multi-Model Text & Code Generation for TITAN.

Dual-Brain Architecture:
1. Gemini Flash / Live: Instant low-latency conversation & text.
2. NVIDIA NIM (meta/llama-3.3-70b-instruct / nemotron-70b): Deep coding, structured slide/doc design & heavy tasks.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

_client = None
_API_KEYS_PATH = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"

DEFAULT_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"


# Active flagship models on NVIDIA NIM:
# nvidia/nemotron-3-super-120b-a12b: 120B MoE flagship with high accuracy tool-calling
# nvidia/nemotron-3-ultra-550b-a55b: 550B flagship fallback
# nvidia/nemotron-3-nano-30b-a3b: 30B high-speed fallback
NVIDIA_MODEL = "nvidia/nemotron-3-super-120b-a12b"
NVIDIA_FALLBACK_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
NVIDIA_FALLBACK_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b",
    "nvidia/nemotron-3-nano-30b-a3b",
    "meta/llama-3.2-11b-vision-instruct",
]
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


def _get_api_key() -> str:
    try:
        cfg = json.loads(_API_KEYS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError(f"Missing {_API_KEYS_PATH} — cannot reach Gemini.")
    key = cfg.get("gemini_api_key")
    if not key:
        raise RuntimeError("config/api_keys.json has no 'gemini_api_key'.")
    return key


def _get_nvidia_api_key() -> str:
    try:
        cfg = json.loads(_API_KEYS_PATH.read_text(encoding="utf-8"))
        return cfg.get("nvidia_api_key", "")
    except Exception:
        return ""


def get_client():
    """Lazily-built, process-wide genai.Client."""
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=_get_api_key())
    return _client


def reset_client() -> None:
    global _client
    _client = None


def _is_rate_limit(err: Exception) -> bool:
    s = str(err).lower()
    return "429" in s or "rate" in s or "quota" in s or "resource_exhausted" in s


def generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_retries: int = 3,
    system_instruction: str | None = None,
) -> str:
    """Single text-generation call using Gemini."""
    client = get_client()
    last_err: Exception | None = None
    models_to_try = [model] + ([FALLBACK_MODEL] if model != FALLBACK_MODEL else [])

    for attempt_model in models_to_try:
        for attempt in range(max_retries):
            try:
                config = {"temperature": temperature}
                if system_instruction:
                    config["system_instruction"] = system_instruction
                resp = client.models.generate_content(
                    model=attempt_model,
                    contents=prompt,
                    config=config,
                )
                text = getattr(resp, "text", None)
                if text:
                    return text
                last_err = RuntimeError(f"Empty response from {attempt_model}")
            except Exception as e:
                last_err = e
                if _is_rate_limit(e):
                    time.sleep(2 ** attempt)
                    continue
                break

    raise RuntimeError(f"Gemini generation failed after retries: {last_err}")


def generate_nvidia(
    prompt: str,
    model: str = NVIDIA_MODEL,
    system_prompt: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    timeout: int = 45,
) -> str:
    """
    Generates high-grade code & structured documents using NVIDIA NIM (Llama 3.3 70B / Nemotron)
    with seamless automatic fallback to Gemini if offline.
    """
    api_key = _get_nvidia_api_key()
    if not api_key:
        return generate(prompt, system_instruction=system_prompt, temperature=temperature)

    import requests
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    for m in [model, NVIDIA_FALLBACK_MODEL]:
        try:
            payload = {
                "model": m,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            r = requests.post(f"{NVIDIA_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                content = data["choices"][0]["message"]["content"]
                if content and content.strip():
                    return content
        except Exception:
            continue

    # Resilient fallback to Gemini
    return generate(prompt, system_instruction=system_prompt, temperature=temperature)


def generate_json(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.2) -> dict:
    """Strips ```json fences and parses the result."""
    raw = generate(prompt, model=model, temperature=temperature)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nRaw: {raw[:500]}")