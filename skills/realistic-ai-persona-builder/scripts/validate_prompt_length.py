#!/usr/bin/env python3
"""
Validate that AI persona prompts fit within API character limits.

Usage:
    python validate_prompt_length.py <prompt_text> [max_length]
    
Examples:
    python validate_prompt_length.py "Your prompt here" 4000
    python validate_prompt_length.py "$PROMPT_VARIABLE" 8000
"""

import sys


def validate_prompt_length(prompt: str, max_length: int = 4000) -> dict:
    """
    Validate prompt length and return detailed metrics.
    
    Args:
        prompt: The prompt text to validate
        max_length: Maximum allowed character count (default: 4000 for Hume AI)
        
    Returns:
        dict with keys:
            - length: Current prompt length in characters
            - max_length: Maximum allowed length
            - within_limit: Boolean indicating if prompt is within limit
            - remaining_space: Characters remaining (negative if over limit)
            - percentage_used: Percentage of limit used
    """
    length = len(prompt)
    within_limit = length <= max_length
    remaining_space = max_length - length
    percentage_used = (length / max_length) * 100
    
    return {
        "length": length,
        "max_length": max_length,
        "within_limit": within_limit,
        "remaining_space": remaining_space,
        "percentage_used": percentage_used,
    }


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Error: Missing required argument")
        print()
        print("Usage: python validate_prompt_length.py <prompt_text> [max_length]")
        print()
        print("Arguments:")
        print("  prompt_text   The prompt text to validate (required)")
        print("  max_length    Maximum character limit (optional, default: 4000)")
        print()
        print("Examples:")
        print('  python validate_prompt_length.py "Your prompt here" 4000')
        print('  python validate_prompt_length.py "$PROMPT_VARIABLE" 8000')
        sys.exit(1)
    
    prompt = sys.argv[1]
    max_length = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    
    result = validate_prompt_length(prompt, max_length)
    
    # Print results
    print("=" * 50)
    print("Prompt Length Validation")
    print("=" * 50)
    print(f"Prompt length:    {result['length']:,} characters")
    print(f"Max length:       {result['max_length']:,} characters")
    print(f"Percentage used:  {result['percentage_used']:.1f}%")
    print(f"Remaining space:  {result['remaining_space']:,} characters")
    print()
    
    if result['within_limit']:
        print("✅ PASS: Prompt is within character limit")
        
        # Warn if close to limit
        if result['remaining_space'] < 200:
            print("⚠️  WARNING: Less than 200 characters remaining")
            print("   Consider condensing further for safety margin")
    else:
        print("❌ FAIL: Prompt exceeds character limit")
        print(f"   Over limit by: {abs(result['remaining_space']):,} characters")
        print("   Must condense before use")
    
    print("=" * 50)
    
    # Exit with appropriate code
    sys.exit(0 if result['within_limit'] else 1)


if __name__ == "__main__":
    main()
