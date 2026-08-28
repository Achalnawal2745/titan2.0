# Autonomous Sync Script

**One command to sync from Manus to GitHub.** ✨

---

## What This Does

Automates the process of syncing files from Manus sandbox to your GitHub repository via Google Drive.

**Before**: Download files → Copy to repo → Git add → Git commit → Git push (6 steps)  
**After**: Run one command (1 step)

---

## Quick Start

### One-Time Setup (5 minutes)

**1. Install rclone**:
```bash
brew install rclone  # macOS
sudo apt install rclone  # Linux
```

**2. Configure Google Drive**:
```bash
rclone config
# Name it: manus_google_drive
# Type: Google Drive
# Follow OAuth flow
```

**3. Copy sync script**:
```bash
cp /path/to/this/skill/scripts/gdrive_to_repo_sync.py ~/
chmod +x ~/gdrive_to_repo_sync.py
```

**4. Test**:
```bash
rclone lsd manus_google_drive:
# Should list your Google Drive folders
```

---

## Usage

### In Manus

Tell Manus what to sync:

```
Sync /home/ubuntu/skills/my-new-skill to GitHub
```

Manus will:
1. Upload files to Google Drive
2. Give you a command to run

### On Your Local Machine

Run the command Manus provides:

```bash
python3 ~/gdrive_to_repo_sync.py github-sync-1770720864 ~/my-repo "feat: add new skill"
```

Done! ✅

---

## How It Works

```
Manus Sandbox
     ↓
Google Drive (temporary storage)
     ↓
Your Local Machine
     ↓
GitHub Repository
```

**Why Google Drive?**
- Bridges Manus sandbox and your local machine
- No direct GitHub API access needed from sandbox
- You control what gets committed

---

## Examples

### Example 1: Sync a Skill

**Manus**: "Sync /home/ubuntu/skills/organize-github-repos to GitHub"

**You run**:
```bash
python3 ~/gdrive_to_repo_sync.py github-sync-1770720864 ~/my-repo "feat: add organize-github-repos skill"
```

### Example 2: Sync Multiple Files

**Manus**: "Sync these to GitHub: skills/skill-a, skills/skill-b, docs/guide.md"

**You run**: (command provided by Manus)

### Example 3: Custom Commit Message

**Manus**: "Sync /home/ubuntu/project with message 'fix: resolve auth bug'"

**You run**: (command with your custom message)

---

## The Script

### Location
`~/gdrive_to_repo_sync.py`

### What It Does
1. Downloads from Google Drive
2. Copies to your repo
3. Git add
4. Git commit
5. Git push
6. Cleanup

### Arguments
```bash
python3 ~/gdrive_to_repo_sync.py <gdrive-folder> <repo-path> "<message>"
```

---

## Troubleshooting

### "rclone not found"
```bash
brew install rclone  # macOS
sudo apt install rclone  # Linux
```

### "Google Drive folder not found"
```bash
rclone lsd manus_google_drive: | grep github-sync
```

### "Git push failed"
```bash
gh auth login  # Set up GitHub auth
```

### "Permission denied"
```bash
chmod +x ~/gdrive_to_repo_sync.py
```

---

## Advanced

### Sync to Specific Branch
```bash
cd ~/my-repo
git checkout feature-branch
python3 ~/gdrive_to_repo_sync.py <folder> . "message"
```

### Sync to Subdirectory
Directory structure is preserved from Google Drive.

---

## Best Practices

1. ✅ Use descriptive commit messages
2. ✅ Review files before syncing
3. ✅ Clean up old Google Drive folders
4. ✅ Test with small changes first

---

## Files

```
autonomous-sync-script/
├── SKILL.md                        # Full documentation
├── README.md                       # This file
└── scripts/
    └── gdrive_to_repo_sync.py      # The sync script
```

---

## Support

**Check setup**:
```bash
rclone about manus_google_drive:
```

**List sync folders**:
```bash
rclone lsd manus_google_drive: | grep github-sync
```

**Verify repo**:
```bash
cd ~/my-repo && git status
```

---

## Version

**v1.0.0** (2026-02-10)
- ✅ Initial release
- ✅ Google Drive automation
- ✅ One-command sync
- ✅ Full documentation
