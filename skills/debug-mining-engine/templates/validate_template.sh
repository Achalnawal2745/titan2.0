#!/bin/bash
# Validation script for {{SKILL_NAME}}
# Auto-generated from debugging session

set -e

echo "🔍 Validating environment for {{ERROR_TYPE}} errors..."

# Validation logic based on error type
{{VALIDATION_LOGIC}}

# Test the fix command (dry run if possible)
echo "Testing fix command..."
{{FINAL_COMMAND}} --dry-run 2>/dev/null || echo "⚠️  Manual validation required"

echo "✅ Validation complete"
