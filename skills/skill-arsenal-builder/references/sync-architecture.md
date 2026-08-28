# Skill Sync Architecture

**Purpose**: Enable all Manus terminals to access and sync the unified skill arsenal from a central GitHub repository

**Date**: February 11, 2026

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CENTRAL HUB (GitHub)                     │
│         https://github.com/abcnuts/manus-skills             │
│                                                             │
│  - 71 skills across 12 categories                          │
│  - skills.json registry                                    │
│  - Shared utilities (lib/)                                 │
│  - Meta-skills                                             │
│  - Complete documentation                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
                    (git pull / git push)
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                    SYNC LAYER (Scripts)                     │
│                                                             │
│  - skill-sync.sh: Pull latest skills from GitHub           │
│  - skill-check.sh: Check for updates                       │
│  - skill-install.sh: First-time setup                      │
│  - skill-status.sh: Show current version                   │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
                    (local file system)
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│              LOCAL CACHE (Each Manus Terminal)              │
│                  /home/ubuntu/skills/                       │
│                                                             │
│  Terminal 1        Terminal 2        Terminal 3            │
│  ├── skill-1       ├── skill-1       ├── skill-1           │
│  ├── skill-2       ├── skill-2       ├── skill-2           │
│  └── ...           └── ...           └── ...               │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. GitHub as Single Source of Truth

**Central Repository**: `https://github.com/abcnuts/manus-skills`

All skills are stored in GitHub, which serves as:
- **Version control** - Track changes over time
- **Backup** - Skills are never lost
- **Accessibility** - Available from any Manus terminal
- **Collaboration** - Can share with others

### 2. Local Caching for Performance

**Local Directory**: `/home/ubuntu/skills/`

Each Manus terminal maintains a local copy:
- **Fast access** - No network latency
- **Offline capability** - Works without internet
- **Sandbox persistence** - Survives hibernation

### 3. Simple Sync Commands

**One-command operations**:
```bash
skill-sync      # Pull latest skills
skill-check     # Check for updates
skill-install   # First-time setup
skill-status    # Show current version
```

### 4. Automatic Update Detection

**Version tracking**:
- Each sync records the Git commit hash
- Terminals can detect when new skills are available
- Optional auto-sync on terminal startup

---

## Sync Workflow

### First-Time Setup (New Terminal)

```bash
# Run once in a new Manus terminal
skill-install
```

**What it does**:
1. Clones `abcnuts/manus-skills` to `/home/ubuntu/skills/`
2. Sets up Python path for skill utilities
3. Creates sync scripts in `/usr/local/bin/`
4. Records initial version
5. Verifies installation

**Expected output**:
```
✅ Cloned manus-skills repository
✅ Installed 71 skills across 12 categories
✅ Set up sync scripts
✅ Current version: abc123def (2026-02-11)
🎯 Skills ready to use!
```

### Regular Sync (Existing Terminal)

```bash
# Run anytime to get latest skills
skill-sync
```

**What it does**:
1. Checks GitHub for updates
2. Pulls latest changes
3. Updates local cache
4. Shows what changed
5. Records new version

**Expected output**:
```
Checking for updates...
✅ Found 3 new skills:
   - cross-platform-sync
   - mcp-converter
   - skill-marketplace

Syncing...
✅ Downloaded 3 new skills
✅ Updated 2 existing skills
✅ Current version: def456ghi (2026-02-11)

New skills available in:
- /home/ubuntu/skills/integration-skills/cross-platform-sync
- /home/ubuntu/skills/utility-skills/mcp-converter
- /home/ubuntu/skills/specialized/skill-marketplace
```

### Check for Updates (No Download)

```bash
# Check if updates are available
skill-check
```

**What it does**:
1. Compares local version with GitHub
2. Lists available updates
3. Does NOT download anything

**Expected output**:
```
Current version: abc123def (2026-02-11)
Latest version: def456ghi (2026-02-11)

✅ 3 new skills available:
   - cross-platform-sync
   - mcp-converter
   - skill-marketplace

Run 'skill-sync' to update
```

### Show Status

```bash
# Show current installation status
skill-status
```

**What it does**:
1. Shows local version
2. Shows skill count
3. Shows last sync time
4. Shows repository status

**Expected output**:
```
Skill Arsenal Status
--------------------
Repository: https://github.com/abcnuts/manus-skills
Local Path: /home/ubuntu/skills/
Version: abc123def (2026-02-11)
Last Sync: 2 hours ago

Skills Installed: 71
Categories: 12
Meta-Skills: 1

Status: ✅ Up to date
```

---

## Technical Implementation

### Directory Structure

```
/home/ubuntu/skills/           # Local skill cache (Git repo)
├── .git/                      # Git metadata
├── skills/                    # All skills
├── lib/                       # Shared utilities
├── meta-skills/               # Meta-skills
├── skills.json                # Registry
├── README.md                  # Documentation
└── .skill-sync-version        # Sync metadata

/usr/local/bin/                # Sync scripts (in PATH)
├── skill-sync                 # Sync command
├── skill-check                # Check command
├── skill-install              # Install command
└── skill-status               # Status command
```

