---
name: "autonomous-sync-script"
description: "Specialized skill for autonomous sync script workflows and automation."
---

# Autonomous Sync Script

## Overview

This skill automates the process of syncing files from Manus to your GitHub repository via Google Drive. Instead of manually downloading files and committing them, this skill uploads everything to Google Drive and provides a single command to run on your local machine that automatically downloads, commits, and pushes to GitHub.

**Key Benefit**: Turn a 6-step manual process into a single command.

## When to Use This Skill

Use this skill when:
- **Syncing new skills** - Push newly created skills to your GitHub repo
- **Updating existing code** - Sync modified files to GitHub
- **Batch operations** - Sync multiple files/directories at once
- **Automating workflow** - Reduce manual steps in your development process

## Quick Start

### Step 1: Specify What to Sync (In Manus)

Tell Manus what files/directories to sync:

```
Sync /home/ubuntu/skills/my-new-skill to GitHub
```

### Step 2: Run the Command (On Your Local Machine)

Manus will provide a command like:

```bash
python3 ~/gdrive_to_repo_sync.py github-sync-1770720864 ~/my-repo "feat: add my-new-skill"
```

Copy and run it. Done! ✅

---

## How It Works

**The Process**:

1. **Manus** uploads your files to Google Drive (timestamped folder)
2. **Manus** gives you a one-line command with the folder name
3. **You** run the command on your local machine
4. **Script** downloads files from Google Drive
5. **Script** copies files to your local Git repository
6. **Script** commits and pushes to GitHub automatically

**Why Google Drive?**
- Bridge between Manus sandbox and your local machine
- No direct GitHub API access needed from sandbox
- You maintain full control over what gets committed

---

## One-Time Setup

### On Your Local Machine

**1. Install rclone** (if not already installed):

```bash
# macOS
brew install rclone

# Linux
sudo apt install rclone
```

**2. Configure rclone with Google Drive**:

```bash
rclone config
```

Follow prompts:
- Choose "n" for new remote
- Name it: `manus_google_drive`
- Choose "Google Drive"
- Follow OAuth flow to authenticate

**3. Get the sync script**:

The script is included in this skill at `scripts/gdrive_to_repo_sync.py`.

Copy it to your home directory:

```bash
cp /path/to/this/skill/scripts/gdrive_to_repo_sync.py ~/
chmod +x ~/gdrive_to_repo_sync.py
```

**4. Test the setup**:

```bash
rclone lsd manus_google_drive:
```

You should see your Google Drive folders listed.

---

## Usage Examples

### Example 1: Sync a Single Skill

**In Manus**:
```
Sync /home/ubuntu/skills/organize-github-repos to GitHub
```

**Manus provides**:
```
✅ Uploaded to Google Drive: github-sync-1770720864

📋 Run this command on your local machine:
python3 ~/gdrive_to_repo_sync.py github-sync-1770720864 ~/my-repo "feat: add organize-github-repos skill"
```

**You run**:
```bash
python3 ~/gdrive_to_repo_sync.py github-sync-1770720864 ~/my-repo "feat: add organize-github-repos skill"
```

**Result**:
```
✅ Downloaded from Google Drive
✅ Copied to repository
✅ Committed changes
✅ Pushed to GitHub
```

---

### Example 2: Sync Multiple Files

**In Manus**:
```
Sync these to GitHub:
- /home/ubuntu/skills/skill-a
- /home/ubuntu/skills/skill-b  
- /home/ubuntu/docs/guide.md
```

**Manus handles the rest** and provides the sync command.

---

### Example 3: Custom Commit Message

**In Manus**:
```
Sync /home/ubuntu/project with commit message "fix: resolve authentication bug"
```

**Manus provides** command with your custom message.

---

## The Sync Script

### Script Location

After setup: `~/gdrive_to_repo_sync.py`

### Script Usage

```bash
python3 ~/gdrive_to_repo_sync.py <gdrive-folder> <repo-path> "<commit-message>"
```

