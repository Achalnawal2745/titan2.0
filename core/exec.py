"""
core/exec.py — THE ONLY place in TITAN that shells out to a subprocess.

Before this file existed, accept_changes.py, comment.py (indirectly via
office/soffice.py), dev_agent.py, file_processor.py, and skill_engine.py each
had their own subprocess.run(...) with inconsistent timeout handling — some
caught TimeoutExpired, some didn't; some checked returncode, some didn't.

This is also the tool exposed to Gemini as `run_command`, so a loaded
SKILL.md (e.g. "run python scripts/merge_runs.py unpacked/") can actually be
executed by the agent instead of the model just describing what should
happen.

SAFETY: this gives the LLM real code execution on the host machine. cwd is
NOT sandboxed here — enforce your workspace jail at the call site (e.g. only
allow cwd under a known project root) before wiring this to a live voice
tool a stranger could reach.
"""
from __future__ import annotations

import hashlib
import os
import re
import shlex
import subprocess
import tempfile
from pathlib import Path


def _recover_inline_code_command(raw: str) -> list[str] | None:
    """Fallback for `node -e '<code>'` / `python -c '<code>'` commands that
    shlex.split() couldn't parse.

    This happens constantly with real generated code: the model wraps the
    whole script in a shell '...' string, but the code itself contains an
    apostrophe (e.g. "world's earliest") — often with a stray backslash in
    front of it because the model tried to escape it. POSIX shells have NO
    escape mechanism inside single quotes, so that backslash-quote just
    closes the string early and shlex throws "No closing quotation". This
    isn't a one-off mistake, it's structurally guaranteed to happen again
    any time inline code contains a quote character — so instead of asking
    a live-voice model to get shell escaping perfect for multi-hundred-line
    JS/Python blobs, we just don't rely on shell quoting at all: pull the
    raw code out, write it to a temp file, run the file.

    Best-effort by design: assumes the FIRST quote char after -e/-c opens
    the code block and the LAST occurrence of that same quote char in the
    string closes it (true for the common case — one big quoted blob, no
    trailing shell args after it). Returns None if the shape doesn't match,
    so the caller can fall back to the original parse error.
    """
    m = re.match(r"^\s*(node|nodejs|python|python3|py)\s+(-e|-c)\s+(.*)$", raw, re.DOTALL)
    if not m:
        return None
    runner, _flag, rest = m.groups()
    rest = rest.strip()
    if not rest or rest[0] not in ("'", '"'):
        return None
    quote = rest[0]
    last = rest.rfind(quote)
    if last <= 0:
        return None
    code = rest[1:last]
    # Undo the model's (invalid) attempt to escape the outer quote from
    # inside it, e.g. \' -> ' or \" -> "
    code = code.replace(f"\\{quote}", quote)
    if not code.strip():
        return None

    suffix = ".js" if runner.lower() in ("node", "nodejs") else ".py"
    tmp_dir = Path(__file__).resolve().parent.parent / "scratch" / "inline_scripts"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(code.encode("utf-8", errors="ignore")).hexdigest()[:10]
    tmp_file = tmp_dir / f"inline_{os.getpid()}_{digest}{suffix}"
    tmp_file.write_text(code, encoding="utf-8")
    return [runner, str(tmp_file)]


