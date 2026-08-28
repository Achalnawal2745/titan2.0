#!/bin/bash
#
# Debug Mining Engine - Setup Monitor
# Installs shell monitoring system for automatic error detection
#

set -e

echo "🔧 Setting up Debug Mining Engine..."
echo

# Create required directories
echo "📁 Creating directories..."
mkdir -p /home/ubuntu/debug-sessions
mkdir -p /home/ubuntu/debug-snippets/{database,api,filesystem,network,auth}
mkdir -p /home/ubuntu/debug-patterns
mkdir -p /home/ubuntu/debug-mining

echo "✅ Directories created"
echo

# Create debug commands
echo "📝 Creating debug commands..."

# /debug-start command
cat > /home/ubuntu/debug-mining/debug-start << 'EOF'
#!/bin/bash
# Start manual debugging session

DESCRIPTION="${1:-Manual debugging session}"

python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/debug_commands.py start "$DESCRIPTION"
EOF

chmod +x /home/ubuntu/debug-mining/debug-start

# /debug-end command
cat > /home/ubuntu/debug-mining/debug-end << 'EOF'
#!/bin/bash
# End manual debugging session

python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/debug_commands.py end
EOF

chmod +x /home/ubuntu/debug-mining/debug-end

# /debug-save command
cat > /home/ubuntu/debug-mining/debug-save << 'EOF'
#!/bin/bash
# Save current debugging session

python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/debug_commands.py save
EOF

chmod +x /home/ubuntu/debug-mining/debug-save

# /debug-discard command
cat > /home/ubuntu/debug-mining/debug-discard << 'EOF'
#!/bin/bash
# Discard current debugging session

python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/debug_commands.py discard
EOF

chmod +x /home/ubuntu/debug-mining/debug-discard

echo "✅ Debug commands created"
echo

# Add to PATH
echo "🔗 Adding debug commands to PATH..."

if ! grep -q "/home/ubuntu/debug-mining" ~/.bashrc; then
    echo '' >> ~/.bashrc
    echo '# Debug Mining Engine' >> ~/.bashrc
    echo 'export PATH="$PATH:/home/ubuntu/debug-mining"' >> ~/.bashrc
    echo "✅ Added to ~/.bashrc"
else
    echo "✅ Already in PATH"
fi

echo

# Create aliases for convenience
echo "📌 Creating command aliases..."

if ! grep -q "alias /debug-start" ~/.bashrc; then
    echo '' >> ~/.bashrc
    echo '# Debug Mining Aliases' >> ~/.bashrc
    echo 'alias /debug-start="/home/ubuntu/debug-mining/debug-start"' >> ~/.bashrc
    echo 'alias /debug-end="/home/ubuntu/debug-mining/debug-end"' >> ~/.bashrc
    echo 'alias /debug-save="/home/ubuntu/debug-mining/debug-save"' >> ~/.bashrc
    echo 'alias /debug-discard="/home/ubuntu/debug-mining/debug-discard"' >> ~/.bashrc
    echo "✅ Aliases created"
else
    echo "✅ Aliases already exist"
fi

echo

# Test the setup
echo "🧪 Testing setup..."
python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/monitor.py --test

echo
echo "="*80
echo "✅ Debug Mining Engine setup complete!"
echo "="*80
echo
echo "📋 Available Commands:"
echo "   /debug-start [description]  - Start manual debugging session"
echo "   /debug-end                  - End debugging session"
echo "   /debug-save                 - Save current session"
echo "   /debug-discard              - Discard current session"
echo
echo "🔄 To activate commands in current shell:"
echo "   source ~/.bashrc"
echo
echo "📖 Read the skill for full usage:"
echo "   cat /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/SKILL.md"
echo
