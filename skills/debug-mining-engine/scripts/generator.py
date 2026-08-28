#!/usr/bin/env python3
"""
Debug Mining Engine - Generator
Generates skills, code snippets, and pattern guides from analyzed debugging sessions
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class SkillGenerator:
    """Generates reusable assets from debugging session analysis"""
    
    def __init__(self, analysis_file: str):
        self.analysis_file = analysis_file
        self.analysis = self._load_analysis()
        self.output_dir = "/home/ubuntu/debug-sessions/generated"
        
    def _load_analysis(self) -> Dict:
        """Load analysis data from file"""
        with open(self.analysis_file, 'r') as f:
            return json.load(f)
    
    def generate_all(self) -> Dict[str, str]:
        """
        Generate all appropriate formats based on skill_type
        
        Returns dict with paths to generated files
        """
        skill_type = self.analysis.get("skill_type", "code_snippet")
        
        outputs = {}
        
        if skill_type == "full_skill":
            outputs["skill"] = self.generate_full_skill()
            outputs["snippet"] = self.generate_code_snippet()
            outputs["pattern"] = self.generate_pattern_guide()
        elif skill_type == "code_snippet":
            outputs["snippet"] = self.generate_code_snippet()
        else:  # pattern_guide
            outputs["pattern"] = self.generate_pattern_guide()
            outputs["snippet"] = self.generate_code_snippet()
        
        return outputs
    
    def generate_full_skill(self) -> str:
        """Generate a complete SKILL.md file"""
        
        # Generate skill name
        skill_name = self._generate_skill_name()
        skill_dir = f"{self.output_dir}/skills/{skill_name}"
        os.makedirs(skill_dir, exist_ok=True)
        
        # Generate SKILL.md content
        content = self._generate_skill_content()
        
        skill_file = f"{skill_dir}/SKILL.md"
        with open(skill_file, 'w') as f:
            f.write(content)
        
        # Generate supporting scripts
        self._generate_skill_scripts(skill_dir)
        
        # Generate README
        self._generate_skill_readme(skill_dir)
        
        return skill_file
    
    def _generate_skill_name(self) -> str:
        """Generate skill name from error pattern"""
        error_pattern = self.analysis.get("error_pattern", {})
        error_type = error_pattern.get("error_type", "general")
        
        # Create descriptive name
        name = f"{error_type}-debugger"
        
        # Sanitize for directory name
        name = re.sub(r'[^a-z0-9-]', '', name.lower())
        
        return name
    
    def _generate_skill_content(self) -> str:
        """Generate SKILL.md content"""
        
        error_pattern = self.analysis.get("error_pattern", {})
        root_cause = self.analysis.get("root_cause", {})
        solution_pattern = self.analysis.get("solution_pattern", {})
        prevention = self.analysis.get("prevention_strategy", {})
        
        skill_name = self._generate_skill_name()
        
        content = f"""# {skill_name.replace('-', ' ').title()}

**Auto-generated from debugging session**

## Overview

This skill helps debug and fix {error_pattern.get('error_type', 'general')} errors.

**Generated from**: Debugging session on {self.analysis.get('timestamp', 'unknown')}  
**Session duration**: {self.analysis.get('duration', 0)} minutes  
**Confidence**: {self.analysis.get('confidence', 0)}

## The Problem

### Error Pattern

**Type**: {error_pattern.get('error_type', 'unknown')}  
**Message**: 
```
{error_pattern.get('error_message', 'No error message captured')}
```

**Context**: 
```bash
{error_pattern.get('error_context', 'No context available')}
```

**Frequency**: This error occurred {error_pattern.get('total_errors', 0)} times during debugging

### Root Cause

{root_cause.get('cause', 'Unknown root cause')}

**Evidence**: {root_cause.get('evidence', 'No evidence captured')}

**Category**: {root_cause.get('category', 'general')}

## The Solution

### Solution Pattern

**Type**: {solution_pattern.get('solution_type', 'unknown')}

**What worked**:
```bash
{solution_pattern.get('final_command', 'No command captured')}
```

### Key Changes

{self._format_key_changes(solution_pattern.get('key_changes', []))}