### Version Tracking

**File**: `/home/ubuntu/skills/.skill-sync-version`

```json
{
  "version": "abc123def456",
  "commit_hash": "abc123def456",
  "last_sync": "2026-02-11T23:49:00Z",
  "skills_count": 71,
  "categories_count": 12,
  "remote_url": "https://github.com/abcnuts/manus-skills"
}
```

### Sync Script Logic

**skill-sync.sh**:
```bash
#!/bin/bash
# Sync skills from GitHub

SKILLS_DIR="/home/ubuntu/skills"

cd "$SKILLS_DIR" || exit 1

# Fetch latest
git fetch origin main

# Check for updates
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ Already up to date"
    exit 0
fi

# Show what's new
echo "Updates available:"
git log --oneline HEAD..origin/main

# Pull changes
git pull origin main

# Update version file
echo "✅ Synced successfully"
skill-status
```

---

## Integration with Manus

### Python Path Setup

**Automatic in each terminal**:
```python
import sys
sys.path.insert(0, '/home/ubuntu/skills')

from lib.skill_registry import SkillRegistry
from lib.skill_composer import SkillComposer

# Now skills are available
registry = SkillRegistry('/home/ubuntu/skills/skills.json')
```

### Skill Discovery

**In any terminal**:
```python
# Find skills
database_skills = registry.find_by_tag("database")

# Get workflow
workflow = registry.suggest_workflow("build a SaaS app")

# Compose skills
composer = SkillComposer(registry)
result = composer.execute_workflow(workflow, context)
```

---

## Cross-Terminal Scenarios

### Scenario 1: Learn New Skill in Terminal 1

**Terminal 1** (learning terminal):
```bash
# Create new skill
cd /home/ubuntu/skills
# ... build new skill ...

# Commit and push
git add skills/new-skill/
git commit -m "feat: add new-skill"
git push origin main
```

**Terminal 2** (other terminal):
```bash
# Sync to get new skill
skill-sync

# New skill is now available
cd /home/ubuntu/skills/skills/new-skill/
cat SKILL.md
```

### Scenario 2: Update Existing Skill

**Terminal 1**:
```bash
# Enhance existing skill
cd /home/ubuntu/skills/skills/database-schema-generator/
# ... make improvements ...

# Push changes
git add .
git commit -m "enhance: improve database-schema-generator"
git push origin main
```

**Terminal 2**:
```bash
# Get updates
skill-sync

# Updated skill is now available
# No manual intervention needed
```

### Scenario 3: Fresh Terminal Setup

**New Terminal**:
```bash
# One command to get everything
skill-install

# All 71 skills are now available
# Can start using immediately
```

---

## Advantages

### For the User

1. **One Command**: `skill-sync` to get latest skills
2. **No Manual Work**: Automatic Git operations
3. **Always Current**: Easy to stay up-to-date
4. **No Data Loss**: GitHub backup
5. **Cross-Terminal**: Skills work everywhere

### For the System

1. **Version Control**: Full Git history
2. **Rollback Capability**: Can revert changes
3. **Conflict Resolution**: Git handles merges
4. **Scalability**: Works with 100+ skills
5. **Reliability**: GitHub uptime guarantee

---

## Security Considerations

### GitHub Authentication

**Already configured**: GitHub CLI (`gh`) is authenticated

**No additional setup needed**: Sync scripts use existing credentials

### Access Control

**Private repository**: Only you can access

**SSH keys**: Secure authentication

**Token management**: Handled by GitHub CLI

---

## Maintenance

### Regular Operations

**Daily**: Terminals auto-check for updates (optional)

**Weekly**: Manual sync to get latest skills

**Monthly**: Review and clean up unused skills

### Troubleshooting

**Sync fails**:
```bash
cd /home/ubuntu/skills
git status
git pull origin main --rebase
```

**Conflicts**:
```bash
cd /home/ubuntu/skills
git stash
git pull origin main
git stash pop
```

**Corrupted local cache**:
```bash
rm -rf /home/ubuntu/skills
skill-install
```

---

## Future Enhancements

### Phase 2 Features

1. **Auto-sync on startup**: Automatically check for updates when terminal starts
2. **Selective sync**: Only sync specific categories
3. **Conflict detection**: Warn if local changes would be overwritten
4. **Update notifications**: Alert when new skills are available

### Phase 3 Features

1. **Skill marketplace**: Share skills with community
2. **Version pinning**: Lock to specific skill versions
3. **Dependency management**: Auto-install required skills
4. **Performance metrics**: Track skill usage and effectiveness

---

## Summary

**Central Hub**: GitHub (`abcnuts/manus-skills`)  
**Local Cache**: `/home/ubuntu/skills/` in each terminal  
**Sync Method**: Git pull/push via simple commands  
**Update Detection**: Version tracking with commit hashes  

**Result**: All Manus terminals can access the same 71-skill arsenal with one command!

---

**Next Steps**: Build the sync scripts and test across terminals
