#!/usr/bin/env python3
"""
Debug Mining Engine - Analyzer
Extracts patterns and insights from captured debugging sessions
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter

class DebugSessionAnalyzer:
    """Analyzes debugging sessions to extract reusable patterns"""
    
    def __init__(self, session_file: str):
        self.session_file = session_file
        self.session_data = self._load_session()
        
    def _load_session(self) -> Dict:
        """Load session data from file"""
        with open(self.session_file, 'r') as f:
            return json.load(f)
    
    def analyze(self) -> Dict:
        """
        Perform complete analysis of debugging session
        
        Returns dict with:
        - error_pattern: What went wrong
        - root_cause: Why it happened
        - solution_pattern: How it was fixed
        - prevention_strategy: How to avoid it
        - reusable_code: Code to reuse
        - skill_type: Type of skill to generate
        - confidence: Confidence score (0-1)
        """
        
        analysis = {
            "session_id": self.session_data.get("session_id"),
            "timestamp": self.session_data.get("timestamp"),
            "duration": self._calculate_duration(),
            "error_pattern": self._extract_error_pattern(),
            "root_cause": self._identify_root_cause(),
            "solution_pattern": self._extract_solution_pattern(),
            "prevention_strategy": self._generate_prevention_strategy(),
            "reusable_code": self._extract_reusable_code(),
            "skill_type": self._determine_skill_type(),
            "confidence": self._calculate_confidence(),
            "tags": self._generate_tags(),
            "related_skills": self._find_related_skills()
        }
        
        return analysis
    
    def _calculate_duration(self) -> float:
        """Calculate debugging session duration in minutes"""
        commands = self.session_data.get("commands", [])
        if len(commands) < 2:
            return 0.0
        
        start_time = datetime.fromisoformat(commands[0]["timestamp"])
        end_time = datetime.fromisoformat(commands[-1]["timestamp"])
        duration = (end_time - start_time).total_seconds() / 60
        return round(duration, 2)
    
    def _extract_error_pattern(self) -> Dict:
        """
        Extract the error pattern from failed commands
        
        Returns:
        - error_type: Classification of error
        - error_message: The actual error message
        - error_context: What was being attempted
        - frequency: How common this error is
        """
        commands = self.session_data.get("commands", [])
        errors = [cmd for cmd in commands if cmd.get("exit_code", 0) != 0]
        
        if not errors:
            return {"error_type": "unknown", "error_message": "", "error_context": ""}
        
        # Get first error (usually the root cause)
        first_error = errors[0]
        error_output = first_error.get("output", "")
        
        # Classify error type
        error_type = self._classify_error(error_output)
        
        # Extract clean error message
        error_message = self._extract_error_message(error_output)
        
        # Get context from command
        error_context = first_error.get("command", "")
        
        return {
            "error_type": error_type,
            "error_message": error_message,
            "error_context": error_context,
            "total_errors": len(errors),
            "retry_count": len(errors) - 1
        }
    
    def _classify_error(self, error_output: str) -> str:
        """Classify error into categories"""
        error_lower = error_output.lower()
        
        # Database errors
        if any(kw in error_lower for kw in ["table", "database", "sql", "query", "schema"]):
            return "database"
        
        # Network errors
        if any(kw in error_lower for kw in ["connection", "timeout", "network", "http", "api"]):
            return "network"
        
        # File system errors
        if any(kw in error_lower for kw in ["file not found", "permission denied", "directory", "path"]):
            return "filesystem"
        
        # Import/dependency errors
        if any(kw in error_lower for kw in ["import", "module", "package", "dependency"]):
            return "dependency"
        
        # Authentication errors
        if any(kw in error_lower for kw in ["auth", "credential", "token", "permission"]):
            return "authentication"
        
        # Configuration errors
        if any(kw in error_lower for kw in ["config", "setting", "environment", "variable"]):
            return "configuration"
        
        return "general"
    
    def _extract_error_message(self, error_output: str) -> str:
        """Extract clean error message from output"""
        lines = error_output.strip().split('\n')
        
        # Look for lines starting with Error:, Exception:, etc.
        for line in lines:
            if re.match(r'^(Error|Exception|Failed|Fatal):', line, re.IGNORECASE):
                return line.strip()
        
        # If no explicit error line, return first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()[:200]  # Limit length
        
        return error_output[:200]
    
    def _identify_root_cause(self) -> Dict:
        """
        Identify the root cause of the error
        
        Returns:
        - cause: Description of root cause
        - evidence: Supporting evidence
        - category: Category of root cause
        """
        error_pattern = self._extract_error_pattern()
        commands = self.session_data.get("commands", [])
        
        error_type = error_pattern["error_type"]
        error_message = error_pattern["error_message"]
        
        # Analyze command progression to understand root cause
        failed_commands = [cmd for cmd in commands if cmd.get("exit_code", 0) != 0]
        successful_commands = [cmd for cmd in commands if cmd.get("exit_code", 0) == 0]
        
        # Common root causes by error type
        root_causes = {
            "database": "Schema mismatch or missing table/column",
            "network": "Connection timeout or unreachable endpoint",
            "filesystem": "Missing file, directory, or insufficient permissions",
            "dependency": "Missing or incompatible package/module",
            "authentication": "Invalid or missing credentials",
            "configuration": "Incorrect or missing configuration value"
        }
        
        cause = root_causes.get(error_type, "Unknown root cause")
        
        return {
            "cause": cause,
            "evidence": error_message,
            "category": error_type,
            "attempts_before_fix": len(failed_commands)
        }
    
    def _extract_solution_pattern(self) -> Dict:
        """
        Extract the solution pattern from successful commands
        
        Returns:
        - solution_type: Type of solution applied
        - solution_steps: Steps taken to fix
        - final_command: The command that worked
        - key_changes: What changed from error to success
        """
        commands = self.session_data.get("commands", [])
        
        # Find transition from failure to success
        failed_commands = []
        successful_command = None
        
        for i, cmd in enumerate(commands):
            if cmd.get("exit_code", 0) != 0:
                failed_commands.append(cmd)
            elif failed_commands:  # First success after failures
                successful_command = cmd
                break
        
        if not successful_command:
            return {"solution_type": "unknown", "solution_steps": [], "final_command": ""}
        
        # Analyze what changed
        if failed_commands:
            last_failed = failed_commands[-1]["command"]
            successful = successful_command["command"]
            key_changes = self._diff_commands(last_failed, successful)
        else:
            key_changes = []
        
        solution_type = self._classify_solution(successful_command, key_changes)
        
        return {
            "solution_type": solution_type,
            "solution_steps": [cmd["command"] for cmd in failed_commands + [successful_command]],
            "final_command": successful_command["command"],
            "key_changes": key_changes
        }
    
    def _diff_commands(self, cmd1: str, cmd2: str) -> List[str]:
        """Find key differences between two commands"""
        changes = []
        
        # Check for added flags
        flags1 = set(re.findall(r'--?\w+', cmd1))
        flags2 = set(re.findall(r'--?\w+', cmd2))
        added_flags = flags2 - flags1
        if added_flags:
            changes.append(f"Added flags: {', '.join(added_flags)}")
        
        # Check for changed arguments
        if cmd1.split()[0] == cmd2.split()[0]:  # Same base command
            if len(cmd2.split()) > len(cmd1.split()):
                changes.append("Added arguments")
            elif len(cmd2.split()) < len(cmd1.split()):
                changes.append("Removed arguments")
        
        return changes
    
    def _classify_solution(self, successful_command: Dict, key_changes: List[str]) -> str:
        """Classify the type of solution"""
        command = successful_command["command"]
        
        if "--validate" in command or "--check" in command:
            return "validation"
        elif "--retry" in command or "retry" in command.lower():
            return "retry_with_backoff"
        elif any("install" in change.lower() for change in key_changes):
            return "dependency_installation"
        elif "--fix" in command or "--repair" in command:
            return "automatic_fix"
        else:
            return "configuration_change"
    
    def _generate_prevention_strategy(self) -> Dict:
        """Generate strategy to prevent this error in the future"""
        error_pattern = self._extract_error_pattern()
        solution_pattern = self._extract_solution_pattern()
        
        strategies = {
            "database": "Validate schema before querying",
            "network": "Add retry logic with exponential backoff",
            "filesystem": "Check file existence before operations",
            "dependency": "Use dependency validation scripts",
            "authentication": "Validate credentials before API calls",
            "configuration": "Use configuration validation at startup"
        }
        
        error_type = error_pattern["error_type"]
        
        return {
            "strategy": strategies.get(error_type, "Add error handling and validation"),
            "implementation": f"Create validation script for {error_type} operations",
            "automation": f"Add {error_type} checks to CI/CD pipeline"
        }
    
    def _extract_reusable_code(self) -> Dict:
        """Extract reusable code snippets from solution"""
        solution_pattern = self._extract_solution_pattern()
        final_command = solution_pattern["final_command"]
        
        # Generate reusable script
        script_content = f"""#!/bin/bash