### Solution Steps

The debugging process followed these steps:

{self._format_solution_steps(solution_pattern.get('solution_steps', []))}

## Prevention Strategy

### How to Avoid This Error

{prevention.get('strategy', 'No prevention strategy available')}

### Implementation

{prevention.get('implementation', 'No implementation details available')}

### Automation

{prevention.get('automation', 'No automation recommendations available')}

## Usage

### Quick Fix

If you encounter this error, run:

```bash
{solution_pattern.get('final_command', 'No command available')}
```

### Validation Script

Use the generated validation script:

```bash
bash {skill_name}/scripts/validate.sh
```

### Prevention Script

Add to your workflow:

```bash
bash {skill_name}/scripts/prevent.sh
```

## Files

- `scripts/validate.sh` - Validation script to check for this error
- `scripts/prevent.sh` - Prevention script to avoid this error
- `scripts/fix.sh` - Automated fix script

## Tags

{', '.join(f'`{tag}`' for tag in self.analysis.get('tags', []))}

## Related Skills

{self._format_related_skills(self.analysis.get('related_skills', []))}

## Metadata

- **Session ID**: {self.analysis.get('session_id', 'unknown')}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Skill Type**: full_skill
- **Confidence**: {self.analysis.get('confidence', 0)}

---

*This skill was automatically generated by the Debug Mining Engine*
"""
        
        return content
    
    def _format_key_changes(self, changes: List[str]) -> str:
        """Format key changes as markdown list"""
        if not changes:
            return "No key changes identified"
        
        return "\n".join(f"- {change}" for change in changes)
    
    def _format_solution_steps(self, steps: List[str]) -> str:
        """Format solution steps as numbered list"""
        if not steps:
            return "No steps captured"
        
        formatted = []
        for i, step in enumerate(steps, 1):
            formatted.append(f"{i}. ```bash\n   {step}\n   ```")
        
        return "\n".join(formatted)
    
    def _format_related_skills(self, skills: List[str]) -> str:
        """Format related skills as list"""
        if not skills:
            return "No related skills found"
        
        return "\n".join(f"- {skill}" for skill in skills)
    
    def _generate_skill_scripts(self, skill_dir: str):
        """Generate supporting scripts for the skill"""
        scripts_dir = f"{skill_dir}/scripts"
        os.makedirs(scripts_dir, exist_ok=True)
        
        solution_pattern = self.analysis.get("solution_pattern", {})
        final_command = solution_pattern.get("final_command", "echo 'No command available'")
        
        # Generate validate.sh
        validate_script = f"""#!/bin/bash
# Validation script for {self._generate_skill_name()}
# Auto-generated from debugging session

set -e

echo "🔍 Validating environment..."

# Add validation logic here
{final_command} --dry-run 2>/dev/null || echo "⚠️  Validation check needed"

echo "✅ Validation complete"
"""
        
        with open(f"{scripts_dir}/validate.sh", 'w') as f:
            f.write(validate_script)
        os.chmod(f"{scripts_dir}/validate.sh", 0o755)
        
        # Generate prevent.sh
        prevent_script = f"""#!/bin/bash
# Prevention script for {self._generate_skill_name()}
# Auto-generated from debugging session

set -e

echo "🛡️  Setting up prevention measures..."

# Add prevention logic here
echo "✅ Prevention measures in place"
"""
        
        with open(f"{scripts_dir}/prevent.sh", 'w') as f:
            f.write(prevent_script)
        os.chmod(f"{scripts_dir}/prevent.sh", 0o755)
        
        # Generate fix.sh
        fix_script = f"""#!/bin/bash
# Automated fix script for {self._generate_skill_name()}
# Auto-generated from debugging session

set -e

echo "🔧 Applying fix..."

{final_command}

echo "✅ Fix applied successfully"
"""
        
        with open(f"{scripts_dir}/fix.sh", 'w') as f:
            f.write(fix_script)
        os.chmod(f"{scripts_dir}/fix.sh", 0o755)
    
    def _generate_skill_readme(self, skill_dir: str):
        """Generate README.md for the skill"""
        skill_name = self._generate_skill_name()
        
        readme = f"""# {skill_name.replace('-', ' ').title()}