**Arguments**:
1. `<gdrive-folder>` - Folder name from Manus (e.g., `github-sync-1770720864`)
2. `<repo-path>` - Path to your local Git repository (e.g., `~/my-repo`)
3. `<commit-message>` - Git commit message in quotes

### What the Script Does

1. Downloads files from Google Drive folder
2. Copies to your local repository (preserving structure)
3. Stages changes (`git add`)
4. Commits with your message
5. Pushes to origin (current branch)
6. Cleans up temporary files

---

## Troubleshooting

### "rclone not found"

**Solution**: Install rclone
```bash
brew install rclone  # macOS
sudo apt install rclone  # Linux
```

### "Google Drive folder not found"

**Check folder exists**:
```bash
rclone lsd manus_google_drive: | grep github-sync
```

**Common causes**:
- Typo in folder name (case-sensitive)
- rclone not configured correctly
- Using wrong Google account

### "Git push failed"

**Solution**: Set up GitHub authentication
```bash
gh auth login  # Using GitHub CLI
# OR configure SSH keys
```

### "Permission denied"

**Solution**: Make script executable
```bash
chmod +x ~/gdrive_to_repo_sync.py
```

---

## Best Practices

1. **Use descriptive commit messages** - Follow [Conventional Commits](https://www.conventionalcommits.org/)
2. **Review before running** - Check what Manus uploaded to Google Drive
3. **Clean up old folders** - Delete old `github-sync-*` folders from Google Drive periodically
4. **Test with small changes** - Verify workflow before syncing large projects
5. **Keep script updated** - Pull latest version if bugs are fixed

---

## Advanced Usage

### Sync to Specific Branch

```bash
cd ~/my-repo
git checkout feature-branch
python3 ~/gdrive_to_repo_sync.py <folder> . "commit message"
```

### Sync to Subdirectory

The script preserves directory structure from Google Drive.

**In Manus**, organize files in the structure you want:
```
/tmp/sync-package/
└── skills/
    └── my-skill/
        └── ...
```

**Result in repo**: `repo/skills/my-skill/...`

### Dry Run (Preview)

Modify script to add `--dry-run` flag:

```python
if '--dry-run' in sys.argv:
    print("Would commit:", files)
    sys.exit(0)
```

---

## Security

**Google Drive**:
- rclone stores credentials securely
- Folders are timestamped (not predictable)
- Only accessible to your Google account

**Git**:
- Uses your existing authentication
- No credentials stored by script
- Standard `git push` (SSH/HTTPS)

**Files**:
- Permissions preserved where possible
- No sensitive data logged

---

## Limitations

1. **Requires local execution** - Can't be fully autonomous without local agent
2. **Google Drive dependency** - Adds latency vs direct GitHub API
3. **Manual branch management** - Doesn't auto-create branches
4. **No conflict resolution** - Requires manual intervention for conflicts
5. **Single remote** - Pushes to `origin` only

---

## Future Enhancements

- [ ] Webhook-based automatic sync (no manual command)
- [ ] Direct GitHub API integration (bypass Google Drive)
- [ ] Automatic branch creation
- [ ] Conflict resolution
- [ ] Multi-remote support
- [ ] Notifications (Slack/Discord)

---

## Related Skills

- **skill-development-workflow** - Create new skills
- **autonomous-github-sync** - Original implementation (this improves on it)
- **organize-github-repos** - Verify GitHub repo alignment

---

## Support

**Check Google Drive connection**:
```bash
rclone about manus_google_drive:
```

**List sync folders**:
```bash
rclone lsd manus_google_drive: | grep github-sync
```

**Verify Git repo**:
```bash
cd ~/my-repo && git status
```

---

## Changelog

### v1.0.0 (2026-02-10)
- ✅ Initial release
- ✅ Google Drive upload automation
- ✅ One-command sync script
- ✅ Comprehensive documentation
