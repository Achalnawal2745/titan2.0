"""
ui_automation.py — TITAN 2.0 Background UI Layer
-------------------------------------------------
Uses Windows UIAutomation (pywinauto) to interact with desktop apps.
This solves the "stealing the mouse" problem.

Instead of taking a screenshot and physically moving the mouse, this code
reads the accessibility tree of an app and sends programmatic clicks directly
to buttons, often without bringing the window to the front.
"""

import pyautogui
import pyperclip
import time
import re
from colorama import Fore, Style, init

init(autoreset=True)
pyautogui.FAILSAFE = False # Prevent crashes from jittery windows

def _log(msg: str, color=Fore.MAGENTA):
    print(f"{color}[UI-AUTO]{Style.RESET_ALL} {msg}")

def _get_app(app_name: str):
    """Helper to connect to a running app with multiple strategies."""
    from pywinauto import Application
    
    class_map = {
        "calculator": "ApplicationFrameWindow",
        "notepad": "Notepad",
        "chrome": "Chrome_WidgetWin_1"
    }
    
    for backend in ["uia", "win32"]:
        from pywinauto import Desktop
        try:
            name_lower = app_name.lower()
            search_title = f"(?i).*{re.escape(app_name)}.*"
            if "chrome" in name_lower: 
                search_title = "(?i).*(Google Chrome|Chrome|Profile).*" 
            
            _log(f"Hunting for window: {search_title} ({backend})", Fore.YELLOW)
            
            from pywinauto import Desktop
            wins = Desktop(backend=backend).windows(title_re=search_title, visible_only=True)
            if not wins:
                raise RuntimeError("No windows found")
            
            dlg = wins[0]
            
            import win32gui
            import win32con
            hwnd = dlg.handle
            
            _log(f"Found window: '{dlg.window_text()}' (Handle: {hwnd})", Fore.GREEN)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            
            from pywinauto import Application
            return Application(backend=backend).connect(handle=hwnd)
        except Exception as e:
            _log(f"Backend {backend} failed: {e}", Fore.RED)
            pass

        if name_lower in class_map:
            try:
                _log(f"Connecting via Class Name: {class_map[name_lower]}", Fore.YELLOW)
                app = Application(backend=backend).connect(class_name=class_map[name_lower], timeout=3)
                dlg = app.top_window()
                dlg.set_focus()
                return app
            except: pass

        try:
            process_name = f"{app_name}.exe" if not app_name.endswith(".exe") else app_name
            if "chrome" in name_lower: process_name = "chrome.exe"
            
            app = Application(backend=backend).connect(path=process_name, timeout=5)
            dlg = app.top_window()
            dlg.set_focus()
            return app
        except Exception:
            pass
            
    raise RuntimeError(f"Could not connect to '{app_name}'. Is it open and on the screen?")


def ui_click(app_name: str, element_name: str, index: int = 0) -> str:
    """
    Find an element by its text/name inside an app and click it programmatically.
    """
    _log(f"Attempting to click '{element_name}' (index {index}) in '{app_name}'")
    try:
        app = _get_app(app_name)
        dlg = app.top_window()
        element = dlg.child_window(title=element_name, found_index=index)
        
        if not element.exists():
            return f"❌ Could not find element '{element_name}' in {app_name}. TRY RUNNING 'ui_dump_tree' to see the actual names of elements on this screen."

        try:
            element.click_input()
            return f"✅ Clicked '{element_name}' at index {index} in {app_name}"
        except Exception as e:
            return f"❌ Failed to click '{element_name}' in {app_name}: {e}. TRY RUNNING 'ui_dump_tree' to refresh your view."

    except Exception as e:
        return f"❌ Error in ui_click process for '{app_name}': {e}"


def ui_type(app_name: str, element_name: str, text: str) -> str:
    """
    Find a text box and paste text into it (to avoid character repetition).
    """
    import pyperclip
    import time
    import win32gui
    import win32con

    _log(f"Writing into '{element_name}' in '{app_name}'")
    try:
        app = _get_app(app_name)
        dlg = app.top_window()
        hwnd = dlg.handle
        
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)
        dlg.set_focus()
        
        try:
            edit_area = None
            for control_type in ["Edit", "Document", "RichEditD2DPT"]:
                try:
                    edit_area = dlg.child_window(control_type=control_type, found_index=0)
                    if edit_area.exists(): break
                except: continue
            
            if edit_area and edit_area.exists():
                _log("Targeting specific Edit area...", Fore.YELLOW)
                edit_area.click_input()
            else:
                _log("No specific Edit area found, clicking center of window...", Fore.YELLOW)
                rect = dlg.rectangle()
                pyautogui.click(rect.left + (rect.width() // 2), rect.top + (rect.height() // 2))
        except:
            pass

        time.sleep(0.2)
        dlg.set_focus()
        
        pyperclip.copy(text)
        time.sleep(0.1)
        
        pyautogui.keyDown('ctrl')
        pyautogui.press('v')
        pyautogui.keyUp('ctrl')
        
        if len(text) < 50:
            pyautogui.press('enter')
            
        return f"✅ Text written into '{app_name}'"
        
    except Exception as e:
        return f"❌ Failed to type into '{element_name}' in '{app_name}': {e}"


def ui_get_text(app_name: str, element_name: str) -> str:
    """
    Extract text from a specific UI element using multiple fallback methods.
    """
    _log(f"Reading text from '{element_name}' in '{app_name}'")
    try:
        app = _get_app(app_name)
        dlg = app.top_window()
        
        element = dlg.child_window(title_re=f".*{re.escape(element_name)}.*", found_index=0)
        text = element.window_text()
        
        if not text:
            try:
                text = element.legacy_properties().get('Value', '')
            except: pass
            
        if not text:
            try:
                text = element.element_info.name
            except: pass

        if not text:
            return f"⚠️ Element found, but it appears empty. Try 'ui_dump_tree' to find a different element."
            
        return f"📄 Text: {text}"
        
    except Exception as e:
        return f"❌ Failed to read '{element_name}' in '{app_name}': {e}"


def ui_dump_tree(app_name: str, search_query: str = None) -> str:
    """
    Extract the accessibility tree, filtered for actionable items.
    """
    import io
    from contextlib import redirect_stdout
    try:
        app = _get_app(app_name)
        dlg = app.top_window()
        f = io.StringIO()
        with redirect_stdout(f):
            dlg.print_control_identifiers()
        
        full_tree = f.getvalue()
        lines = full_tree.splitlines()
        
        useful_types = ["Button", "Static", "Text", "ListItem", "MenuItem", "Edit", "Document", "Pane", "Group", "Image"]
        filtered_lines = []
        for line in lines:
            has_title = '"' in line
            if any(t in line for t in useful_types) or has_title or (search_query and search_query.lower() in line.lower()):
                filtered_lines.append(line)
        
        if not filtered_lines:
            return "\n".join(lines[:100]) + "\n... (raw tree shown due to empty filter)"
            
        output = "\n".join(filtered_lines)
        return f"🌳 FILTERED UI TREE FOR {app_name}:\n" + output[:4000]
    except Exception as e:
        return f"❌ Failed to dump tree: {e}"
