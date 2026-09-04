"""
actions/shadow_link.py — Real Chrome Extension Bridge for TITAN

Connects TITAN directly to your real open Chrome browser tab via WebSocket bridge on ws://127.0.0.1:8002/client.
"""

import asyncio
import json
import uuid
from pathlib import Path

_WEBSOCKETS_OK = False
try:
    import websockets
    _WEBSOCKETS_OK = True
except ImportError:
    pass

_BRIDGE_URL = "ws://127.0.0.1:8002/client"


def _ensure_bridge_running():
    import subprocess, sys
    bridge_script = Path(__file__).resolve().parent.parent / "shadow_bridge.py"
    if not bridge_script.exists():
        bridge_script = Path(__file__).resolve().parent.parent.parent / "shadow_bridge.py"
    if bridge_script.exists():
        try:
            subprocess.Popen([sys.executable, str(bridge_script)], cwd=str(bridge_script.parent), creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        except Exception:
            pass


async def _send_chrome_command(action_name: str, payload: dict = None, timeout: float = 10.0) -> dict:
    if not _WEBSOCKETS_OK:
        return {"error": "websockets package not installed."}
    payload = payload or {}
    msg_id = str(uuid.uuid4())
    cmd = {
        "type": "action",
        "action": action_name,
        "id": msg_id,
        **payload
    }

    last_err = None
    for attempt in range(4):
        try:
            async with websockets.connect(_BRIDGE_URL, close_timeout=3.0) as ws:
                await ws.send(json.dumps(cmd))
                resp_raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                resp = json.loads(resp_raw)
                if resp.get("state") == "ERROR":
                    err_msg = resp.get("msg", "Extension command error")
                    if "No extension connected" in err_msg and attempt < 3:
                        await asyncio.sleep(1.0)
                        continue
                    return {"error": err_msg}
                return resp.get("result", resp)
        except (ConnectionRefusedError, OSError) as e:
            last_err = e
            if attempt == 0:
                _ensure_bridge_running()
            await asyncio.sleep(0.5)
        except asyncio.TimeoutError:
            return {"error": "Shadow-Link bridge timed out waiting for Chrome response."}
        except Exception as e:
            last_err = e
            if attempt < 3:
                await asyncio.sleep(0.5)
                continue
            return {"error": f"Could not connect to Shadow-Link Chrome bridge at {_BRIDGE_URL}: {e}"}

    return {"error": f"Could not connect to Shadow-Link Chrome bridge at {_BRIDGE_URL}: {last_err}"}


def _focus_chrome_window():
    try:
        import pygetwindow as gw
        for w in gw.getWindowsWithTitle("Chrome"):
            if w.title and "Chrome" in w.title:
                if w.isMinimized:
                    w.restore()
                w.activate()
                break
    except Exception:
        pass


def shadow_link_control(parameters: dict = None) -> str:
    """
    Synchronous entry point for TITAN tool invocation.
    """
    params = parameters or {}
    action = params.get("action", "get_url").lower()
    action_map = {
        "get_url": "get_state",
        "url": "get_state",
        "extract": "get_state",
        "type": "input",
        "smart_type": "input",
        "smart_click": "click",
        "new_tab": "open_tab",
        "switch": "switch_tab",
        "switch_tab": "switch_tab",
        "scroll": "scroll_down"
    }
    action = action_map.get(action, action)

    # Bring Chrome window to front if performing interaction
    if action in ("click", "navigate", "input", "scroll_down", "scroll_up"):
        _focus_chrome_window()

    # Auto-resolve index from DOM tree if clicking or inputting without index
    if action in ("click", "input") and "index" not in params:
        try:
            st_res = None
            try:
                loop = asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    st_res = pool.submit(_run_async_in_new_loop, "get_state", {}).result(timeout=5.0)
            except RuntimeError:
                st_res = asyncio.run(_send_chrome_command("get_state", {}))

            if isinstance(st_res, dict):
                q = (params.get("description") or params.get("text") or params.get("selector") or "").lower()
                q_clean = q.replace("login", "log in").replace("button", "").strip()
                q_words = set(q_clean.split())
                
                matched_idx = None
                best_score = 0
                all_found_indices = []

                # Format A: interactive_elements string (standard Chrome extension output)
                raw_tree_str = st_res.get("interactive_elements", "")
                if isinstance(raw_tree_str, str) and raw_tree_str:
                    import re
                    # Matches [0]<a class='...'> Go or *[0]<button>...
                    line_matches = re.findall(r"(?:\*?\[(\d+)\])(.*?)(?=\n|\r|$)", raw_tree_str)
                    for idx_str, content_str in line_matches:
                        try:
                            idx = int(idx_str)
                            all_found_indices.append(idx)
                            c_lower = content_str.lower()

                            # Exact or high match
                            if q_clean and (q_clean in c_lower or c_lower in q_clean):
                                matched_idx = idx
                                best_score = 999
                                break

                            # Keyword scoring
                            score = sum(1 for w in q_words if w in c_lower)
                            if score > best_score:
                                best_score = score
                                matched_idx = idx
                        except ValueError:
                            continue

                # Format B: raw elementTree dict
                elif "elementTree" in st_res:
                    elems = st_res["elementTree"].get("clickableElements", [])
                    if q_clean:
                        for el in elems:
                            attrs = el.get("attributes", {})
                            parts = [
                                el.get("text", ""),
                                attrs.get("text", ""),
                                attrs.get("value", ""),
                                attrs.get("aria-label", ""),
                                attrs.get("title", ""),
                                attrs.get("class", ""),
                                attrs.get("id", ""),
                                attrs.get("name", ""),
                                attrs.get("alt", ""),
                                el.get("tagName", ""),
                            ]
                            combined_txt = " ".join(str(p) for p in parts if p).lower()
                            idx_found = el.get("highlightIndex")
                            if idx_found is None:
                                continue
                            all_found_indices.append(idx_found)

                            if q_clean in combined_txt or combined_txt in q_clean:
                                matched_idx = idx_found
                                break

                            score = sum(1 for w in q_words if w in combined_txt)
                            if score > best_score:
                                best_score = score
                                matched_idx = idx_found

                # Fallback: if no text matched, use first interactive index
                if matched_idx is None and all_found_indices:
                    matched_idx = all_found_indices[0]

                if matched_idx is not None:
                    params["index"] = matched_idx
                    print(f"[ShadowLink AutoIndex] Resolved index={matched_idx} for query='{q}' (score={best_score})")
        except Exception as e:
            print(f"[ShadowLink AutoIndex Error] {e}")

    payload = {}
    if "url" in params:
        payload["url"] = params["url"]
    if "text" in params:
        payload["text"] = params["text"]
    if "selector" in params:
        payload["selector"] = params["selector"]
    if "description" in params:
        payload["description"] = params["description"]
    if "index" in params:
        payload["index"] = params["index"]

    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_run_async_in_new_loop, action, payload)
            res = future.result(timeout=15.0)
    except RuntimeError:
        res = asyncio.run(_send_chrome_command(action, payload))

    if isinstance(res, dict) and "error" in res:
        return f"[Shadow-Link Chrome] ⚠️ {res['error']}"
    if isinstance(res, dict) and res.get("unsupported"):
        return (
            "[Shadow-Link Chrome] ⚠️ "
            f"{res['unsupported']} URL: {res.get('url') or '(hidden by Chrome)'}"
        )
    if isinstance(res, dict) and res.get("msg"):
        return f"[Shadow-Link Chrome] ✅ {res['msg']}"
    if (
        isinstance(res, dict)
        and not res.get("url")
        and not res.get("title")
        and not res.get("interactive_elements")
    ):
        return (
            "[Shadow-Link Chrome] ⚠️ The active tab returned no readable page content. "
            "It is probably Chrome's built-in PDF viewer or a restricted Chrome page. "
            "Use smart_task summarize_document or file_processor for the PDF instead."
        )
    return f"[Shadow-Link Chrome] ✅ Result: {json.dumps(res, ensure_ascii=False)[:300]}"


def _run_async_in_new_loop(action: str, payload: dict) -> dict:
    """Run the async command in a brand-new event loop on a worker thread."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_send_chrome_command(action, payload))
    finally:
        loop.close()
