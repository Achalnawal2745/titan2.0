#!/usr/bin/env python3
"""
Automated Git commit and push with intelligent commit message generation.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def get_git_status(repo_dir):
    """Get git status information."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def get_changed_files(repo_dir):
    """Get list of changed files."""
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    staged = result.stdout.strip().split("\n") if result.stdout.strip() else []
    
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    unstaged = result.stdout.strip().split("\n") if result.stdout.strip() else []
    
    return list(set(staged + unstaged))

def generate_commit_message(changed_files):
    """Generate intelligent commit message based on changed files."""
    if not changed_files:
        return "Update files"
    
    # Analyze file types
    file_types = {}
    for file in changed_files:
        if not file:
            continue
        ext = Path(file).suffix or "other"
        file_types[ext] = file_types.get(ext, 0) + 1
    
    # Generate message based on patterns
    if ".md" in file_types and len(file_types) == 1:
        return "Update documentation"
    elif ".py" in file_types:
        return "Update Python code"
    elif ".js" in file_types or ".ts" in file_types:
        return "Update JavaScript/TypeScript code"
    elif ".json" in file_types:
        return "Update configuration"
    elif ".css" in file_types or ".scss" in file_types:
        return "Update styles"
    elif len(changed_files) == 1:
        return f"Update {Path(changed_files[0]).name}"
    else:
        return f"Update {len(changed_files)} files"

def git_add_all(repo_dir):
    """Stage all changes."""
    result = subprocess.run(
        ["git", "add", "."],
        cwd=repo_dir
    )
    return result.returncode == 0

def git_commit(repo_dir, message):
    """Commit changes."""
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout + result.stderr

def git_push(repo_dir, branch="main"):
    """Push to remote."""
    result = subprocess.run(
        ["git", "push", "origin", branch],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout + result.stderr

def get_current_branch(repo_dir):
    """Get current branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: auto_commit.py <repo_directory> [commit_message]")
        print("Example: auto_commit.py /path/to/repo")
        print("         auto_commit.py /path/to/repo \"Custom commit message\"")
        sys.exit(1)
    
    repo_dir = sys.argv[1]
    custom_message = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.isdir(repo_dir):
        print(f"❌ Error: {repo_dir} is not a valid directory")
        sys.exit(1)
    
    if not os.path.isdir(os.path.join(repo_dir, ".git")):
        print(f"❌ Error: {repo_dir} is not a git repository")
        sys.exit(1)
    
    print(f"📁 Repository: {repo_dir}")
    
    # Check for changes
    status = get_git_status(repo_dir)
    if not status:
        print("✅ No changes to commit")
        sys.exit(0)
    
    print(f"📝 Changes detected:")
    print(status)
    print()
    
    # Get changed files
    changed_files = get_changed_files(repo_dir)
    
    # Generate or use custom commit message
    if custom_message:
        commit_message = custom_message
    else:
        commit_message = generate_commit_message(changed_files)
    
    print(f"💬 Commit message: {commit_message}")
    print()
    
    # Stage all changes
    print("📦 Staging changes...")
    if not git_add_all(repo_dir):
        print("❌ Failed to stage changes")
        sys.exit(1)
    
    # Commit
    print("💾 Committing...")
    success, output = git_commit(repo_dir, commit_message)
    if not success:
        print(f"❌ Failed to commit:")
        print(output)
        sys.exit(1)
    
    print("✅ Committed successfully")
    print()
    
    # Get current branch
    branch = get_current_branch(repo_dir)
    print(f"🌿 Current branch: {branch}")
    
    # Push
    print(f"🚀 Pushing to origin/{branch}...")
    success, output = git_push(repo_dir, branch)
    if not success:
        print(f"❌ Failed to push:")
        print(output)
        sys.exit(1)
    
    print("✅ Pushed successfully!")
    print()
    print("🎉 All done!")

if __name__ == "__main__":
    main()
