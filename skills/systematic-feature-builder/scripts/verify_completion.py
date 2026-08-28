#!/usr/bin/env python3
"""
Verify all checklist items are complete before creating checkpoint.

Usage:
    python verify_completion.py <path/to/todo.md>

Returns:
    Exit code 0 if all items complete, 1 if incomplete items found
"""

import sys
import re
from pathlib import Path


def parse_todo(file_path):
    """Parse todo.md and extract incomplete items."""
    try:
        content = Path(file_path).read_text()
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    incomplete_items = []
    current_section = None
    
    for line_num, line in enumerate(content.split('\n'), 1):
        # Track current section
        if line.startswith('##'):
            current_section = line.strip('# ').strip()
        
        # Find incomplete checklist items
        if re.match(r'^\s*-\s*\[\s*\]', line):
            item = line.strip()
            incomplete_items.append({
                'line': line_num,
                'section': current_section,
                'item': item
            })
    
    return incomplete_items


def main():
    if len(sys.argv) != 2:
        print("Usage: python verify_completion.py <path/to/todo.md>")
        sys.exit(1)
    
    todo_path = sys.argv[1]
    incomplete = parse_todo(todo_path)
    
    if not incomplete:
        print("✅ All checklist items complete!")
        print("Ready to create checkpoint.")
        sys.exit(0)
    
    print(f"⚠️  Found {len(incomplete)} incomplete items:\n")
    
    current_section = None
    for item in incomplete:
        if item['section'] != current_section:
            current_section = item['section']
            print(f"\n## {current_section}")
        
        print(f"  Line {item['line']}: {item['item']}")
    
    print(f"\n❌ Please complete all items before creating checkpoint.")
    sys.exit(1)


if __name__ == '__main__':
    main()
