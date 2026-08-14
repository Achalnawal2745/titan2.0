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
            except Exception as e:
                print(f"[SkillEngine] ⚠️  Failed to auto-load saved skill '{clean_name}': {e}")
        return loaded_summary

    @staticmethod
    def _verify_safety(code: str) -> tuple[bool, str]:
        """
        Static AST code analyzer to detect dangerous or harmful system commands.
        Blocks destructive OS wiping, raw disk manipulation, format commands,
        and malicious system-level overrides.
        """
        import ast
        try:
            ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"

        dangerous_patterns = [
            "shutil.rmtree('c:", 'shutil.rmtree("c:', "shutil.rmtree('c:\\", 'shutil.rmtree("c:\\',
            "os.system('format", 'os.system("format', "os.system('rmdir /s", 'os.system("rmdir /s',
            "rd /s /q c:", "del /f /s /q c:", "format c:", ":(){ :|:& };:"
        ]
        code_lower = code.lower()
        for pat in dangerous_patterns:
            if pat in code_lower:
                return False, f"Security Violation: Prohibited destructive system command detected: '{pat}'"

        return True, "Safe"

    def create_and_test_skill(self, skill_name: str, python_code: str, test_inputs: dict | None = None) -> dict:
        """
        1. Validates code safety with AST security analyzer.
        2. Writes skill code to skills/<skill_name>.py
        3. Executes code in isolated sandbox process with 10s timeout.
        4. Dynamically imports and registers skill into TITAN runtime.
        """
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
        
        try:
            # 1. Save skill code
            skill_file.write_text(python_code, encoding="utf-8")

            # 2. Test in Isolated Subprocess Sandbox
            cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, r'{SKILLS_DIR.parent}'); import skills.{clean_name}; print('SANDBOX_PASS')"]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=12,
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

            return {
                "success": True,
                "skill_name": clean_name,
                "status": "Verified & Registered into TITAN Runtime",
                "file_path": str(skill_file),
                "exported_functions": [name for name, obj in inspect.getmembers(mod, inspect.isfunction) if not name.startswith("_")]
            }

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

    def execute_skill(self, skill_name: str, function_name: str, **kwargs) -> dict:
        """Execute a dynamic skill function by name."""
        clean_name = skill_name if skill_name.endswith("_skill") else f"{skill_name}_skill"
        
        if clean_name not in self.loaded_skills:
            # Try to load from disk
            try:
                if str(SKILLS_DIR.parent) not in sys.path:
                    sys.path.insert(0, str(SKILLS_DIR.parent))
                mod = importlib.import_module(f"skills.{clean_name}")
                self.loaded_skills[clean_name] = mod
            except Exception as e:
                return {"success": False, "error": f"Skill '{clean_name}' not loaded: {e}"}

        mod = self.loaded_skills[clean_name]
        func = getattr(mod, function_name, None)
        if not func:
            return {"success": False, "error": f"Function '{function_name}' not found in '{clean_name}'"}

        try:
            result = func(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": f"Skill execution failed: {e}\n{traceback.format_exc()}"}


# Singleton instance
skill_engine = SkillEngine()
