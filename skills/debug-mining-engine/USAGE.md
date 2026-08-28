# Debug Mining Engine - Usage Guide

## Quick Start

### 1. Setup (One Time)

```bash
# Setup the debug monitor
bash /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/setup_monitor.sh

# Reload shell
source ~/.bashrc
```

### 2. Capture Debugging Sessions

**Option A: Manual Capture**

```bash
# Start capturing
/debug-start "Fixing database connection error"

# Debug your issue
python3 my_script.py  # Error
python3 my_script.py --fix  # Success

# End capture
/debug-end
```

**Option B: Automatic Detection**

The monitor automatically detects errors and starts capturing. When you fix the issue, it will prompt:

```
🤔 I noticed you just fixed an error. Should I save this debugging session?
   [Yes, save it] [No, discard] [Let me review first]
```

### 3. Analyze Captured Sessions

```bash
# Analyze a debugging session
python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/analyzer.py \
  /home/ubuntu/debug-sessions/SESSION_ID.json
```

**Output:**
- Error pattern analysis
- Root cause identification
- Solution pattern extraction
- Prevention strategy
- Confidence score
- Recommended skill type

### 4. Generate Reusable Assets

```bash
# Generate skills/snippets/patterns from analysis
python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/generator.py \
  /home/ubuntu/debug-sessions/analyses/SESSION_ID_analysis.json
```

**Output formats (based on complexity):**

1. **Full Skill** (complex issues, 10+ minutes)
   - Complete SKILL.md documentation
   - validate.sh, prevent.sh, fix.sh scripts
   - README.md
   - Ready to add to skill arsenal

2. **Code Snippet** (quick fixes, <2 minutes)
   - Standalone executable script
   - Copy/paste ready
   - Includes context and metadata

3. **Pattern Guide** (medium complexity, 2-10 minutes)
   - Conceptual documentation
   - When/why/how to fix
   - Prevention strategies
   - Best practices

## Complete Workflow

### End-to-End Example

```bash
# 1. Start debugging session
/debug-start "API authentication failing"

# 2. Debug (errors captured automatically)
curl https://api.example.com/auth
# Error: 401 Unauthorized

curl https://api.example.com/auth -H "Authorization: Bearer $TOKEN"
# Error: 403 Forbidden

curl https://api.example.com/auth/activate -H "Authorization: Bearer $TOKEN"
# Success!

curl https://api.example.com/auth -H "Authorization: Bearer $TOKEN"
# Success!

# 3. End session
/debug-end

# 4. Analyze
python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/analyzer.py \
  /home/ubuntu/debug-sessions/LATEST_SESSION.json

# 5. Generate assets
python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/generator.py \
  /home/ubuntu/debug-sessions/analyses/LATEST_SESSION_analysis.json

# 6. Review generated assets
cat /home/ubuntu/debug-sessions/generated/generation_summary.md

# 7. Add to skill arsenal (if full skill)
cp -r /home/ubuntu/debug-sessions/generated/skills/NEW_SKILL \
  /home/ubuntu/skills/skills/utility-skills/

# 8. Commit to GitHub
cd /home/ubuntu/skills
git add .
git commit -m "Add auto-generated skill from debugging session"
git push
```

## Output Locations

All generated assets are saved to `/home/ubuntu/debug-sessions/generated/`:

```
/home/ubuntu/debug-sessions/
├── SESSION_ID.json                    # Raw captured session
├── analyses/
│   └── SESSION_ID_analysis.json       # Analysis results
└── generated/
    ├── skills/                        # Full skills
    │   └── SKILL_NAME/
    │       ├── SKILL.md
    │       ├── README.md
    │       └── scripts/
    │           ├── validate.sh
    │           ├── prevent.sh
    │           └── fix.sh
    ├── snippets/                      # Code snippets
    │   └── SNIPPET_NAME.sh
    ├── patterns/                      # Pattern guides
    │   └── PATTERN_NAME.md
    └── generation_summary.md          # Summary report
```

## Advanced Usage

### Batch Processing

Process multiple sessions:

```bash
# Analyze all sessions
for session in /home/ubuntu/debug-sessions/*.json; do
  python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/analyzer.py "$session"
done

# Generate all assets
for analysis in /home/ubuntu/debug-sessions/analyses/*.json; do
  python3 /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/generator.py "$analysis"
done
```

### Custom Analysis