Auto-generated debugging skill from Debug Mining Engine.

## Quick Start

```bash
# Validate environment
bash scripts/validate.sh

# Apply fix
bash scripts/fix.sh

# Set up prevention
bash scripts/prevent.sh
```

## Documentation

See [SKILL.md](SKILL.md) for complete documentation.

## Generated

- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Session ID**: {self.analysis.get('session_id', 'unknown')}
- **Confidence**: {self.analysis.get('confidence', 0)}
"""
        
        with open(f"{skill_dir}/README.md", 'w') as f:
            f.write(readme)
    
    def generate_code_snippet(self) -> str:
        """Generate a standalone code snippet"""
        
        snippets_dir = f"{self.output_dir}/snippets"
        os.makedirs(snippets_dir, exist_ok=True)
        
        solution_pattern = self.analysis.get("solution_pattern", {})
        error_pattern = self.analysis.get("error_pattern", {})
        
        snippet_name = f"{error_pattern.get('error_type', 'general')}-fix"
        snippet_file = f"{snippets_dir}/{snippet_name}.sh"
        
        snippet = f"""#!/bin/bash
# Code Snippet: {snippet_name}
# Auto-generated from debugging session
# 
# Problem: {error_pattern.get('error_message', 'No description')[:100]}
# Solution: {solution_pattern.get('solution_type', 'unknown')}
# 
# Usage: bash {snippet_name}.sh

set -e

# The fix that worked
{solution_pattern.get('final_command', 'echo "No command available"')}

# Additional context
# Session ID: {self.analysis.get('session_id', 'unknown')}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Confidence: {self.analysis.get('confidence', 0)}
"""
        
        with open(snippet_file, 'w') as f:
            f.write(snippet)
        os.chmod(snippet_file, 0o755)
        
        return snippet_file
    
    def generate_pattern_guide(self) -> str:
        """Generate a pattern guide document"""
        
        patterns_dir = f"{self.output_dir}/patterns"
        os.makedirs(patterns_dir, exist_ok=True)
        
        error_pattern = self.analysis.get("error_pattern", {})
        pattern_name = f"{error_pattern.get('error_type', 'general')}-pattern"
        pattern_file = f"{patterns_dir}/{pattern_name}.md"
        
        root_cause = self.analysis.get("root_cause", {})
        solution_pattern = self.analysis.get("solution_pattern", {})
        prevention = self.analysis.get("prevention_strategy", {})
        
        guide = f"""# {error_pattern.get('error_type', 'General').title()} Error Pattern

**Auto-generated pattern guide from debugging session**

## Pattern Overview

This guide documents a common {error_pattern.get('error_type', 'general')} error pattern and how to handle it.

**Generated from**: Debugging session on {self.analysis.get('timestamp', 'unknown')}  
**Confidence**: {self.analysis.get('confidence', 0)}

## The Pattern

### When This Happens

You'll see this error pattern when:

```
{error_pattern.get('error_message', 'No error message')}
```

**Context**: {error_pattern.get('error_context', 'No context available')}

**Frequency**: Occurred {error_pattern.get('total_errors', 0)} times in debugging session

### Why It Happens

**Root Cause**: {root_cause.get('cause', 'Unknown')}

**Category**: {root_cause.get('category', 'general')}

**Evidence**: {root_cause.get('evidence', 'No evidence')}

## How to Fix It

### Solution Pattern

**Type**: {solution_pattern.get('solution_type', 'unknown')}

**The Fix**:
```bash
{solution_pattern.get('final_command', 'No command available')}
```

### Why This Works

{self._explain_solution(solution_pattern)}

### Key Changes Required

{self._format_key_changes(solution_pattern.get('key_changes', []))}

## How to Prevent It

### Prevention Strategy

{prevention.get('strategy', 'No prevention strategy')}

### Implementation Steps

1. {prevention.get('implementation', 'No implementation details')}
2. {prevention.get('automation', 'No automation recommendations')}

### Best Practices

