"""
TITAN Skill Engine 2.0
======================
Write a skill → install its deps in an isolated venv → test it → run it.

Nothing is pip-installed into TITAN's own environment.
Skills never import into TITAN's process (a bad skill cannot crash the assistant).
"""
from __future__ import annotations

import ast
import inspect
import json
import os
import re
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any


SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
SANDBOX_DIR = SKILLS_DIR / "_sandbox"
VENV_DIR = SANDBOX_DIR / "venv"
META_DIR = SKILLS_DIR / "_meta"
RUNNER_PATH = SANDBOX_DIR / "runner.py"

# ---------------------------------------------------------------------------
# Sandbox runner — executed by the *venv* python, never by TITAN
# ---------------------------------------------------------------------------
_RUNNER_SRC = r'''
import json, sys, traceback, importlib, inspect
from pathlib import Path

# skills/_sandbox/runner.py  →  project root is parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def _jsonable(x):
    if x is None or isinstance(x, (str, int, float, bool)):
        return x
    if isinstance(x, (list, tuple)):
        return [_jsonable(i) for i in x]
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    return str(x)


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    op = payload.get("op")
    skill = payload.get("skill")
    try:
        if op == "inspect":
            mod = importlib.import_module(f"skills.{skill}")
            funcs = [n for n, o in inspect.getmembers(mod, inspect.isfunction) if not n.startswith("_")]
            req = getattr(mod, "REQUIREMENTS", [])
            print(json.dumps({
                "ok": True,
                "functions": funcs,
                "requirements": list(req) if req else [],
            }))
            return

        if op == "test":
            mod = importlib.import_module(f"skills.{skill}")
            funcs = [n for n, o in inspect.getmembers(mod, inspect.isfunction) if not n.startswith("_")]
            if hasattr(mod, "test") and callable(mod.test):
                result = mod.test()
                print(json.dumps({
                    "ok": True,
                    "tested": True,
                    "functions": funcs,
                    "result": _jsonable(result),
                }))
            else:
                print(json.dumps({
                    "ok": True,
                    "tested": False,
                    "imported": True,
                    "functions": funcs,
                    "note": "no test() — import succeeded",
                }))
            return

        if op == "call":
            mod = importlib.import_module(f"skills.{skill}")
            fn = (payload.get("function") or "").strip()
            kwargs = payload.get("kwargs") or {}
            if not isinstance(kwargs, dict):
                kwargs = {}
            funcs = [n for n, o in inspect.getmembers(mod, inspect.isfunction) if not n.startswith("_")]
            func = None
            if fn and hasattr(mod, fn):
                func = getattr(mod, fn)
            elif fn:
                fl = fn.lower()
                for pf in funcs:
                    if fl in pf.lower() or pf.lower() in fl:
                        func = getattr(mod, pf)
                        break
            if func is None and funcs:
                # skip test() as the default callable
                pick = next((p for p in funcs if p != "test"), funcs[0])
                func = getattr(mod, pick)
            if func is None:
                print(json.dumps({"ok": False, "error": f"No function in '{skill}'. Available: {funcs}"}))
                return
            result = func(**kwargs) if kwargs else func()
            print(json.dumps({
                "ok": True,
                "function": func.__name__,
                "result": _jsonable(result),
            }))
            return

        print(json.dumps({"ok": False, "error": f"unknown op {op}"}))
    except Exception as e:
        print(json.dumps({
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }))


if __name__ == "__main__":
    main()
'''