```python
from scripts.analyzer import DebugSessionAnalyzer

# Load and analyze
analyzer = DebugSessionAnalyzer("session.json")
analysis = analyzer.analyze()

# Access specific data
print(f"Error type: {analysis['error_pattern']['error_type']}")
print(f"Root cause: {analysis['root_cause']['cause']}")
print(f"Solution: {analysis['solution_pattern']['final_command']}")
print(f"Confidence: {analysis['confidence']}")
```

### Custom Generation

```python
from scripts.generator import SkillGenerator

# Load and generate
generator = SkillGenerator("analysis.json")

# Generate specific format
skill_path = generator.generate_full_skill()
snippet_path = generator.generate_code_snippet()
pattern_path = generator.generate_pattern_guide()

# Or generate all
outputs = generator.generate_all()
```

## Integration with Skill Arsenal

### Adding Generated Skills

```bash
# 1. Review generated skill
cat /home/ubuntu/debug-sessions/generated/skills/NEW_SKILL/SKILL.md

# 2. Move to appropriate category
mv /home/ubuntu/debug-sessions/generated/skills/NEW_SKILL \
   /home/ubuntu/skills/skills/utility-skills/

# 3. Update skill registry
cd /home/ubuntu/skills
python3 lib/skill_registry.py update

# 4. Commit to GitHub
git add .
git commit -m "Add NEW_SKILL from debugging session"
git push

# 5. Deploy across terminals
skill-sync
```

### Using Generated Snippets

```bash
# 1. Find relevant snippet
ls /home/ubuntu/debug-sessions/generated/snippets/

# 2. Run directly
bash /home/ubuntu/debug-sessions/generated/snippets/database-fix.sh

# 3. Or copy to project
cp /home/ubuntu/debug-sessions/generated/snippets/database-fix.sh \
   /home/ubuntu/my-project/scripts/
```

## Tips & Best Practices

### Capture Quality

**Good captures include:**
- Clear description of the problem
- Multiple solution attempts (including failures)
- Final working solution
- Enough context to understand the issue

**Poor captures:**
- Single command with no context
- No clear error message
- No successful resolution
- Too short (<1 minute)

### When to Use Each Format

**Full Skill:**
- Complex multi-step debugging
- Reusable across projects
- Requires validation/prevention scripts
- Duration: 10+ minutes

**Code Snippet:**
- Quick one-line fixes
- Copy/paste solutions
- Simple error handling
- Duration: <2 minutes

**Pattern Guide:**
- Conceptual understanding needed
- Multiple approaches possible
- Educational value
- Duration: 2-10 minutes

### Improving Confidence Scores

High confidence (0.8-1.0) requires:
- ✅ Clear error message
- ✅ Clear solution
- ✅ Multiple attempts showing progression
- ✅ Descriptive session name

Low confidence (<0.5) indicates:
- ❌ Missing error messages
- ❌ No clear solution
- ❌ Too few commands
- ❌ No description

## Troubleshooting

### Monitor Not Working

```bash
# Check if monitor is running
ps aux | grep debug_monitor

# Restart monitor
bash /home/ubuntu/skills/skills/utility-skills/debug-mining-engine/scripts/setup_monitor.sh

# Check logs
tail -f /tmp/debug_monitor.log
```

### Commands Not Found

```bash
# Reload shell configuration
source ~/.bashrc

# Verify commands exist
type /debug-start
type /debug-end
```

### Analysis Fails

```bash
# Validate session file
cat /home/ubuntu/debug-sessions/SESSION_ID.json | jq .

# Check for required fields
jq '.commands | length' /home/ubuntu/debug-sessions/SESSION_ID.json
```

### Generation Fails

```bash
# Validate analysis file
cat /home/ubuntu/debug-sessions/analyses/SESSION_ID_analysis.json | jq .

# Check confidence score
jq '.confidence' /home/ubuntu/debug-sessions/analyses/SESSION_ID_analysis.json
```

## Examples

See the test sessions for examples:

```bash
# Simple database error
cat /home/ubuntu/debug-sessions/test_session.json

# Complex API authentication
cat /home/ubuntu/debug-sessions/test_session_complex.json

# View generated outputs
ls -R /home/ubuntu/debug-sessions/generated/
```

## Next Steps

1. **Capture your first debugging session**
2. **Review generated assets**
3. **Add best skills to arsenal**
4. **Share patterns with team**
5. **Build your debugging knowledge base**

---

**Remember: "The answer lies in the darkness"** - Every bug you fix becomes a permanent asset! 💡
