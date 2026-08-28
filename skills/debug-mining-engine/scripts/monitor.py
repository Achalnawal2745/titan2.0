#!/usr/bin/env python3
"""
Debug Mining Engine - Monitor
Detects errors and captures debugging sessions automatically
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

# Configuration
DEBUG_SESSIONS_DIR = Path("/home/ubuntu/debug-sessions")
MONITOR_LOG = Path("/home/ubuntu/debug-mining/monitor.log")
CURRENT_SESSION_FILE = Path("/home/ubuntu/debug-mining/current_session.json")

# Error patterns to detect
ERROR_PATTERNS = [
    r'error:', r'Error:', r'ERROR:',
    r'exception', r'Exception', r'EXCEPTION',
    r'failed', r'Failed', r'FAILED',
    r'not found', r'Not found', r'NOT FOUND',
    r'❌', r'✗', r'✘',
    r'traceback', r'Traceback',
    r'cannot', r'Cannot', r'CANNOT',
    r'unable', r'Unable', r'UNABLE',
    r'invalid', r'Invalid', r'INVALID',
]

class DebuggingSession:
    """Represents a debugging session"""
    
    def __init__(self, session_id=None):
        self.session_id = session_id or self._generate_session_id()
        self.start_time = datetime.now()
        self.end_time = None
        self.commands = []
        self.error_detected = False
        self.error_info = {}
        self.solution_found = False
        self.context = {}
        
    def _generate_session_id(self):
        """Generate unique session ID"""
        return f"debug_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    
    def add_command(self, command, exit_code, output="", pwd=""):
        """Add a command to the session"""
        self.commands.append({
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'exit_code': exit_code,
            'output': output,
            'pwd': pwd
        })
    
    def set_error(self, error_message, error_type="Unknown"):
        """Mark error detected"""
        self.error_detected = True
        self.error_info = {
            'message': error_message,
            'type': error_type,
            'timestamp': datetime.now().isoformat()
        }
    
    def mark_solution_found(self):
        """Mark solution found"""
        self.solution_found = True
        self.end_time = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary"""
        duration = None
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': duration,
            'commands': self.commands,
            'error_detected': self.error_detected,
            'error_info': self.error_info,
            'solution_found': self.solution_found,
            'context': self.context
        }
    
    def save(self):
        """Save session to file"""
        # Create directory for today
        today = datetime.now().strftime('%Y-%m-%d')
        session_dir = DEBUG_SESSIONS_DIR / today
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save session
        session_file = session_dir / f"{self.session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return session_file

class DebugMonitor:
    """Monitors shell for debugging activity"""
    
    def __init__(self):
        self.current_session = None
        self.error_patterns = [re.compile(p, re.IGNORECASE) for p in ERROR_PATTERNS]
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        DEBUG_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        MONITOR_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    def _log(self, message):
        """Log message to file"""
        with open(MONITOR_LOG, 'a') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"[{timestamp}] {message}\n")
    
    def detect_error(self, exit_code, command, output=""):
        """Detect if command resulted in error"""
        # Check exit code
        if exit_code != 0:
            return True, "Non-zero exit code"
        
        # Check output for error patterns
        for pattern in self.error_patterns:
            if pattern.search(output):
                return True, f"Error pattern matched: {pattern.pattern}"
        
        return False, None
    
    def start_session(self, description="", manual=False):
        """Start a new debugging session"""
        if self.current_session:
            self._log("Warning: Starting new session while one is active")
        
        self.current_session = DebuggingSession()
        self.current_session.context['description'] = description
        self.current_session.context['manual'] = manual
        
        # Save current session reference
        with open(CURRENT_SESSION_FILE, 'w') as f:
            json.dump({
                'session_id': self.current_session.session_id,
                'start_time': self.current_session.start_time.isoformat()
            }, f)
        
        self._log(f"Session started: {self.current_session.session_id} (manual={manual})")
        
        if manual:
            print(f"[Debug Mining: Manual capture started - \"{description}\"]")
        else:
            print(f"[Debug Mining: Capture started]")
        
        return self.current_session.session_id
    
    def end_session(self):
        """End current debugging session"""
        if not self.current_session:
            print("[Debug Mining: No active session]")
            return None
        
        self.current_session.mark_solution_found()
        session_file = self.current_session.save()
        
        self._log(f"Session ended: {self.current_session.session_id}")
        
        # Clear current session
        session_id = self.current_session.session_id
        self.current_session = None
        
        if CURRENT_SESSION_FILE.exists():
            CURRENT_SESSION_FILE.unlink()
        
        print(f"[Debug Mining: Session saved to {session_file}]")
        
        # Trigger analysis
        self._trigger_analysis(session_id)
        
        return session_id
    
    def _trigger_analysis(self, session_id):
        """Trigger analysis of completed session"""
        print(f"[Debug Mining: Analyzing session...]")
        # This would call analyzer.py in a real implementation
        # For now, just log it
        self._log(f"Analysis triggered for session: {session_id}")
    
    def record_command(self, exit_code, command, output="", pwd=""):
        """Record a command execution"""
        # Detect error
        is_error, error_reason = self.detect_error(exit_code, command, output)
        
        # If error detected and no active session, start one
        if is_error and not self.current_session:
            self.start_session(description="Auto-detected error", manual=False)
            self.current_session.set_error(error_reason, "Auto-detected")
        
        # If active session, record command
        if self.current_session:
            self.current_session.add_command(command, exit_code, output, pwd)
            
            # If this command succeeded after errors, might be solution
            if not is_error and self.current_session.error_detected:
                self._log(f"Potential solution detected: {command}")
                # Could prompt user here in interactive mode
        
        return is_error

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Debug Mining Monitor')
    parser.add_argument('--exit-code', type=int, help='Exit code of last command')
    parser.add_argument('--command', type=str, help='Last command executed')
    parser.add_argument('--output', type=str, default="", help='Command output')
    parser.add_argument('--pwd', type=str, default="", help='Working directory')
    parser.add_argument('--test', action='store_true', help='Run test')
    
    args = parser.parse_args()
    
    monitor = DebugMonitor()
    
    if args.test:
        print("Testing Debug Monitor...")
        print(f"✅ Directories exist: {DEBUG_SESSIONS_DIR.exists()}")
        print(f"✅ Can write logs: {MONITOR_LOG.parent.exists()}")
        print("✅ Monitor ready")
        return
    
    if args.exit_code is not None and args.command:
        is_error = monitor.record_command(
            args.exit_code,
            args.command,
            args.output,
            args.pwd
        )
        
        if is_error:
            sys.exit(1)
    else:
        print("Usage: monitor.py --exit-code CODE --command COMMAND [--output OUTPUT] [--pwd PWD]")
        sys.exit(1)

if __name__ == "__main__":
    main()
