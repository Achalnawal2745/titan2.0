#!/usr/bin/env python3
"""
Generate secure promotional codes.

Usage:
    python3 generate_codes.py [options]

Options:
    --count N          Number of codes to generate (default: 10)
    --prefix PREFIX    Code prefix (default: PROMO)
    --length N         Random part length (default: 8)
    --format FORMAT    Format: alphanumeric, alpha, numeric (default: alphanumeric)
    --separator SEP    Separator character (default: -)

Examples:
    python3 generate_codes.py --count 5
    python3 generate_codes.py --prefix SAVE --length 6
    python3 generate_codes.py --prefix FRIEND --format alpha --separator _
"""

import sys
import random
import string
import argparse

def generate_code(prefix, length, format_type, separator):
    """Generate a single promo code."""
    if format_type == 'alphanumeric':
        chars = string.ascii_uppercase + string.digits
    elif format_type == 'alpha':
        chars = string.ascii_uppercase
    elif format_type == 'numeric':
        chars = string.digits
    else:
        chars = string.ascii_uppercase + string.digits
    
    # Exclude confusing characters
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
    
    # Generate random part
    random_part = ''.join(random.choice(chars) for _ in range(length))
    
    # Format code
    if prefix:
        code = f"{prefix}{separator}{random_part}"
    else:
        code = random_part
    
    return code

def main():
    parser = argparse.ArgumentParser(description='Generate secure promotional codes')
    parser.add_argument('--count', type=int, default=10, help='Number of codes to generate')
    parser.add_argument('--prefix', type=str, default='PROMO', help='Code prefix')
    parser.add_argument('--length', type=int, default=8, help='Random part length')
    parser.add_argument('--format', type=str, default='alphanumeric', 
                       choices=['alphanumeric', 'alpha', 'numeric'],
                       help='Character format')
    parser.add_argument('--separator', type=str, default='-', help='Separator character')
    parser.add_argument('--no-prefix', action='store_true', help='Generate without prefix')
    
    args = parser.parse_args()
    
    prefix = None if args.no_prefix else args.prefix
    
    print(f"🎯 Generating {args.count} promo codes")
    print("=" * 80)
    
    codes = []
    for i in range(args.count):
        code = generate_code(prefix, args.length, args.format, args.separator)
        codes.append(code)
        print(f"{i+1:3d}. {code}")
    
    print("\n" + "=" * 80)
    print("📋 COPY-PASTE FORMATS")
    print("=" * 80)
    
    # JavaScript object format
    print("\n// JavaScript/TypeScript (hardcoded):")
    print("const DISCOUNT_CODES = {")
    for code in codes:
        print(f"  '{code}': {{ type: 'free', value: 0 }},")
    print("};")
    
    # SQL INSERT format
    print("\n-- SQL (database):")
    print("INSERT INTO promo_codes (code, discount_type, discount_value, description) VALUES")
    for i, code in enumerate(codes):
        comma = "," if i < len(codes) - 1 else ";"
        print(f"  ('{code}', 'free', 0, 'Auto-generated code'){comma}")
    
    # Markdown list format
    print("\n<!-- Markdown list:")
    for code in codes:
        print(f"- `{code}` - Free access")
    print("-->")
    
    # Plain text list
    print("\n# Plain text list:")
    for code in codes:
        print(code)

if __name__ == '__main__':
    main()