# stdlib / builtins — never pip-install these
_STDLIB = {
    "abc", "argparse", "array", "ast", "asyncio", "atexit", "base64", "binascii",
    "bisect", "builtins", "calendar", "cmath", "collections", "colorsys", "compileall",
    "concurrent", "contextlib", "copy", "copyreg", "csv", "ctypes", "dataclasses",
    "datetime", "decimal", "difflib", "dis", "email", "enum", "errno", "fnmatch",
    "fractions", "functools", "gc", "getopt", "getpass", "gettext", "glob", "gzip",
    "hashlib", "heapq", "hmac", "html", "http", "imaplib", "inspect", "io", "ipaddress",
    "itertools", "json", "keyword", "linecache", "locale", "logging", "lzma", "math",
    "mimetypes", "multiprocessing", "numbers", "operator", "os", "pathlib", "pickle",
    "pkgutil", "platform", "plistlib", "pprint", "queue", "random", "re", "reprlib",
    "secrets", "select", "shelve", "shlex", "shutil", "signal", "socket", "sqlite3",
    "ssl", "stat", "statistics", "string", "struct", "subprocess", "sys", "sysconfig",
    "tarfile", "tempfile", "textwrap", "threading", "time", "timeit", "token",
    "tokenize", "traceback", "types", "typing", "unicodedata", "unittest", "urllib",
    "uuid", "warnings", "wave", "weakref", "webbrowser", "xml", "xmlrpc", "zipfile",
    "zipimport", "zoneinfo", "tomllib", "graphlib", "__future__",
}

PIP_MODULE_MAP = {
    "speedtest": "speedtest-cli",
    "pptx": "python-pptx",
    "bs4": "beautifulsoup4",
    "yaml": "pyyaml",
    "cv2": "opencv-python",
    "PIL": "pillow",
    "Image": "pillow",
    "docx": "python-docx",
    "fitz": "pymupdf",
    "sklearn": "scikit-learn",
    "serial": "pyserial",
    "qrcode": "qrcode[pil]",
    "dotenv": "python-dotenv",
    "yt_dlp": "yt-dlp",
    "cv2": "opencv-python",
    "dateutil": "python-dateutil",
    "skimage": "scikit-image",
    "wx": "wxpython",
    "gi": "PyGObject",
    "lxml": "lxml",
    "bs4": "beautifulsoup4",
}

_DANGEROUS_SUBSTRINGS = (
    "format c:", "format d:", "format e:",
    "rd /s /q c:", "del /f /s /q c:",
    "rmdir /s /q c:", "rm -rf /", "rm -rf /*",
    ":(){ :|:& };:",
    "mkfs.", "diskpart",
    "remove-item -recurse c:",
)

_DANGEROUS_CALLS = {
    ("os", "system"),
    ("os", "_exit"),
    ("os", "kill"),
    ("ctypes", "windll"),
    ("ctypes", "cdll"),
    ("ctypes", "WinDLL"),
}


def _run(cmd: list[str], timeout: int, cwd: str | None = None, stdin_text: str | None = None) -> subprocess.CompletedProcess:
    kw: dict[str, Any] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "timeout": timeout,
        "cwd": cwd,
    }
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if stdin_text is None:
        kw["stdin"] = subprocess.DEVNULL
    else:
        kw["input"] = stdin_text
    return subprocess.run(cmd, **kw)


