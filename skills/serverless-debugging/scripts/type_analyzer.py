#!/usr/bin/env python3
"""
Type Coercion Analyzer for JavaScript/TypeScript

Analyzes conditional statements to identify potential type coercion bugs.

Usage:
    python type_analyzer.py <file_path> [function_name]
    
Example:
    python type_analyzer.py memory-extractor.ts shouldExtractMemories
"""

import sys
import re
from pathlib import Path

def analyze_conditions(content: str, function_name: str = None):
    """Analyze conditional statements for type coercion issues"""
    
    issues = []
    
    # Extract function if specified
    if function_name:
        func_pattern = rf'function\s+{function_name}\s*\([^)]*\)\s*{{([^}}]*)}}'
        match = re.search(func_pattern, content, re.DOTALL)
        if match:
            content = match.group(1)
            print(f"Analyzing function: {function_name}\n")
        else:
            print(f"Warning: Function '{function_name}' not found\n")
    
    # Check for null comparisons
    null_checks = re.findall(r'(\w+)\s*===\s*null', content)
    for var in null_checks:
        issues.append({
            'type': 'NULL_CHECK',
            'variable': var,
            'message': f"Variable '{var}' checked for null - verify it can't be 0, undefined, or empty string",
            'suggestion': f"Consider: if ({var} === null || {var} === 0)"
        })
    
    # Check for equality without type check
    loose_equality = re.findall(r'(\w+)\s*==\s*(\w+|null|undefined|\d+)', content)
    for var, value in loose_equality:
        issues.append({
            'type': 'LOOSE_EQUALITY',
            'variable': var,
            'message': f"Loose equality (==) used for '{var}' - may cause type coercion",
            'suggestion': f"Use strict equality (===) instead"
        })
    
    # Check for number comparisons on potentially string values
    number_comparisons = re.findall(r'(\w+)\s*([><]=?)\s*(\d+)', content)
    for var, op, num in number_comparisons:
        issues.append({
            'type': 'NUMBER_COMPARISON',
            'variable': var,
            'message': f"Numeric comparison '{var} {op} {num}' - verify '{var}' is actually a number",
            'suggestion': f"Consider: parseInt({var}) {op} {num} or typeof {var} === 'number'"
        })
    
    # Check for undefined checks
    undefined_checks = re.findall(r'(\w+)\s*===\s*undefined', content)
    for var in undefined_checks:
        issues.append({
            'type': 'UNDEFINED_CHECK',
            'variable': var,
            'message': f"Variable '{var}' checked for undefined - verify it can't be null or 0",
            'suggestion': f"Consider: if (!{var})"
        })
    
    # Check for truthiness checks that might miss 0
    truthiness = re.findall(r'if\s*\(\s*(\w+)\s*\)', content)
    for var in truthiness:
        if var not in ['true', 'false']:
            issues.append({
                'type': 'TRUTHINESS',
                'variable': var,
                'message': f"Truthiness check on '{var}' - will be false for 0, '', null, undefined",
                'suggestion': f"Be explicit: if ({var} !== null && {var} !== undefined)"
            })
    
    return issues

def print_issues(issues: list):
    """Print analysis results"""
    if not issues:
        print("✅ No obvious type coercion issues found")
        return
    
    print(f"⚠️  Found {len(issues)} potential type coercion issues:\n")
    
    # Group by type
    by_type = {}
    for issue in issues:
        issue_type = issue['type']
        if issue_type not in by_type:
            by_type[issue_type] = []
        by_type[issue_type].append(issue)
    
    for issue_type, type_issues in by_type.items():
        print(f"=== {issue_type} ===")
        for issue in type_issues:
            print(f"Variable: {issue['variable']}")
            print(f"Issue: {issue['message']}")
            print(f"Suggestion: {issue['suggestion']}")
            print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    function_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    content = file_path.read_text()
    
    print(f"Analyzing: {file_path}")
    if function_name:
        print(f"Function: {function_name}")
    print()
    
    issues = analyze_conditions(content, function_name)
    print_issues(issues)
    
    # Return exit code based on issues found
    sys.exit(1 if issues else 0)

if __name__ == "__main__":
    main()
