#!/usr/bin/env python3
"""
Discover existing promo code systems in a codebase.

Usage:
    python3 discover_promo_system.py <project_directory>

Example:
    python3 discover_promo_system.py /Users/brandon/my-app/
"""

import os
import sys
import re
import json
from pathlib import Path

# Search patterns for promo code implementations
PATTERNS = {
    'discount_keywords': [
        r'\bdiscount[_-]?code\b',
        r'\bpromo[_-]?code\b',
        r'\bcoupon\b',
        r'\bvoucher\b',
        r'DISCOUNT_CODES',
        r'PROMO_CODES',
    ],
    'stripe_patterns': [
        r'stripe\.checkout\.sessions\.create',
        r'stripe\.coupons',
        r'stripe\.promotionCodes',
    ],
    'api_endpoints': [
        r'/api/.*discount',
        r'/api/.*promo',
        r'/api/.*coupon',
        r'/api/validate.*code',
    ],
    'database_tables': [
        r'CREATE TABLE.*promo',
        r'CREATE TABLE.*discount',
        r'CREATE TABLE.*coupon',
    ],
}

# File extensions to search
EXTENSIONS = ['.js', '.ts', '.jsx', '.tsx', '.py', '.sql', '.env', '.json']

def search_file(filepath, patterns):
    """Search a file for patterns."""
    matches = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for category, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, content, re.IGNORECASE):
                        # Get context (line with match)
                        for i, line in enumerate(content.split('\n'), 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                matches.append({
                                    'category': category,
                                    'pattern': pattern,
                                    'line': i,
                                    'content': line.strip()[:100]
                                })
    except Exception as e:
        pass
    return matches

def discover_promo_system(project_dir):
    """Discover promo code system in project directory."""
    project_path = Path(project_dir)
    
    if not project_path.exists():
        print(f"❌ Error: Directory not found: {project_dir}")
        return
    
    print(f"🔍 Scanning: {project_dir}")
    print("=" * 80)
    
    results = {}
    file_count = 0
    
    # Search all files
    for root, dirs, files in os.walk(project_path):
        # Skip common directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'dist', 'build', '__pycache__', 'venv']]
        
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONS):
                filepath = Path(root) / file
                matches = search_file(filepath, PATTERNS)
                if matches:
                    relative_path = filepath.relative_to(project_path)
                    results[str(relative_path)] = matches
                    file_count += 1
    
    # Display results
    if not results:
        print("❌ No promo code system found")
        print("\nSearched for:")
        for category, patterns in PATTERNS.items():
            print(f"  • {category}: {', '.join(patterns[:2])}...")
        return
    
    print(f"✅ Found promo code patterns in {file_count} files\n")
    
    # Group by category
    by_category = {}
    for filepath, matches in results.items():
        for match in matches:
            category = match['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append({
                'file': filepath,
                'line': match['line'],
                'content': match['content']
            })
    
    # Display by category
    for category, items in by_category.items():
        print(f"\n📁 {category.upper().replace('_', ' ')}")
        print("-" * 80)
        for item in items[:5]:  # Show first 5 matches per category
            print(f"  {item['file']}:{item['line']}")
            print(f"    {item['content']}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more matches")
    
    # Analysis
    print("\n" + "=" * 80)
    print("📊 ANALYSIS")
    print("=" * 80)
    
    has_hardcoded = any('DISCOUNT_CODES' in str(m) or 'PROMO_CODES' in str(m) for matches in results.values() for m in matches)
    has_database = 'database_tables' in by_category
    has_api = 'api_endpoints' in by_category
    has_stripe = 'stripe_patterns' in by_category
    
    print(f"\n✓ Hardcoded codes: {'Yes' if has_hardcoded else 'No'}")
    print(f"✓ Database tables: {'Yes' if has_database else 'No'}")
    print(f"✓ API endpoints: {'Yes' if has_api else 'No'}")
    print(f"✓ Stripe integration: {'Yes' if has_stripe else 'No'}")
    
    # Recommendation
    print("\n💡 RECOMMENDATION")
    print("-" * 80)
    if has_hardcoded and not has_database:
        print("Current system: Hardcoded discount codes")
        print("Upgrade path: Implement database-driven system for better management")
    elif has_database:
        print("Current system: Database-driven promo code system")
        print("Status: Proper implementation detected ✅")
    else:
        print("Current system: Basic or partial implementation")
        print("Next steps: Review files above to understand current setup")
    
    # Key files
    print("\n📝 KEY FILES TO REVIEW")
    print("-" * 80)
    for filepath in list(results.keys())[:10]:
        print(f"  • {filepath}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 discover_promo_system.py <project_directory>")
        print("Example: python3 discover_promo_system.py /Users/brandon/my-app/")
        sys.exit(1)
    
    discover_promo_system(sys.argv[1])