def run_command(
    cmd: str | list[str],
    cwd: str | None = None,
    timeout: int = 30,
    shell: bool = False,
    stdin_text: str | None = None,
    no_window: bool = True,
) -> dict:
    """
    Runs a command and always returns a dict — never raises. Shape:
        {"ok": bool, "stdout": str, "stderr": str, "exit_code": int}
    `cmd` may be a string ("python scripts/x.py file.docx") or an argv list.
    If it's a string and shell=False, it's split with shlex so args with
    spaces in quotes survive.

    stdin_text: piped to the process's stdin if given (e.g. sandboxed skill
    tests that read from stdin); otherwise stdin is DEVNULL so a hung
    process waiting on input can't block the calling thread forever.
    no_window: on Windows, suppress the console window popup (matches what
    skill_engine.py's sandboxed test runs need — a live-voice assistant
    spawning terminal windows during a voice session is a bad experience).
    """
    if isinstance(cmd, str) and not shell:
        # Check for inline -e/-c code FIRST, before shlex ever touches it.
        # This is the actual bug behind real-world failures like a JS
        # template literal containing "India's": shlex doesn't always raise
        # on a quote character embedded inside the code (an apostrophe in
        # real text/JS is extremely common) — it can silently mis-split
        # instead, truncating the script at that apostrophe with NO
        # exception raised at all. The old order only routed through
        # _recover_inline_code_command when shlex raised ValueError, which
        # never happens in the silent-corruption case — so the truncated,
        # syntactically-broken script actually ran, unnoticed until it
        # failed downstream. Routing every -e/-c command through the
        # tempfile path unconditionally, before shlex sees it, removes
        # shell quoting from this path entirely.
        recovered = _recover_inline_code_command(cmd)
        if recovered is not None:
            cmd = recovered
        else:
            try:
                cmd = shlex.split(cmd)
            except ValueError as e:
                return {"ok": False, "stdout": "", "stderr": f"bad command syntax: {e}", "exit_code": -1}

    # Automatically resolve python interpreter to project/sandbox venv
    node_env = None
    if isinstance(cmd, list) and cmd:
        if cmd[0].lower() in ("python", "python3", "py"):
            cmd[0] = _resolve_python(True)
        if cmd[0].lower() in ("npm", "npx") and os.name == "nt":
            import shutil
            resolved_cmd = shutil.which(cmd[0]) or shutil.which(f"{cmd[0]}.cmd")
            if resolved_cmd:
                cmd[0] = resolved_cmd
            else:
                shell = True
        if cmd[0].lower() in ("node", "nodejs"):
            node_env = dict(os.environ)
            paths_to_add = [
                str(Path(__file__).resolve().parent.parent / "node_modules"),
                str(Path(__file__).resolve().parent.parent / "skills" / "_sandbox" / "node" / "node_modules"),
            ]
            appdata = os.environ.get("APPDATA")
            if appdata:
                paths_to_add.append(str(Path(appdata) / "npm" / "node_modules"))
            
            existing = [p for p in node_env.get("NODE_PATH", "").split(os.pathsep) if p]
            all_node_paths = [p for p in paths_to_add if Path(p).exists()] + existing
            node_env["NODE_PATH"] = os.pathsep.join(all_node_paths)
        # Expand user Desktop/Downloads/Documents if relative
        home = Path.home()
        base_dir = Path(__file__).resolve().parent.parent
        for idx in range(1, len(cmd)):
            arg = cmd[idx]
            for folder in ("Desktop", "Downloads", "Documents"):
                if arg.startswith(f"{folder}/") or arg.startswith(f"{folder}\\"):
                    candidate = home / arg
                    if candidate.parent.exists():
                        cmd[idx] = str(candidate)

        # Auto-resolve relative script files under skills/ — all skills live
        # here directly (not under bro/), so this is the one place to search.
        # Real fix is skill_registry.load() now giving absolute paths
        # directly (see core/skill_registry.py) — this stays only as a
        # fallback if a relative path slips through anyway.
        if len(cmd) > 1 and not cmd[1].startswith("-") and not Path(cmd[1]).is_absolute() and not (base_dir / cmd[1]).exists():
            script_name = Path(cmd[1]).name
            skills_root = base_dir / "skills"
            if skills_root.exists():
                found_path = next((f for f in skills_root.rglob(script_name) if f.is_file()), None)
                if found_path:
                    cmd[1] = str(found_path)

    if cwd and not Path(cwd).exists():
        return {"ok": False, "stdout": "", "stderr": f"cwd does not exist: {cwd}", "exit_code": -1}

    kw: dict = {
        "cwd": cwd or str(Path(__file__).resolve().parent.parent),
        "timeout": timeout,
        "shell": shell,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "check": False,
    }
    if stdin_text is None:
        kw["stdin"] = subprocess.DEVNULL
    else:
        kw["input"] = stdin_text
    if no_window and os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if node_env is not None:
        kw["env"] = node_env

    try:
        from core.spill import maybe_spill_output
        result = subprocess.run(cmd, **kw)
        stdout_clean, _, _ = maybe_spill_output("run_command_stdout", result.stdout)
        stderr_clean, _, _ = maybe_spill_output("run_command_stderr", result.stderr)
        return {
            "ok": result.returncode == 0,
            "stdout": stdout_clean,
            "stderr": stderr_clean,
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": f"command timed out after {timeout}s", "exit_code": -1}
    except FileNotFoundError as e:
        return {"ok": False, "stdout": "", "stderr": f"command not found: {e}", "exit_code": -1}
    except Exception as e:
        return {"ok": False, "stdout": "", "stderr": str(e), "exit_code": -1}


def run_python_file(path: str, args: list[str] | None = None, cwd: str | None = None,
                     timeout: int = 30, use_sandbox: bool = True) -> dict:
    """Convenience wrapper — skills reference scripts by path constantly."""
    exe = _resolve_python(use_sandbox)
    cmd = [exe, path] + (args or [])
    return run_command(cmd, cwd=cwd, timeout=timeout)


def _resolve_python(use_sandbox: bool = True) -> str:
    """Single source of truth for which python interpreter run_command uses.

    NOTE: skill_engine.py's sandbox venv (skills/_sandbox/venv) is gone —
    that engine was a separate flat-file (skills/*.py) skill system,
    unrelated to the SKILL.md skills discovered by skill_registry.py, and
    it was never wired into main.py's TOOL_DECLARATIONS to begin with. This
    now just checks for a plain project-root venv, falling back to whatever
    Python is already running TITAN. If your skills need packages that
    aren't in that interpreter, install them into it directly (pip install
    into the project venv, or your global interpreter if there is no venv)
    — there's no separate sandbox venv/installer anymore.
    """
    import sys
    if use_sandbox:
        try:
            proj_py = Path(__file__).resolve().parent.parent / "venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
            if proj_py.exists():
                return str(proj_py)
        except Exception:
            pass
    return sys.executable or "python"


# ── Gemini tool declaration, importable straight into main.py's TOOL_DECLARATIONS ──
RUN_COMMAND_DECLARATION = {
    "name": "run_command",
    "description": (
        "Run a shell command — most often a skill's scripts/*.py after load_skill "
        "told you which script to run. Returns stdout, stderr, and exit_code. "
        "cwd defaults to the project root if you don't pass one, so relative "
        "paths from a SKILL.md (e.g. 'scripts/unpack.py') resolve correctly. "
        "AVOID `node -e '<code>'` or `python -c '<code>'` for anything longer than "
        "one line — if the code contains an apostrophe or quote character (very common "
        "in real text/JS), shell quoting breaks and the command fails before it even runs. "
        "Prefer writing the code to a .js/.py file with your file tool first, then run "
        "'node path/to/file.js' or 'python path/to/file.py'. "
        "If a Python script fails with ModuleNotFoundError, run this tool again with "
        "cmd='pip install <package_name>' FIRST (same interpreter this tool uses), "
        "then retry the original command once. "
        "If a Node script fails with 'Cannot find module', run this tool again with "
        "cmd='npm install <package_name>' AND cwd set to the SAME FOLDER the .js script "
        "lives in (not the project root) — Node only finds node_modules next to or above "
        "the script's own file, so installing anywhere else silently does nothing — then "
        "retry the original node command once. "
        "Do not retry an unchanged command a second time "
        "without first changing something (interpreter, cwd, or dependency). "
        "If exit_code is non-zero, the task did NOT succeed — do not tell the user "
        "it's done or that a file was saved. Paths given to you by load_skill's "
        "[SCRIPTS AVAILABLE] list are already absolute and correct — use them "
        "exactly as given, never shorten them or guess a different path, and "
        "never run 'find'/'dir' to search for a script yourself."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "cmd": {"type": "STRING", "description": "Command to run, e.g. 'python scripts/merge_runs.py unpacked/'. If the command starts with 'python', the sandbox interpreter is used automatically."},
            "cwd": {"type": "STRING", "description": "Working directory (optional — defaults to project root)"},
            "timeout": {"type": "INTEGER", "description": "Seconds before killing the command (default 30)"},
        },
        "required": ["cmd"],
    },
}