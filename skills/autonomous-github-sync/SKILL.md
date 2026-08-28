---
name: "autonomous-github-sync"
description: "Specialized skill for autonomous github sync workflows and automation."
---

# Autonomous GitHub Sync

Enable Manus to commit and push changes to GitHub repositories without requiring manual user intervention.

## When to Use This Skill

Use this skill when:
- You've made changes to files in a repository and need to push them to GitHub
- The user requests autonomous git operations
- You want to avoid the manual "download patch → apply → push" workflow
- The user has Google Drive integration enabled

## How It Works

The sync workflow uses Google Drive as a bridge between the Manus sandbox and the user's local machine:

1. **Manus** uploads changed files to Google Drive
2. **User's local machine** (via script) downloads files from Google Drive
3. **Script** copies files to the local repository
4. **Script** commits and pushes to GitHub automatically

## Prerequisites

- User must have Google Drive integration enabled in Manus
- User must have the sync script running on their local machine
- User's local repository must be configured with GitHub authentication

## Usage Pattern

### Step 1: Upload Files to Google Drive

After making changes to repository files in the sandbox, upload them to a Google Drive folder:

```bash
# Create a deployment package with changed files
mkdir -p /tmp/repo-sync
cp /path/to/changed/file1.js /tmp/repo-sync/
cp /path/to/changed/file2.html /tmp/repo-sync/

# Upload to Google Drive
rclone copy /tmp/repo-sync manus_google_drive:repo-sync-$(date +%s) --config /home/ubuntu/.gdrive-rclone.ini

# Get the folder ID for the user
rclone lsd manus_google_drive: --config /home/ubuntu/.gdrive-rclone.ini | grep repo-sync
```

### Step 2: Notify User to Run Sync Script

Tell the user to run the sync script on their local machine:

```bash
python3 ~/gdrive_to_repo_sync.py <gdrive_folder_name> <local_repo_path> "<commit_message>"
```

Example:
```bash
python3 ~/gdrive_to_repo_sync.py repo-sync-1707543210 /Users/username/my-repo "feat: add demographic data collection"
```

### Step 3: Verify Push

Check GitHub or ask the user to confirm the push was successful.

## Alternative: Direct Patch Method

If Google Drive sync isn't set up, fall back to the patch method:

```bash
# Create patch file
cd /path/to/sandbox/repo
git format-patch origin/main --stdout > /tmp/changes.patch

# Upload patch to Google Drive
rclone copy /tmp/changes.patch manus_google_drive: --config /home/ubuntu/.gdrive-rclone.ini
rclone link manus_google_drive:changes.patch --config /home/ubuntu/.gdrive-rclone.ini
```

Then instruct the user:
```bash
# Download patch from Google Drive link
cd /path/to/local/repo
git am < ~/Downloads/changes.patch
git push origin main
```

## Setup Instructions for User

To enable autonomous sync, the user needs to:

1. **Copy the sync script to their home directory:**
   ```bash
   cp /home/ubuntu/skills/autonomous-github-sync/scripts/gdrive_to_repo_sync.py ~/
   ```

2. **Install rclone on their local machine** (if not already installed):
   ```bash
   # macOS
   brew install rclone
   
   # Linux
   sudo apt install rclone
   ```

3. **Configure rclone with the same Google Drive account:**
   ```bash
   rclone config
   # Follow prompts to add Google Drive remote named "manus_google_drive"
   ```

4. **Test the sync:**
   ```bash
   python3 ~/gdrive_to_repo_sync.py test-folder /path/to/repo "test commit"
   ```

## Troubleshooting

**"Repository not found" when pushing:**
- User's local machine needs GitHub authentication configured
- Check: `git remote -v` in the local repository
- Fix: `gh auth login` or configure SSH keys

**"rclone not found":**
- User needs to install rclone on their local machine
- See setup instructions above

**Files not syncing:**
- Verify Google Drive folder name is correct
- Check rclone config on user's machine matches Manus config
- Ensure user has permission to access the Google Drive folder

## Best Practices

1. **Use descriptive commit messages** - Include what changed and why
2. **Group related changes** - Don't sync every single file change individually
3. **Verify before pushing** - Check that files copied correctly
4. **Clean up Google Drive** - Remove old sync folders after successful push
5. **Test with small changes first** - Verify the workflow before large updates

## Limitations

- Requires user to run script manually (can't be fully autonomous without local agent)
- Depends on Google Drive as intermediary (adds latency)
- User must have rclone configured on local machine
- Works best for single-user workflows (not team collaboration)

## Future Improvements

- Webhook-based automatic sync when files appear in Google Drive
- Direct GitHub API integration (requires GitHub App or PAT)
- Support for multiple repositories
- Automatic conflict resolution
