"""
core/nvidia_brain.py — "Full Brain" mode: NVIDIA NIM decides every tool call.

In this mode Gemini Live is demoted to voice I/O only (STT in, TTS out) —
see main.py's _build_config(), which drops `tools=` from the Live session
and swaps in a "silent relay" system_instruction when full-brain mode is on.

Flow per user turn:
  1. main.py gets the final transcribed user utterance (`full_in`) from
     Gemini Live's input_transcription at turn_complete.
  2. That text is handed to `run_brain_turn()` here.
  3. This module talks to NVIDIA's OpenAI-compatible chat/completions
     endpoint with the full TITAN tool list attached, in a loop:
       - model responds with tool_calls          -> we execute them via
         `tool_executor` (main.py's _execute_tool_by_name) and feed the
         results back as role="tool" messages, then call again.
       - model responds with plain content, no tool_calls -> that's the
         final answer; loop ends.
  4. main.py sends that final text back into the Gemini Live session as
     a "speak this" instruction, so Gemini voices it.

NVIDIA never sees raw audio and Gemini never sees the tools — a clean
split-brain. If NVIDIA is unreachable/misconfigured, `run_brain_turn`
raises; main.py should catch that and fall back to speaking an apology,
NOT silently return no answer.
"""
from __future__ import annotations

import copy
import json
from typing import Any, Awaitable, Callable, Dict, List, Optional

import requests

from core.llm import (
    NVIDIA_BASE_URL,
    NVIDIA_MODEL,
    NVIDIA_FALLBACK_MODEL,
    NVIDIA_FALLBACK_MODELS,
    _get_nvidia_api_key,
)

# Async (name, args) -> result string. main.py passes self._execute_tool_by_name.
ToolExecutor = Callable[[str, dict], Awaitable[str]]

MAX_TOOL_HOPS = 8          # hard ceiling per user turn — never loop forever
REQUEST_TIMEOUT = 60


def _gemini_schema_to_openai(gemini_decl: dict) -> dict:
    """Converts one Gemini function_declarations entry (upper-case JSON
    Schema `type` values: OBJECT/STRING/INTEGER/...) into an OpenAI
    `{"type": "function", "function": {...}}` tool entry (lower-case types).
    Recursive — handles nested `items`/`properties` (e.g. ARRAY of STRING)."""

    def lower_types(node: Any) -> Any:
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                if k == "type" and isinstance(v, str):
                    out[k] = v.lower()
                else:
                    out[k] = lower_types(v)
            return out
        if isinstance(node, list):
            return [lower_types(x) for x in node]
        return node

    params = lower_types(gemini_decl.get("parameters") or {"type": "object", "properties": {}})
    return {
        "type": "function",
        "function": {
            "name": gemini_decl["name"],
            "description": gemini_decl.get("description", ""),
            "parameters": params,
        },
    }


def build_openai_tools(gemini_tool_declarations: List[dict]) -> List[dict]:
    tools = []
    for decl in gemini_tool_declarations:
        try:
            tools.append(_gemini_schema_to_openai(decl))
        except Exception as e:
            print(f"[NvidiaBrain] Skipping bad tool decl {decl.get('name')}: {e}")
    return tools


def _call_nvidia(messages: List[dict], tools: List[dict], model: str, temperature: float) -> dict:
    """One raw HTTP call. Returns the parsed `choices[0].message` dict.
    Tries `model`, then NVIDIA_FALLBACK_MODEL, on any failure/non-200."""
    api_key = _get_nvidia_api_key()
    if not api_key:
        raise RuntimeError(
            "No 'nvidia_api_key' in config/api_keys.json — full-brain mode "
            "needs it. Add it or switch off full-brain mode."
        )

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    last_err: Optional[Exception] = None

    models_to_try = [model] + [m for m in NVIDIA_FALLBACK_MODELS if m != model]
    for attempt_model in models_to_try:
        payload = {
            "model": attempt_model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": temperature,
            "max_tokens": 4096,
        }
        try:
            r = requests.post(
                f"{NVIDIA_BASE_URL}/chat/completions",
                json=payload, headers=headers, timeout=REQUEST_TIMEOUT,
            )
            if r.status_code != 200:
                last_err = RuntimeError(f"NVIDIA {attempt_model} returned {r.status_code}: {r.text[:300]}")
                continue
            data = r.json()
            choice = data["choices"][0]["message"]
            return choice
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(f"NVIDIA brain call failed on all models: {last_err}")


async def run_brain_turn(
    user_text: str,
    history: List[dict],
    tool_executor: ToolExecutor,
    gemini_tool_declarations: List[dict],
    system_prompt: str,
    model: str = NVIDIA_MODEL,
    temperature: float = 0.3,
) -> str:
    """Runs the full plan -> tool-call -> observe loop for ONE user turn.

    `history` is the caller's running OpenAI-format message list (owned by
    main.py, one per live session) — this function appends to it in place
    so the next turn keeps context, and returns only the final spoken
    answer text.
    """
    tools = build_openai_tools(gemini_tool_declarations)

    if not history:
        history.append({"role": "system", "content": system_prompt})

    history.append({"role": "user", "content": user_text})

    for hop in range(MAX_TOOL_HOPS):
        msg = _call_nvidia(history, tools, model, temperature)
        history.append(msg)

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            return (msg.get("content") or "").strip() or "Done."

        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name", "")
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}

            print(f"[NvidiaBrain] hop {hop+1}/{MAX_TOOL_HOPS} -> tool {name}({args})")
            try:
                result = await tool_executor(name, args)
            except Exception as e:
                result = f"Tool '{name}' raised an exception: {e}"

            history.append({
                "role": "tool",
                "tool_call_id": tc.get("id", ""),
                "content": str(result)[:6000],   # keep context sane
            })

    # Hit MAX_TOOL_HOPS without a final answer — surface that honestly
    # instead of pretending the task is done.
    return (
        "I ran into a long tool-call chain and stopped before finishing — "
        "the last steps didn't converge on a final answer. Check the logs."
    )