- Always validate before executing
- Add error handling for edge cases
- Document assumptions and requirements
- Test in staging environment first

## Related Patterns

{self._format_related_skills(self.analysis.get('related_skills', []))}

## Tags

{', '.join(f'`{tag}`' for tag in self.analysis.get('tags', []))}

## Metadata

- **Session ID**: {self.analysis.get('session_id', 'unknown')}
- **Duration**: {self.analysis.get('duration', 0)} minutes
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Confidence**: {self.analysis.get('confidence', 0)}

---

*This pattern guide was automatically generated by the Debug Mining Engine*
"""
        
        with open(pattern_file, 'w') as f:
            f.write(guide)
        
        return pattern_file
    
    def _explain_solution(self, solution_pattern: Dict) -> str:
        """Generate explanation of why the solution works"""
        solution_type = solution_pattern.get('solution_type', 'unknown')
        
        explanations = {
            "validation": "This solution adds validation checks before executing operations, catching errors early.",
            "retry_with_backoff": "This solution implements retry logic with exponential backoff to handle transient failures.",
            "dependency_installation": "This solution installs missing dependencies required for the operation.",
            "automatic_fix": "This solution automatically detects and repairs the issue.",
            "configuration_change": "This solution adjusts configuration to match requirements."
        }
        
        return explanations.get(solution_type, "This solution addresses the root cause of the error.")
    
    def generate_summary(self, outputs: Dict[str, str]) -> str:
        """Generate summary report of generated assets"""
        
        summary_file = f"{self.output_dir}/generation_summary.md"
        
        summary = f"""# Debug Mining Engine - Generation Summary

**Session ID**: {self.analysis.get('session_id', 'unknown')}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Analysis Summary

- **Error Type**: {self.analysis.get('error_pattern', {}).get('error_type', 'unknown')}
- **Duration**: {self.analysis.get('duration', 0)} minutes
- **Confidence**: {self.analysis.get('confidence', 0)}
- **Skill Type**: {self.analysis.get('skill_type', 'unknown')}

## Generated Assets

{self._format_outputs(outputs)}

## Quick Access

{self._format_quick_access(outputs)}

## Next Steps

1. Review generated assets
2. Test in your environment
3. Customize as needed
4. Add to skill arsenal
5. Share with team

## Tags

{', '.join(f'`{tag}`' for tag in self.analysis.get('tags', []))}

---

*Generated by Debug Mining Engine*
"""
        
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        return summary_file
    
    def _format_outputs(self, outputs: Dict[str, str]) -> str:
        """Format outputs as markdown list"""
        if not outputs:
            return "No assets generated"
        
        formatted = []
        for asset_type, path in outputs.items():
            formatted.append(f"- **{asset_type.title()}**: `{path}`")
        
        return "\n".join(formatted)
    
    def _format_quick_access(self, outputs: Dict[str, str]) -> str:
        """Format quick access commands"""
        if not outputs:
            return "No assets to access"
        
        formatted = []
        for asset_type, path in outputs.items():
            if path.endswith('.sh'):
                formatted.append(f"```bash\n# Run {asset_type}\nbash {path}\n```")
            else:
                formatted.append(f"```bash\n# View {asset_type}\ncat {path}\n```")
        
        return "\n\n".join(formatted)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: generator.py <analysis_file>")
        sys.exit(1)
    
    analysis_file = sys.argv[1]
    
    if not os.path.exists(analysis_file):
        print(f"Error: Analysis file not found: {analysis_file}")
        sys.exit(1)
    
    generator = SkillGenerator(analysis_file)
    
    print(f"\n🎯 Generating assets from analysis...")
    print(f"=" * 60)
    
    # Generate all appropriate formats
    outputs = generator.generate_all()
    
    print(f"\n✅ Generated {len(outputs)} asset(s):")
    for asset_type, path in outputs.items():
        print(f"  - {asset_type.title()}: {path}")
    
    # Generate summary
    summary_file = generator.generate_summary(outputs)
    print(f"\n📊 Summary: {summary_file}")
    
    print(f"\n🎉 Generation complete!")
    print()


if __name__ == "__main__":
    main()