class SkillEngine:
    def __init__(self):
        self.loaded_skills: dict[str, dict] = {}
        self._ensure_dirs()
        self._index_disk_skills()

    # ── paths / naming ────────────────────────────────────────────────────

    def _ensure_dirs(self) -> None:
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        META_DIR.mkdir(parents=True, exist_ok=True)
        SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
        init = SKILLS_DIR / "__init__.py"
        if not init.exists():
            init.write_text('"""TITAN Dynamic Skills Package"""\n', encoding="utf-8")
        if not RUNNER_PATH.exists() or RUNNER_PATH.read_text(encoding="utf-8") != _RUNNER_SRC:
            RUNNER_PATH.write_text(_RUNNER_SRC, encoding="utf-8")

    @staticmethod
    def _clean_name(skill_name: str) -> str:
        clean = "".join(c if c.isalnum() or c == "_" else "_" for c in (skill_name or "custom")).lower()
        clean = re.sub(r"_+", "_", clean).strip("_") or "custom"
        if not clean.endswith("_skill"):
            clean = f"{clean}_skill"
        return clean

    def _skill_file(self, clean_name: str) -> Path:
        return SKILLS_DIR / f"{clean_name}.py"

    def _req_file(self, clean_name: str) -> Path:
        return SKILLS_DIR / f"{clean_name}.requirements.txt"

    def _meta_file(self, clean_name: str) -> Path:
        return META_DIR / f"{clean_name}.json"

    def _save_meta(self, clean_name: str, data: dict) -> None:
        try:
            self._meta_file(clean_name).write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _load_meta(self, clean_name: str) -> dict:
        p = self._meta_file(clean_name)
        if not p.exists():
            return {}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}

    # ── host / venv python ────────────────────────────────────────────────

    @staticmethod
    def _host_python() -> str:
        exe = sys.executable or ""
        name = Path(exe).name.lower()
        if "python" in name:
            return exe
        # Frozen TITAN.exe — find a real interpreter
        for cand in ("python", "python3", "py"):
            try:
                r = subprocess.run(
                    [cand, "-c", "import sys; print(sys.executable)"],
                    capture_output=True, text=True, timeout=8,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
                )
                if r.returncode == 0 and r.stdout.strip():
                    return r.stdout.strip()
            except Exception:
                continue
        return exe or "python"

    def _venv_python(self) -> Path:
        if os.name == "nt":
            return VENV_DIR / "Scripts" / "python.exe"
        return VENV_DIR / "bin" / "python"

    def ensure_sandbox(self) -> dict:
        """Create skills/_sandbox/venv once. Never touches TITAN's venv."""
        self._ensure_dirs()
        py = self._venv_python()
        if py.exists():
            return {"success": True, "python": str(py), "created": False}

        host = self._host_python()
        print(f"[SkillEngine] Creating sandbox venv with {host} → {VENV_DIR}")
        try:
            proc = _run([host, "-m", "venv", str(VENV_DIR)], timeout=120)
        except Exception as e:
            return {"success": False, "error": f"venv create failed: {e}"}
        if proc.returncode != 0 or not py.exists():
            err = (proc.stderr or proc.stdout or "").strip()
            return {"success": False, "error": f"venv create failed: {err}"}

        try:
            _run([str(py), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], timeout=180)
        except Exception as e:
            print(f"[SkillEngine] pip upgrade warning: {e}")

        print(f"[SkillEngine] Sandbox ready: {py}")
        return {"success": True, "python": str(py), "created": True}

    # ── code helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _normalize_code(code: str) -> str:
        if not code:
            return ""
        if "\\n" in code and "\n" not in code:
            try:
                code = bytes(code, "utf-8").decode("unicode_escape")
            except Exception:
                code = code.replace("\\n", "\n").replace("\\t", "\t")
        elif "\\n" in code and code.count("\\n") > code.count("\n"):
            code = code.replace("\\n", "\n").replace("\\t", "\t")
        return code.strip()

    def _verify_safety(self, code: str) -> tuple[bool, str]:
        norm = self._normalize_code(code)
        try:
            tree = ast.parse(norm)
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"

        low = norm.lower()
        for pat in _DANGEROUS_SUBSTRINGS:
            if pat in low:
                return False, f"Blocked destructive command: '{pat}'"

        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                pair = (node.value.id, node.attr)
                if pair in _DANGEROUS_CALLS:
                    return False, f"Blocked call: {pair[0]}.{pair[1]}"
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "shutil" and node.func.attr == "rmtree":
                    # allow rmtree of local paths; block if a constant starts with a drive root
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            v = arg.value.lower().replace("/", "\\")
                            if re.match(r"^[a-z]:\\?$", v) or v.startswith("c:\\windows") or v.startswith("c:\\users"):
                                return False, f"Blocked shutil.rmtree on system path: {arg.value}"
        return True, "Safe"

    def _public_functions(self, code: str) -> list[str]:
        try:
            tree = ast.parse(self._normalize_code(code))
        except SyntaxError:
            return []
        names = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                names.append(node.name)
        return names

    def _extract_requirements(self, code: str, extra: list[str] | None = None) -> list[str]:
        """REQUIREMENTS = [...] plus third-party imports, mapped to pip names."""
        pkgs: list[str] = []
        src = self._normalize_code(code)
        try:
            tree = ast.parse(src)
        except SyntaxError:
            tree = None

        if tree:
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name) and t.id == "REQUIREMENTS":
                            if isinstance(node.value, (ast.List, ast.Tuple)):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                        pkgs.append(elt.value.strip())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        pkgs.append(self._mod_to_pip(alias.name.split(".")[0]))
                elif isinstance(node, ast.ImportFrom) and node.module:
                    pkgs.append(self._mod_to_pip(node.module.split(".")[0]))

        if extra:
            pkgs.extend(extra)

        out: list[str] = []
        seen: set[str] = set()
        for p in pkgs:
            p = (p or "").strip()
            if not p or p in seen:
                continue
            top = p.split("==")[0].split(">=")[0].split("[")[0].replace("-", "_").lower()
            if top in _STDLIB or top in {"skills", "actions", "memory", "ui", "titan"}:
                continue
            if p in seen:
                continue
            seen.add(p)
            out.append(p)
        return out

    @staticmethod
    def _mod_to_pip(mod: str) -> str:
        return PIP_MODULE_MAP.get(mod, mod)

    # ── sandbox I/O ───────────────────────────────────────────────────────

    def _sandbox_json(self, payload: dict, timeout: int = 45) -> dict:
        ready = self.ensure_sandbox()
        if not ready.get("success"):
            return {"ok": False, "error": ready.get("error", "sandbox missing")}
        py = str(self._venv_python())
        try:
            proc = _run(
                [py, str(RUNNER_PATH)],
                timeout=timeout,
                cwd=str(SKILLS_DIR.parent),
                stdin_text=json.dumps(payload),
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"Sandbox timed out after {timeout}s"}
        except Exception as e:
            return {"ok": False, "error": f"Sandbox launch failed: {e}"}

        raw = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if not raw:
            return {"ok": False, "error": err or f"empty sandbox output (exit {proc.returncode})"}
        # runner prints one JSON object — take the last line in case of warnings
        line = raw.splitlines()[-1]
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return {"ok": False, "error": f"bad sandbox JSON: {raw[:400]}", "stderr": err}
        if err and not data.get("ok"):
            data.setdefault("stderr", err)
        return data

    def install_deps(self, packages: list[str] | str, skill_name: str = "") -> dict:
        """pip install into the sandbox venv only."""
        if isinstance(packages, str):
            packages = [p.strip() for p in packages.replace(",", " ").split() if p.strip()]
        packages = [p for p in (packages or []) if p]
        if not packages:
            return {"success": True, "installed": [], "note": "nothing to install"}

        ready = self.ensure_sandbox()
        if not ready.get("success"):
            return {"success": False, "error": ready.get("error")}

        py = str(self._venv_python())
        installed, failed = [], []
        for pkg in packages:
            print(f"[SkillEngine] pip install {pkg}  (sandbox)")
            try:
                proc = _run(
                    [py, "-m", "pip", "install", "--no-warn-script-location", pkg],
                    timeout=180,
                )
            except subprocess.TimeoutExpired:
                failed.append({pkg: "timeout"})
                continue
            except Exception as e:
                failed.append({pkg: str(e)})
                continue
            if proc.returncode == 0:
                installed.append(pkg)
            else:
                failed.append({pkg: (proc.stderr or proc.stdout or "")[-400:]})

        result = {
            "success": not failed,
            "installed": installed,
            "failed": failed,
            "venv": str(VENV_DIR),
        }
        if skill_name:
            clean = self._clean_name(skill_name)
            meta = self._load_meta(clean)
            meta["installed"] = sorted(set((meta.get("installed") or []) + installed))
            self._save_meta(clean, meta)
        return result

    def _auto_install_from_error(self, error_output: str) -> list[str]:
        matches = re.findall(r"No module named ['\"]([^'\"]+)['\"]", error_output or "")
        pkgs = []
        for mod in set(matches):
            top = mod.split(".")[0]
            if top in _STDLIB:
                continue
            pkgs.append(self._mod_to_pip(top))
        if not pkgs:
            return []
        res = self.install_deps(pkgs)
        return res.get("installed") or []

    # ── public API (same names main.py already calls) ─────────────────────

    def create_and_test_skill(
        self,
        skill_name: str,
        python_code: str,
        test_inputs: dict | None = None,
        extra_packages: list[str] | None = None,
    ) -> dict:
        """
        1. Safety + syntax
        2. Write skills/<name>_skill.py + requirements.txt
        3. Ensure sandbox venv
        4. pip install deps into THAT venv
        5. Import + run test() inside the venv
        6. Return a report Titan can speak / use to fix
        """
        python_code = self._normalize_code(python_code)
        is_safe, reason = self._verify_safety(python_code)
        if not is_safe:
            return {
                "success": False,
                "skill_name": skill_name,
                "error": f"Safety check failed: {reason}",
                "status": "BLOCKED",
                "hint": "Rewrite the skill without destructive system commands, then call create_skill again.",
            }

        clean = self._clean_name(skill_name)
        skill_file = self._skill_file(clean)
        funcs = self._public_functions(python_code)
        reqs = self._extract_requirements(python_code, extra_packages)

        if not funcs:
            return {
                "success": False,
                "skill_name": clean,
                "error": "Skill has no public function. Add at least one def foo(...): and a def test():",
                "hint": (
                    "Every skill must look like:\n"
                    "REQUIREMENTS = [\"requests\"]\n"
                    "def do_thing(x=1):\n    return x\n"
                    "def test():\n    assert do_thing(2) == 2\n    return True\n"
                ),
            }

        try:
            skill_file.write_text(python_code, encoding="utf-8")
            if reqs:
                self._req_file(clean).write_text("\n".join(reqs) + "\n", encoding="utf-8")
        except Exception as e:
            return {"success": False, "skill_name": clean, "error": f"Could not write skill file: {e}"}

        ready = self.ensure_sandbox()
        if not ready.get("success"):
            return {
                "success": False,
                "skill_name": clean,
                "error": f"Sandbox venv failed: {ready.get('error')}",
                "file_path": str(skill_file),
            }

        install_report = self.install_deps(reqs, skill_name=clean) if reqs else {"installed": [], "failed": []}

        # Test loop: import / test(), auto-pip on missing module, up to 3 tries
        last = {}
        auto: list[str] = list(install_report.get("installed") or [])
        for attempt in range(1, 4):
            last = self._sandbox_json({"op": "test", "skill": clean}, timeout=45)
            if last.get("ok"):
                break
            err = f"{last.get('error','')} {last.get('traceback','')} {last.get('stderr','')}"
            newly = self._auto_install_from_error(err)
            auto.extend(newly)
            if not newly:
                break

        meta = {
            "name": clean,
            "functions": last.get("functions") or funcs,
            "requirements": reqs,
            "installed": sorted(set(auto)),
            "last_test_ok": bool(last.get("ok")),
            "has_test": bool(last.get("tested")),
        }
        self._save_meta(clean, meta)
        self.loaded_skills[clean] = meta

        if not last.get("ok"):
            return {
                "success": False,
                "skill_name": clean,
                "status": "SAVED_BUT_TESTS_FAILED",
                "file_path": str(skill_file),
                "functions": funcs,
                "requirements": reqs,
                "auto_installed": auto,
                "install_failed": install_report.get("failed") or [],
                "error": last.get("error") or "sandbox test failed",
                "traceback": (last.get("traceback") or "")[-1500:],
                "hint": (
                    "Read the traceback, fix the Python, then call "
                    "skill_engine action='edit_skill' with the full corrected code. "
                    "Do not tell the user you cannot do it — fix the skill."
                ),
            }

        return {
            "success": True,
            "skill_name": clean,
            "status": "Verified in sandbox venv & ready to execute",
            "file_path": str(skill_file),
            "exported_functions": last.get("functions") or funcs,
            "requirements": reqs,
            "auto_installed_dependencies": auto,
            "test_ran": bool(last.get("tested")),
            "test_result": last.get("result"),
            "how_to_run": (
                f"Call skill_engine action='execute_skill' skill_name='{clean}' "
                f"function_name='{next((f for f in (last.get('functions') or funcs) if f != 'test'), funcs[0])}'"
            ),
        }

    def edit_skill(self, skill_name: str, new_python_code: str) -> dict:
        return self.create_and_test_skill(skill_name, new_python_code)

    def test_skill(self, skill_name: str) -> dict:
        clean = self._clean_name(skill_name)
        if not self._skill_file(clean).exists():
            return {"success": False, "error": f"Skill '{clean}' not found."}
        # reinstall declared reqs then test
        code = self._skill_file(clean).read_text(encoding="utf-8")
        reqs = self._extract_requirements(code)
        if reqs:
            self.install_deps(reqs, skill_name=clean)
        last = self._sandbox_json({"op": "test", "skill": clean}, timeout=45)
        if not last.get("ok"):
            newly = self._auto_install_from_error(
                f"{last.get('error','')} {last.get('traceback','')}"
            )
            if newly:
                last = self._sandbox_json({"op": "test", "skill": clean}, timeout=45)
        last["success"] = bool(last.get("ok"))
        last["skill_name"] = clean
        return last

    def get_skill_code(self, skill_name: str) -> dict:
        clean = self._clean_name(skill_name)
        skill_file = self._skill_file(clean)
        if not skill_file.exists():
            # tolerate already-suffixed / raw names
            alt = SKILLS_DIR / f"{skill_name}.py"
            if alt.exists():
                skill_file = alt
                clean = alt.stem
            else:
                return {"success": False, "error": f"Skill '{clean}' does not exist on disk."}
        try:
            return {
                "success": True,
                "skill_name": clean,
                "code": skill_file.read_text(encoding="utf-8"),
                "meta": self._load_meta(clean),
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to read skill '{clean}': {e}"}

    def delete_skill(self, skill_name: str) -> dict:
        clean = self._clean_name(skill_name)
        skill_file = self._skill_file(clean)
        deleted = False
        if skill_file.exists():
            try:
                skill_file.unlink()
                deleted = True
            except Exception as e:
                return {"success": False, "error": f"Failed to delete skill file: {e}"}
        for extra in (self._req_file(clean), self._meta_file(clean)):
            try:
                if extra.exists():
                    extra.unlink()
            except Exception:
                pass
        self.loaded_skills.pop(clean, None)
        return {
            "success": True,
            "skill_name": clean,
            "status": "Deleted" if deleted else "Nothing on disk to delete",
        }

    def list_skills(self) -> list[str]:
        return [
            f.stem
            for f in SKILLS_DIR.glob("*.py")
            if f.name not in {"__init__.py"} and not f.name.startswith("_")
        ]

    def list_skills_detailed(self) -> list[dict]:
        out = []
        for name in self.list_skills():
            meta = self._load_meta(name)
            if not meta.get("functions"):
                try:
                    code = self._skill_file(name).read_text(encoding="utf-8")
                    meta["functions"] = self._public_functions(code)
                    meta["requirements"] = self._extract_requirements(code)
                except Exception:
                    meta["functions"] = []
            out.append({
                "name": name,
                "functions": meta.get("functions") or [],
                "requirements": meta.get("requirements") or [],
                "tested": meta.get("last_test_ok"),
            })
        return out

    def skill_info(self, skill_name: str) -> dict:
        clean = self._clean_name(skill_name)
        if not self._skill_file(clean).exists():
            return {"success": False, "error": f"Skill '{clean}' not found.", "available": self.list_skills()}
        meta = self._load_meta(clean)
        inspect_ = self._sandbox_json({"op": "inspect", "skill": clean}, timeout=20)
        return {
            "success": True,
            "skill_name": clean,
            "file_path": str(self._skill_file(clean)),
            "meta": meta,
            "sandbox": inspect_,
            "venv": str(VENV_DIR),
        }

    def execute_skill(self, skill_name: str = "", function_name: str = "", **kwargs) -> dict:
        """Run a skill function inside the sandbox venv (where its pip packages live)."""
        all_skills = self.list_skills()
        clean = self._clean_name(skill_name) if skill_name else ""

        if not skill_name or clean == "_skill":
            if function_name:
                for s in all_skills:
                    try:
                        code = self._skill_file(s).read_text(encoding="utf-8")
                        if function_name in self._public_functions(code):
                            clean = s
                            break
                    except Exception:
                        continue
            if (not clean or clean == "_skill") and len(all_skills) == 1:
                clean = all_skills[0]
            elif not clean or clean == "_skill":
                return {"success": False, "error": f"Specify skill_name. Available: {all_skills}"}

        if not self._skill_file(clean).exists():
            return {"success": False, "error": f"Skill file '{clean}.py' not found."}

        # Make sure declared deps are present before the call
        try:
            code = self._skill_file(clean).read_text(encoding="utf-8")
            reqs = self._extract_requirements(code)
            if reqs:
                self.install_deps(reqs, skill_name=clean)
        except Exception:
            pass

        last = self._sandbox_json(
            {"op": "call", "skill": clean, "function": function_name or "", "kwargs": kwargs},
            timeout=60,
        )
        if not last.get("ok"):
            newly = self._auto_install_from_error(f"{last.get('error','')} {last.get('traceback','')}")
            if newly:
                last = self._sandbox_json(
                    {"op": "call", "skill": clean, "function": function_name or "", "kwargs": kwargs},
                    timeout=60,
                )
        if last.get("ok"):
            return {
                "success": True,
                "skill_name": clean,
                "function": last.get("function"),
                "result": last.get("result"),
            }
        return {
            "success": False,
            "skill_name": clean,
            "error": last.get("error") or "execution failed",
            "traceback": (last.get("traceback") or "")[-1500:],
        }

    def run_command(self, command: str, timeout: int = 90) -> dict:
        """
        Run a developer command *inside the sandbox venv*.
        Allowed: pip ..., python ..., python -m ..., python -c ...
        """
        if not command or not str(command).strip():
            return {"success": False, "error": "Empty command."}
        raw = str(command).strip()
        low = raw.lower()

        banned = ("format ", "del /", "rmdir", "rm -rf", "powershell", "cmd /c",
                  "msiexec", "reg add", "reg delete", "shutdown", "start ")
        if any(b in low for b in banned):
            return {"success": False, "error": "Command not allowed in sandbox."}

        ready = self.ensure_sandbox()
        if not ready.get("success"):
            return {"success": False, "error": ready.get("error")}
        py = str(self._venv_python())

        # Rewrite to always use the venv interpreter
        import shlex
        try:
            parts = shlex.split(raw, posix=(os.name != "nt"))
        except ValueError:
            parts = raw.split()
        if not parts:
            return {"success": False, "error": "Empty command."}
        head = parts[0].lower().replace(".exe", "")
        if head in {"pip", "pip3"}:
            cmd = [py, "-m", "pip"] + parts[1:]
        elif head in {"python", "python3", "py"}:
            cmd = [py] + parts[1:]
        elif head in {"pytest"}:
            cmd = [py, "-m", "pytest"] + parts[1:]
        else:
            return {
                "success": False,
                "error": "Only pip / python / pytest commands are allowed in the sandbox.",
                "got": raw,
            }

        try:
            proc = _run(cmd, timeout=int(timeout or 90), cwd=str(SKILLS_DIR.parent))
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out after {timeout}s", "cmd": cmd}
        except Exception as e:
            return {"success": False, "error": str(e), "cmd": cmd}

        out = (proc.stdout or "")[-3000:]
        err = (proc.stderr or "")[-2000:]
        return {
            "success": proc.returncode == 0,
            "returncode": proc.returncode,
            "cmd": cmd,
            "stdout": out,
            "stderr": err,
        }

    def _index_disk_skills(self) -> dict[str, list[str]]:
        """Scan skills/*.py with AST only — never import into TITAN."""
        summary: dict[str, list[str]] = {}
        for skill_file in SKILLS_DIR.glob("*.py"):
            if skill_file.name.startswith("_") or skill_file.name == "__init__.py":
                continue
            try:
                code = skill_file.read_text(encoding="utf-8")
                funcs = self._public_functions(code)
                summary[skill_file.stem] = funcs
                self.loaded_skills[skill_file.stem] = {
                    "functions": funcs,
                    "requirements": self._extract_requirements(code),
                }
            except Exception as e:
                print(f"[SkillEngine] skip {skill_file.name}: {e}")
        if summary:
            print(f"[SkillEngine] indexed {len(summary)} skill(s): {list(summary)}")
        return summary

    # backward-compat alias
    def load_all_saved_skills(self) -> dict[str, list[str]]:
        return self._index_disk_skills()


skill_engine = SkillEngine()
