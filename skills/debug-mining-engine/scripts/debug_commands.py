#!/usr/bin/env python3
"""
Debug Mining Engine - Debug Commands
Handles /debug-start, /debug-end, /debug-save, /debug-discard commands
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import monitor
sys.path.insert(0, str(Path(__file__).parent))
from monitor import DebugMonitor

def start_command(description):
    """Handle /debug-start command"""
    monitor = DebugMonitor()
    session_id = monitor.start_session(description=description, manual=True)
    print(f"✅ Debugging session started: {session_id}")
    print(f"   Description: {description}")
    print(f"   Run '/debug-end' when done")

def end_command():
    """Handle /debug-end command"""
    monitor = DebugMonitor()
    
    # Load current session
    current_session_file = Path("/home/ubuntu/debug-mining/current_session.json")
    if not current_session_file.exists():
        print("❌ No active debugging session")
        print("   Start one with: /debug-start \"description\"")
        return
    
    session_id = monitor.end_session()
    if session_id:
        print(f"✅ Session ended: {session_id}")
        print(f"   Analyzing session...")
        print(f"   Generated assets will appear in:")
        print(f"   - /home/ubuntu/skills/skills/debugging-patterns/")
        print(f"   - /home/ubuntu/debug-snippets/")
        print(f"   - /home/ubuntu/debug-patterns/")

def save_command():
    """Handle /debug-save command"""
    monitor = DebugMonitor()
    session_id = monitor.end_session()
    if session_id:
        print(f"✅ Session saved: {session_id}")

def discard_command():
    """Handle /debug-discard command"""
    current_session_file = Path("/home/ubuntu/debug-mining/current_session.json")
    if current_session_file.exists():
        current_session_file.unlink()
        print("✅ Session discarded")
    else:
        print("❌ No active session to discard")

def main():
    if len(sys.argv) < 2:
        print("Usage: debug_commands.py {start|end|save|discard} [args...]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        description = sys.argv[2] if len(sys.argv) > 2 else "Manual debugging session"
        start_command(description)
    elif command == "end":
        end_command()
    elif command == "save":
        save_command()
    elif command == "discard":
        discard_command()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
