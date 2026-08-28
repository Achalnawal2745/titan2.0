#!/usr/bin/env python3
"""
Automated deployment script for Vercel, Railway, and other platforms.
Handles environment detection, configuration, and one-command deployment.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def detect_platform(project_dir):
    """Detect which platform the project is configured for."""
    project_path = Path(project_dir)
    
    platforms = []
    
    # Check for Vercel
    if (project_path / "vercel.json").exists() or (project_path / ".vercel").exists():
        platforms.append("vercel")
    
    # Check for Railway
    if (project_path / "railway.json").exists() or (project_path / "railway.toml").exists():
        platforms.append("railway")
    
    # Check for Netlify
    if (project_path / "netlify.toml").exists():
        platforms.append("netlify")
    
    # Check for Heroku
    if (project_path / "Procfile").exists():
        platforms.append("heroku")
    
    # Check for package.json scripts
    package_json = project_path / "package.json"
    if package_json.exists():
        with open(package_json) as f:
            data = json.load(f)
            scripts = data.get("scripts", {})
            if "deploy" in scripts:
                platforms.append("custom")
    
    return platforms

def check_cli_installed(platform):
    """Check if platform CLI is installed."""
    cli_commands = {
        "vercel": "vercel",
        "railway": "railway",
        "netlify": "netlify",
        "heroku": "heroku"
    }
    
    cmd = cli_commands.get(platform)
    if not cmd:
        return True  # Custom platform, assume ready
    
    try:
        result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_cli(platform):
    """Install platform CLI."""
    install_commands = {
        "vercel": "npm install -g vercel",
        "railway": "npm install -g @railway/cli",
        "netlify": "npm install -g netlify-cli",
        "heroku": "curl https://cli-assets.heroku.com/install.sh | sh"
    }
    
    cmd = install_commands.get(platform)
    if not cmd:
        print(f"⚠️  No automatic installation for {platform}")
        return False
    
    print(f"📦 Installing {platform} CLI...")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def deploy_vercel(project_dir, production=True):
    """Deploy to Vercel."""
    print("🚀 Deploying to Vercel...")
    
    cmd = ["vercel"]
    if production:
        cmd.append("--prod")
    
    result = subprocess.run(cmd, cwd=project_dir)
    return result.returncode == 0

def deploy_railway(project_dir):
    """Deploy to Railway."""
    print("🚀 Deploying to Railway...")
    
    result = subprocess.run(["railway", "up"], cwd=project_dir)
    return result.returncode == 0

def deploy_netlify(project_dir, production=True):
    """Deploy to Netlify."""
    print("🚀 Deploying to Netlify...")
    
    cmd = ["netlify", "deploy"]
    if production:
        cmd.append("--prod")
    
    result = subprocess.run(cmd, cwd=project_dir)
    return result.returncode == 0

def deploy_heroku(project_dir):
    """Deploy to Heroku."""
    print("🚀 Deploying to Heroku...")
    
    result = subprocess.run(["git", "push", "heroku", "main"], cwd=project_dir)
    return result.returncode == 0

def deploy_custom(project_dir):
    """Deploy using custom npm script."""
    print("🚀 Running custom deploy script...")
    
    result = subprocess.run(["npm", "run", "deploy"], cwd=project_dir)
    return result.returncode == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: deploy.py <project_directory> [--preview]")
        print("Example: deploy.py /path/to/project")
        print("         deploy.py /path/to/project --preview")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    production = "--preview" not in sys.argv
    
    if not os.path.isdir(project_dir):
        print(f"❌ Error: {project_dir} is not a valid directory")
        sys.exit(1)
    
    print(f"📁 Project: {project_dir}")
    print(f"🎯 Mode: {'Production' if production else 'Preview'}")
    print()
    
    # Detect platforms
    platforms = detect_platform(project_dir)
    
    if not platforms:
        print("❌ No deployment platform detected")
        print("   Supported: Vercel, Railway, Netlify, Heroku, or custom npm script")
        sys.exit(1)
    
    print(f"✅ Detected platforms: {', '.join(platforms)}")
    print()
    
    # Use first detected platform
    platform = platforms[0]
    
    # Check CLI installed
    if not check_cli_installed(platform):
        print(f"⚠️  {platform} CLI not installed")
        if input(f"Install {platform} CLI? (y/n): ").lower() == 'y':
            if not install_cli(platform):
                print(f"❌ Failed to install {platform} CLI")
                sys.exit(1)
        else:
            print("❌ Deployment cancelled")
            sys.exit(1)
    
    # Deploy
    deploy_functions = {
        "vercel": lambda: deploy_vercel(project_dir, production),
        "railway": lambda: deploy_railway(project_dir),
        "netlify": lambda: deploy_netlify(project_dir, production),
        "heroku": lambda: deploy_heroku(project_dir),
        "custom": lambda: deploy_custom(project_dir)
    }
    
    deploy_func = deploy_functions.get(platform)
    if not deploy_func:
        print(f"❌ No deployment function for {platform}")
        sys.exit(1)
    
    success = deploy_func()
    
    if success:
        print()
        print("✅ Deployment successful!")
    else:
        print()
        print("❌ Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
