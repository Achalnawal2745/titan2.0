#!/usr/bin/env python3
"""
Google Drive to GitHub Repository Sync Script

Downloads files from Google Drive and automatically commits/pushes to GitHub repository.

Usage:
    python3 gdrive_to_repo_sync.py <gdrive-folder> <repo-path> "<commit-message>"

Example:
    python3 gdrive_to_repo_sync.py github-sync-1770720864 ~/my-repo "feat: add new skill"

Requirements:
    - rclone configured with 'manus_google_drive' remote
    - Git repository with remote configured
    - GitHub authentication set up (gh CLI or SSH)
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

def print_step(step, message):
    """Print formatted step message"""
    print(f"\n{'='*60}")
    print(f"Step {step}: {message}")
    print('='*60)

def run_command(cmd, cwd=None, check=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def check_prerequisites():
    """Check that required tools are installed"""
    print_step(1, "Checking prerequisites")
    
    # Check rclone
    result = run_command("which rclone", check=False)
    if result.returncode != 0:
        print("❌ rclone not found. Please install it:")
        print("   macOS: brew install rclone")
        print("   Linux: sudo apt install rclone")
        sys.exit(1)
    print("✅ rclone found")
    
    # Check rclone config
    result = run_command("rclone listremotes", check=False)
    if "manus_google_drive:" not in result.stdout:
        print("❌ rclone remote 'manus_google_drive' not configured")
        print("   Run: rclone config")
        sys.exit(1)
    print("✅ rclone configured with manus_google_drive")
    
    # Check git
    result = run_command("which git", check=False)
    if result.returncode != 0:
        print("❌ git not found. Please install it.")
        sys.exit(1)
    print("✅ git found")

def download_from_gdrive(gdrive_folder):
    """Download files from Google Drive to temp directory"""
    print_step(2, f"Downloading from Google Drive: {gdrive_folder}")
    
    # Create temp directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"/tmp/gdrive-sync-{timestamp}"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Download using rclone
    cmd = f"rclone copy manus_google_drive:{gdrive_folder} {temp_dir}"
    print(f"Running: {cmd}")
    
    result = run_command(cmd)
    
    # Check if files were downloaded
    if not os.listdir(temp_dir):
        print(f"❌ No files downloaded from {gdrive_folder}")
        print("   Check that the folder exists in Google Drive:")
        print(f"   rclone lsd manus_google_drive: | grep {gdrive_folder}")
        sys.exit(1)
    
    print(f"✅ Downloaded to {temp_dir}")
    
    # List downloaded files
    print("\nDownloaded files:")
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), temp_dir)
            print(f"  - {rel_path}")
    
    return temp_dir

def copy_to_repo(temp_dir, repo_path):
    """Copy files from temp directory to repository"""
    print_step(3, f"Copying files to repository: {repo_path}")
    
    # Verify repo exists
    if not os.path.exists(repo_path):
        print(f"❌ Repository not found: {repo_path}")
        sys.exit(1)
    
    # Verify it's a git repo
    git_dir = os.path.join(repo_path, ".git")
    if not os.path.exists(git_dir):
        print(f"❌ Not a git repository: {repo_path}")
        print("   Initialize with: git init")
        sys.exit(1)
    
    print(f"✅ Repository found: {repo_path}")
    
    # Copy files
    copied_files = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            src = os.path.join(root, file)
            rel_path = os.path.relpath(src, temp_dir)
            dest = os.path.join(repo_path, rel_path)
            
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            
            # Copy file
            shutil.copy2(src, dest)
            copied_files.append(rel_path)
            print(f"  ✅ Copied: {rel_path}")
    
    print(f"\n✅ Copied {len(copied_files)} file(s)")
    return copied_files

def commit_and_push(repo_path, commit_message, copied_files):
    """Commit changes and push to GitHub"""
    print_step(4, "Committing and pushing to GitHub")
    
    # Add files
    print("Adding files to git...")
    for file in copied_files:
        run_command(f"git add '{file}'", cwd=repo_path)
    print(f"✅ Added {len(copied_files)} file(s)")
    
    # Check if there are changes to commit
    result = run_command("git diff --cached --quiet", cwd=repo_path, check=False)
    if result.returncode == 0:
        print("⚠️  No changes to commit (files may already be up to date)")
        return False
    
    # Commit
    print(f"Committing with message: {commit_message}")
    run_command(f"git commit -m '{commit_message}'", cwd=repo_path)
    print("✅ Committed")
    
    # Push
    print("Pushing to GitHub...")
    result = run_command("git push", cwd=repo_path, check=False)
    
    if result.returncode != 0:
        print("❌ Push failed. Common causes:")
        print("   - GitHub authentication not set up (run: gh auth login)")
        print("   - Remote not configured (run: git remote -v)")
        print("   - Need to pull first (run: git pull)")
        print("\nError output:")
        print(result.stderr)
        sys.exit(1)
    
    print("✅ Pushed to GitHub")
    return True

def cleanup(temp_dir):
    """Clean up temporary directory"""
    print_step(5, "Cleaning up")
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"✅ Removed temporary directory: {temp_dir}")

def main():
    """Main sync workflow"""
    if len(sys.argv) != 4:
        print("Usage: python3 gdrive_to_repo_sync.py <gdrive-folder> <repo-path> \"<commit-message>\"")
        print("\nExample:")
        print("  python3 gdrive_to_repo_sync.py github-sync-1770720864 ~/my-repo \"feat: add new skill\"")
        sys.exit(1)
    
    gdrive_folder = sys.argv[1]
    repo_path = os.path.expanduser(sys.argv[2])
    commit_message = sys.argv[3]
    
    print("🚀 GitHub Sync Script")
    print(f"   Google Drive folder: {gdrive_folder}")
    print(f"   Repository: {repo_path}")
    print(f"   Commit message: {commit_message}")
    
    try:
        # Run workflow
        check_prerequisites()
        temp_dir = download_from_gdrive(gdrive_folder)
        copied_files = copy_to_repo(temp_dir, repo_path)
        success = commit_and_push(repo_path, commit_message, copied_files)
        cleanup(temp_dir)
        
        # Summary
        print("\n" + "="*60)
        print("✅ SYNC COMPLETE")
        print("="*60)
        if success:
            print(f"✅ {len(copied_files)} file(s) synced to GitHub")
            print(f"✅ Commit: {commit_message}")
            print(f"✅ Repository: {repo_path}")
        else:
            print("⚠️  No changes committed (files already up to date)")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        if 'temp_dir' in locals():
            cleanup(temp_dir)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        if 'temp_dir' in locals():
            cleanup(temp_dir)
        sys.exit(1)

if __name__ == "__main__":
    main()
