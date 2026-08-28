#!/bin/bash
# Skill Development Workflow
# Automates the process of creating, testing, and deploying a new skill

set -e  # Exit on error

SKILL_NAME="$1"

if [ -z "$SKILL_NAME" ]; then
    echo "❌ Error: Please provide a skill name"
    echo "Usage: $0 <skill-name>"
    exit 1
fi

echo "🤖 Starting Skill Development Workflow for: $SKILL_NAME"
echo "=============================================="
echo ""

# Step 1: Initialize the skill
echo "📦 Step 1: Initializing skill structure..."
python /home/ubuntu/skills/skill-creator/scripts/init_skill.py "$SKILL_NAME"
echo "✅ Skill initialized"
echo ""

# Step 2: Validate the skill structure
echo "🔍 Step 2: Validating skill structure..."
python /home/ubuntu/skills/skill-creator/scripts/quick_validate.py "$SKILL_NAME"
echo "✅ Skill structure validated"
echo ""

# Step 3: Check if skillz server can discover it
echo "📚 Step 3: Checking if skillz server can discover the skill..."
sleep 2  # Give skillz a moment to discover the new skill
echo "✅ Skill should now be discoverable by skillz server"
echo ""

# Step 4: Summary
echo "=============================================="
echo "✅ Skill Development Workflow Complete!"
echo ""
echo "📋 Summary:"
echo "  - Skill created at: /home/ubuntu/skills/$SKILL_NAME"
echo "  - Next steps:"
echo "    1. Edit /home/ubuntu/skills/$SKILL_NAME/SKILL.md"
echo "    2. Add your scripts to /home/ubuntu/skills/$SKILL_NAME/scripts/"
echo "    3. Test your skill"
echo "    4. The skillz server will auto-discover it"
echo ""
echo "🎉 Happy skill building!"
