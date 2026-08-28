#!/usr/bin/env python3
"""
Google Drive to Repository Sync Script

Syncs files from a Google Drive folder to a local git repository,
commits changes, and pushes to GitHub.

Usage:
    python gdrive_to_repo_sync.py <gdrive_folder_id> <local_repo_path> <commit_message>
"""

import sys
import os
import subprocess
import shutil

def run_command(cmd, cwd=None):
    """Run a shell command and return output"""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def main():
    if len(sys.argv) < 4:
        print("Usage: python gdrive_to_repo_sync.py <gdrive_folder_id> <local_repo_path> <commit_message>")
        sys.exit(1)
    
    gdrive_folder_id = sys.argv[1]
    local_repo_path = sys.argv[2]
    commit_message = sys.argv[3]
    
    # Step 1: Download from Google Drive to temp location
    temp_dir = "/tmp/gdrive_sync"
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"📥 Downloading from Google Drive folder: {gdrive_folder_id}")
    returncode, stdout, stderr = run_command(
        f"rclone copy manus_google_drive:{gdrive_folder_id} {temp_dir} --config /home/ubuntu/.gdrive-rclone.ini"
    )
    
    if returncode != 0:
        print(f"❌ Error downloading from Google Drive: {stderr}")
        sys.exit(1)
    
    print(f"✅ Downloaded files to {temp_dir}")
    
    # Step 2: Copy files to local repository
    print(f"📋 Copying files to {local_repo_path}")
    
    # Get list of files in temp_dir
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            src_path = os.path.join(root, file)
            # Calculate relative path
            rel_path = os.path.relpath(src_path, temp_dir)
            dest_path = os.path.join(local_repo_path, rel_path)
            
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Copy file
            shutil.copy2(src_path, dest_path)
            print(f"  ✓ {rel_path}")
    
    # Step 3: Git add, commit, and push
    print(f"\n📝 Committing changes...")
    
    # Add all changes
    returncode, stdout, stderr = run_command("git add .", cwd=local_repo_path)
    if returncode != 0:
        print(f"❌ Error adding files: {stderr}")
        sys.exit(1)
    
    # Check if there are changes to commit
    returncode, stdout, stderr = run_command("git status --porcelain", cwd=local_repo_path)
    if not stdout.strip():
        print("ℹ️  No changes to commit")
        return
    
    # Commit
    returncode, stdout, stderr = run_command(
        f'git commit -m "{commit_message}"',
        cwd=local_repo_path
    )
    if returncode != 0:
        print(f"❌ Error committing: {stderr}")
        sys.exit(1)
    
    print(f"✅ Committed: {commit_message}")
    
    # Push
    print(f"📤 Pushing to GitHub...")
    returncode, stdout, stderr = run_command("git push origin main", cwd=local_repo_path)
    if returncode != 0:
        print(f"❌ Error pushing: {stderr}")
        sys.exit(1)
    
    print(f"✅ Successfully pushed to GitHub!")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print(f"🧹 Cleaned up temporary files")

if __name__ == "__main__":
    main()
