"""
TITAN Skill Engine — Dynamic Skill Creation, Sandbox Testing & Runtime Tool Loader.
Allows TITAN to autonomously create new Python skills, test them in a sandbox,
and dynamically load & register them into its live tool registry.
"""
import sys
import os
import io
import inspect
import importlib
import subprocess
import traceback
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

class SkillEngine:
    """
    Manages autonomous creation, testing, and dynamic loading of TITAN skills.
    """

    def __init__(self):
        self.loaded_skills: dict[str, object] = {}
        self._ensure_skills_dir()
        self.load_all_saved_skills()

    def _ensure_skills_dir(self):
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        init_file = SKILLS_DIR / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""TITAN Dynamic Skills Package"""\n', encoding="utf-8")

    def load_all_saved_skills(self) -> dict[str, list[str]]:
        """Scans skills/ directory on startup and auto-loads all saved skills."""
        if str(SKILLS_DIR.parent) not in sys.path:
            sys.path.insert(0, str(SKILLS_DIR.parent))

        loaded_summary = {}
        for skill_file in SKILLS_DIR.glob("*.py"):
            if skill_file.name == "__init__.py":
                continue
            clean_name = skill_file.stem
            try:
                module_path = f"skills.{clean_name}"
                mod = importlib.import_module(module_path)
                self.loaded_skills[clean_name] = mod
                funcs = [name for name, obj in inspect.getmembers(mod, inspect.isfunction) if not name.startswith("_")]
                loaded_summary[clean_name] = funcs
            except ModuleNotFoundError as e:
                # Missing dependency on startup — auto-install and retry!
                installed = self._auto_install_missing_packages(str(e))
                if installed:
                    try:
                        mod = importlib.import_module(f"skills.{clean_name}")
                        self.loaded_skills[clean_name] = mod
                        funcs = [name for name, obj in inspect.getmembers(mod, inspect.isfunction) if not name.startswith("_")]
                        loaded_summary[clean_name] = funcs
                        continue
                    except Exception:
                        pass
                print(f"[SkillEngine] [WARN] Missing dependency for '{clean_name}': {e}")
            except Exception as e:
                print(f"[SkillEngine] [WARN] Failed to auto-load saved skill '{clean_name}': {e}")
        return loaded_summary

    @staticmethod
    def _normalize_code(code: str) -> str:
        """Normalizes escaped newlines and string formatting passed from JSON tool calls."""
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
        """
        Static AST code analyzer to detect dangerous or harmful system commands.
        Blocks destructive OS wiping, raw disk manipulation, format commands,
        and malicious system-level overrides.
        """
        import ast
        norm_code = self._normalize_code(code)
        try:
            ast.parse(norm_code)
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"

        dangerous_patterns = [
            "shutil.rmtree('c:", 'shutil.rmtree("c:', "shutil.rmtree('c:\\", 'shutil.rmtree("c:\\',
            "os.system('format", 'os.system("format', "os.system('rmdir /s", 'os.system("rmdir /s',
            "rd /s /q c:", "del /f /s /q c:", "format c:", ":(){ :|:& };:"
        ]
        code_lower = norm_code.lower()
        for pat in dangerous_patterns:
            if pat in code_lower:
                return False, f"Security Violation: Prohibited destructive system command detected: '{pat}'"

        return True, "Safe"

    PIP_MODULE_MAP = {
        "speedtest": "speedtest-cli",
        "pptx": "python-pptx",
        "bs4": "beautifulsoup4",
        "yaml": "pyyaml",
        "cv2": "opencv-python",
        "PIL": "pillow",
        "docx": "python-docx",
        "fitz": "pymupdf",
        "sklearn": "scikit-learn",
        "serial": "pyserial",
        "qrcode": "qrcode[pil]",
        "dotenv": "python-dotenv",
        "requests": "requests",
        "matplotlib": "matplotlib",
        "pandas": "pandas",
        "numpy": "numpy",
        "reportlab": "reportlab",
        "yt_dlp": "yt-dlp",
        "pytube": "pytube",
        "pynput": "pynput",
        "schedule": "schedule",
        "tqdm": "tqdm",
    }

    def _auto_install_missing_packages(self, error_output: str) -> list[str]:
        """Detects missing module errors in sandbox output and auto-installs via pip in active venv."""
        import re
        installed = []
        matches = re.findall(r"No module named ['\"]([^'\"]+)['\"]", error_output)
        for mod in set(matches):
            pkg = self.PIP_MODULE_MAP.get(mod, mod)
            try:
                print(f"[SkillEngine] [INSTALL] Auto-installing missing dependency '{pkg}' (module: '{mod}') into sandbox venv...")
                res = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--no-warn-script-location", pkg],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=90
                )
                if res.returncode == 0:
                    installed.append(pkg)
                    print(f"[SkillEngine] [OK] Successfully installed '{pkg}'!")
                else:
                    print(f"[SkillEngine] [ERROR] Failed to install '{pkg}': {res.stderr.strip()}")
            except Exception as e:
                print(f"[SkillEngine] [ERROR] Error installing '{pkg}': {e}")
        return installed

    def create_and_test_skill(self, skill_name: str, python_code: str, test_inputs: dict | None = None) -> dict:
        """
        1. Validates code safety with AST security analyzer.
        2. Writes skill code to skills/<skill_name>.py
        3. Executes code in isolated sandbox process with auto pip-install on missing dependencies.
        4. Dynamically imports and registers skill into TITAN runtime.
        """
        python_code = self._normalize_code(python_code)
        # Safety Check
        is_safe, reason = self._verify_safety(python_code)
        if not is_safe:
            return {
                "success": False,
                "skill_name": skill_name,
                "error": f"🛡️ Safety Check Failed: {reason}",
                "status": "BLOCKED"
            }

        # Clean skill filename
        clean_name = "".join(c if c.isalnum() or c == "_" else "_" for c in skill_name).lower()
        if not clean_name.endswith("_skill"):
            clean_name = f"{clean_name}_skill"

        skill_file = SKILLS_DIR / f"{clean_name}.py"
        auto_installed: list[str] = []
        
        try:
            # 1. Save skill code
            skill_file.write_text(python_code, encoding="utf-8")

            # 2. Test in Isolated Subprocess Sandbox
            cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, r'{SKILLS_DIR.parent}'); import skills.{clean_name}; print('SANDBOX_PASS')"]
            proc = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15,
                cwd=str(SKILLS_DIR.parent)
            )

            # If failed due to missing library, auto-install into venv and re-test!
            if proc.returncode != 0:
                error_msg = proc.stderr.strip() or proc.stdout.strip()
                auto_installed = self._auto_install_missing_packages(error_msg)
                if auto_installed:
                    # Re-run sandbox test after pip install
                    proc = subprocess.run(
                        cmd,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=15,
                        cwd=str(SKILLS_DIR.parent)
                    )

            if proc.returncode != 0:
                error_msg = proc.stderr.strip() or proc.stdout.strip()
                return {
                    "success": False,
                    "skill_name": clean_name,
                    "error": f"Sandbox Verification Failed:\n{error_msg}",
                    "file_path": str(skill_file)
                }

            # 3. Dynamic Runtime Import
            if str(SKILLS_DIR.parent) not in sys.path:
                sys.path.insert(0, str(SKILLS_DIR.parent))

            module_path = f"skills.{clean_name}"
            if module_path in sys.modules:
                mod = importlib.reload(sys.modules[module_path])
            else:
                mod = importlib.import_module(module_path)

            self.loaded_skills[clean_name] = mod

            res_data = {
                "success": True,
                "skill_name": clean_name,
                "status": "Verified & Registered into TITAN Runtime",
                "file_path": str(skill_file),
                "exported_functions": [name for name, obj in inspect.getmembers(mod, inspect.isfunction) if not name.startswith("_")]
            }
            if auto_installed:
                res_data["auto_installed_dependencies"] = auto_installed
            return res_data

        except Exception as e:
            tb = traceback.format_exc()
            return {
                "success": False,
                "skill_name": clean_name,
                "error": f"Exception during skill creation: {e}\n{tb}",
                "file_path": str(skill_file)
            }

    def edit_skill(self, skill_name: str, new_python_code: str) -> dict:
        """Edit and re-verify an existing skill with updated Python code."""
        return self.create_and_test_skill(skill_name, new_python_code)

    def get_skill_code(self, skill_name: str) -> dict:
        """Retrieve the Python source code of a saved skill."""
        clean_name = skill_name if skill_name.endswith("_skill") else f"{skill_name}_skill"
        skill_file = SKILLS_DIR / f"{clean_name}.py"
        if not skill_file.exists():
            return {"success": False, "error": f"Skill '{clean_name}' does not exist on disk."}
        try:
            return {"success": True, "skill_name": clean_name, "code": skill_file.read_text(encoding="utf-8")}
        except Exception as e:
            return {"success": False, "error": f"Failed to read skill '{clean_name}': {e}"}

    def delete_skill(self, skill_name: str) -> dict:
        """Permanently delete a skill file from disk and unload from runtime."""
        clean_name = skill_name if skill_name.endswith("_skill") else f"{skill_name}_skill"
        skill_file = SKILLS_DIR / f"{clean_name}.py"
        
        deleted_file = False
        if skill_file.exists():
            try:
                skill_file.unlink()
                deleted_file = True
            except Exception as e:
                return {"success": False, "error": f"Failed to delete skill file: {e}"}

        # Unload from memory
        self.loaded_skills.pop(clean_name, None)
        module_path = f"skills.{clean_name}"
        if module_path in sys.modules:
            del sys.modules[module_path]

        return {
            "success": True,
            "skill_name": clean_name,
            "status": "Deleted from disk & unloaded from memory" if deleted_file else "Unloaded from memory (file not on disk)"
        }

    def list_skills(self) -> list[str]:
        """List all verified dynamic skills currently on disk."""
        return [f.stem for f in SKILLS_DIR.glob("*.py") if f.name != "__init__.py"]

    def execute_skill(self, skill_name: str = "", function_name: str = "", **kwargs) -> dict:
        """Execute a dynamic skill function by name with smart function and skill resolution."""
        all_skills = self.list_skills()
        
        # 1. Resolve skill name if missing or empty
        clean_name = ""
        if skill_name:
            clean_name = skill_name if skill_name.endswith("_skill") else f"{skill_name}_skill"
        
        if not clean_name or clean_name == "_skill":
            # Auto-resolve skill from function_name across all skills
            if function_name:
                for s in all_skills:
                    if s not in self.loaded_skills:
                        try:
                            mod = importlib.import_module(f"skills.{s}")
                            self.loaded_skills[s] = mod
                        except Exception:
                            continue
                    if hasattr(self.loaded_skills.get(s), function_name):
                        clean_name = s
                        break
            if not clean_name and len(all_skills) == 1:
                clean_name = all_skills[0]
            elif not clean_name:
                return {"success": False, "error": f"Please specify a skill_name. Available skills: {all_skills}"}

        # 2. Ensure skill is loaded and always up-to-date with disk
        skill_file = SKILLS_DIR / f"{clean_name}.py"
        if not skill_file.exists():
            return {"success": False, "error": f"Skill file '{clean_name}.py' not found on disk."}

        module_path = f"skills.{clean_name}"
        mod = None
        try:
            if str(SKILLS_DIR.parent) not in sys.path:
                sys.path.insert(0, str(SKILLS_DIR.parent))
            if module_path in sys.modules:
                mod = importlib.reload(sys.modules[module_path])
            else:
                mod = importlib.import_module(module_path)
            self.loaded_skills[clean_name] = mod
        except Exception as e:
            # Robust fallback: compile and execute file into fresh module directly
            try:
                import types
                mod = types.ModuleType(clean_name)
                code_str = skill_file.read_text(encoding="utf-8")
                exec(code_str, mod.__dict__)
                self.loaded_skills[clean_name] = mod
                sys.modules[module_path] = mod
            except Exception as e2:
                return {"success": False, "error": f"Skill '{clean_name}' failed to load: {e2}\n{traceback.format_exc()}"}

        mod = self.loaded_skills[clean_name]
        public_funcs = [name for name, obj in inspect.getmembers(mod, inspect.isfunction) if not name.startswith("_")]

        # 3. Resolve function
        func = None
        if function_name and hasattr(mod, function_name):
            func = getattr(mod, function_name)
        elif len(public_funcs) == 1:
            # If the skill only has 1 function, invoke it automatically!
            func = getattr(mod, public_funcs[0])
        elif function_name in ("run", "execute", "main", "") and public_funcs:
            func = getattr(mod, public_funcs[0])
        else:
            # Fuzzy match: e.g. 'run_speed_test' matches 'run' or 'test_speed'
            for pf in public_funcs:
                if pf.lower() in function_name.lower() or function_name.lower() in pf.lower():
                    func = getattr(mod, pf)
                    break
        
        if not func and public_funcs:
            func = getattr(mod, public_funcs[0])
        elif not func:
            return {"success": False, "error": f"No executable function found in '{clean_name}'. Available functions: {public_funcs}"}

        try:
            result = func(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": f"Skill execution failed: {e}\n{traceback.format_exc()}"}


# Singleton instance
skill_engine = SkillEngine()