# Auto-generated from debugging session
# {self.session_data.get('description', 'Debugging session')}

{final_command}
"""
        
        return {
            "script": script_content,
            "command": final_command,
            "language": "bash"
        }
    
    def _determine_skill_type(self) -> str:
        """
        Determine what type of skill to generate
        
        Returns: "full_skill", "code_snippet", or "pattern_guide"
        """
        error_pattern = self._extract_error_pattern()
        duration = self._calculate_duration()
        
        # Complex issues → full skill
        if duration > 10 or error_pattern["retry_count"] > 3:
            return "full_skill"
        
        # Quick fixes → code snippet
        elif duration < 2 and error_pattern["retry_count"] <= 1:
            return "code_snippet"
        
        # Medium complexity → pattern guide
        else:
            return "pattern_guide"
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score for analysis (0-1)"""
        commands = self.session_data.get("commands", [])
        
        # Factors that increase confidence
        has_clear_error = bool(self._extract_error_pattern()["error_message"])
        has_clear_solution = bool(self._extract_solution_pattern()["final_command"])
        has_multiple_attempts = len(commands) > 2
        has_description = bool(self.session_data.get("description"))
        
        confidence = 0.0
        if has_clear_error:
            confidence += 0.3
        if has_clear_solution:
            confidence += 0.3
        if has_multiple_attempts:
            confidence += 0.2
        if has_description:
            confidence += 0.2
        
        return round(confidence, 2)
    
    def _generate_tags(self) -> List[str]:
        """Generate tags for categorization"""
        error_pattern = self._extract_error_pattern()
        solution_pattern = self._extract_solution_pattern()
        
        tags = [
            error_pattern["error_type"],
            solution_pattern["solution_type"],
            "debugging",
            "auto-generated"
        ]
        
        # Add language tags
        commands = self.session_data.get("commands", [])
        for cmd in commands:
            command = cmd.get("command", "")
            if command.startswith("python"):
                tags.append("python")
            elif command.startswith("npm") or command.startswith("node"):
                tags.append("nodejs")
            elif command.startswith("docker"):
                tags.append("docker")
        
        return list(set(tags))  # Remove duplicates
    
    def _find_related_skills(self) -> List[str]:
        """Find related skills in the arsenal"""
        # This would query the skill registry
        # For now, return empty list
        return []
    
    def save_analysis(self, output_file: Optional[str] = None) -> str:
        """Save analysis to file"""
        analysis = self.analyze()
        
        if output_file is None:
            session_id = self.session_data.get("session_id", "unknown")
            output_file = f"/home/ubuntu/debug-sessions/analyses/{session_id}_analysis.json"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return output_file


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: analyzer.py <session_file>")
        sys.exit(1)
    
    session_file = sys.argv[1]
    
    if not os.path.exists(session_file):
        print(f"Error: Session file not found: {session_file}")
        sys.exit(1)
    
    analyzer = DebugSessionAnalyzer(session_file)
    analysis = analyzer.analyze()
    
    # Print summary
    print(f"\n📊 Debug Session Analysis")
    print(f"=" * 60)
    print(f"Session ID: {analysis['session_id']}")
    print(f"Duration: {analysis['duration']} minutes")
    print(f"Confidence: {analysis['confidence']}")
    print(f"\n🔍 Error Pattern:")
    print(f"  Type: {analysis['error_pattern']['error_type']}")
    print(f"  Message: {analysis['error_pattern']['error_message'][:100]}")
    print(f"\n💡 Root Cause:")
    print(f"  {analysis['root_cause']['cause']}")
    print(f"\n✅ Solution:")
    print(f"  Type: {analysis['solution_pattern']['solution_type']}")
    print(f"  Command: {analysis['solution_pattern']['final_command']}")
    print(f"\n🛡️ Prevention:")
    print(f"  {analysis['prevention_strategy']['strategy']}")
    print(f"\n🎯 Recommended Skill Type: {analysis['skill_type']}")
    print(f"📎 Tags: {', '.join(analysis['tags'])}")
    
    # Save analysis
    output_file = analyzer.save_analysis()
    print(f"\n💾 Analysis saved to: {output_file}")
    print()


if __name__ == "__main__":
    main()
