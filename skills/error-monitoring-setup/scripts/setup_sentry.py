#!/usr/bin/env python3
"""
Automated Sentry setup for Next.js, React, Node.js, and Python projects.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def detect_project_type(project_dir):
    """Detect project type based on files present."""
    project_path = Path(project_dir)
    
    # Check for package.json
    package_json = project_path / "package.json"
    if package_json.exists():
        with open(package_json) as f:
            data = json.load(f)
            dependencies = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            
            if "next" in dependencies:
                return "nextjs"
            elif "react" in dependencies:
                return "react"
            elif "express" in dependencies:
                return "node"
    
    # Check for Python
    if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
        return "python"
    
    return "unknown"

def install_sentry_package(project_dir, project_type):
    """Install Sentry package based on project type."""
    print(f"📦 Installing Sentry package for {project_type}...")
    
    if project_type in ["nextjs", "react", "node"]:
        result = subprocess.run(
            ["npm", "install", "--save", "@sentry/nextjs" if project_type == "nextjs" else "@sentry/react" if project_type == "react" else "@sentry/node"],
            cwd=project_dir
        )
        return result.returncode == 0
    elif project_type == "python":
        result = subprocess.run(
            ["pip", "install", "sentry-sdk"],
            cwd=project_dir
        )
        return result.returncode == 0
    
    return False

def create_sentry_config_nextjs(project_dir, dsn):
    """Create Sentry configuration for Next.js."""
    # Create sentry.client.config.js
    client_config = f"""import * as Sentry from "@sentry/nextjs";

Sentry.init({{
  dsn: "{dsn}",
  tracesSampleRate: 1.0,
  debug: false,
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  integrations: [
    new Sentry.Replay({{
      maskAllText: true,
      blockAllMedia: true,
    }}),
  ],
}});
"""
    
    with open(Path(project_dir) / "sentry.client.config.js", "w") as f:
        f.write(client_config)
    
    # Create sentry.server.config.js
    server_config = f"""import * as Sentry from "@sentry/nextjs";

Sentry.init({{
  dsn: "{dsn}",
  tracesSampleRate: 1.0,
  debug: false,
}});
"""
    
    with open(Path(project_dir) / "sentry.server.config.js", "w") as f:
        f.write(server_config)
    
    # Create sentry.edge.config.js
    edge_config = f"""import * as Sentry from "@sentry/nextjs";

Sentry.init({{
  dsn: "{dsn}",
  tracesSampleRate: 1.0,
  debug: false,
}});
"""
    
    with open(Path(project_dir) / "sentry.edge.config.js", "w") as f:
        f.write(edge_config)
    
    print("✅ Created Sentry config files")

def create_sentry_config_react(project_dir, dsn):
    """Create Sentry configuration for React."""
    config = f"""import * as Sentry from "@sentry/react";

Sentry.init({{
  dsn: "{dsn}",
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay(),
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
}});

export default Sentry;
"""
    
    with open(Path(project_dir) / "src" / "sentry.js", "w") as f:
        f.write(config)
    
    print("✅ Created Sentry config file")

def create_sentry_config_node(project_dir, dsn):
    """Create Sentry configuration for Node.js."""
    config = f"""const Sentry = require("@sentry/node");

Sentry.init({{
  dsn: "{dsn}",
  tracesSampleRate: 1.0,
}});

module.exports = Sentry;
"""
    
    with open(Path(project_dir) / "sentry.js", "w") as f:
        f.write(config)
    
    print("✅ Created Sentry config file")

def create_sentry_config_python(project_dir, dsn):
    """Create Sentry configuration for Python."""
    config = f"""import sentry_sdk

sentry_sdk.init(
    dsn="{dsn}",
    traces_sample_rate=1.0,
)
"""
    
    with open(Path(project_dir) / "sentry_config.py", "w") as f:
        f.write(config)
    
    print("✅ Created Sentry config file")

def main():
    if len(sys.argv) < 3:
        print("Usage: setup_sentry.py <project_directory> <sentry_dsn>")
        print("Example: setup_sentry.py /path/to/project https://...@sentry.io/...")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    dsn = sys.argv[2]
    
    if not os.path.isdir(project_dir):
        print(f"❌ Error: {project_dir} is not a valid directory")
        sys.exit(1)
    
    print(f"📁 Project: {project_dir}")
    print(f"🔑 DSN: {dsn[:20]}...")
    print()
    
    # Detect project type
    project_type = detect_project_type(project_dir)
    
    if project_type == "unknown":
        print("❌ Unable to detect project type")
        print("   Supported: Next.js, React, Node.js, Python")
        sys.exit(1)
    
    print(f"✅ Detected project type: {project_type}")
    print()
    
    # Install Sentry package
    if not install_sentry_package(project_dir, project_type):
        print("❌ Failed to install Sentry package")
        sys.exit(1)
    
    print("✅ Sentry package installed")
    print()
    
    # Create configuration
    print("📝 Creating Sentry configuration...")
    
    if project_type == "nextjs":
        create_sentry_config_nextjs(project_dir, dsn)
    elif project_type == "react":
        create_sentry_config_react(project_dir, dsn)
    elif project_type == "node":
        create_sentry_config_node(project_dir, dsn)
    elif project_type == "python":
        create_sentry_config_python(project_dir, dsn)
    
    print()
    print("✅ Sentry setup complete!")
    print()
    print("📋 Next steps:")
    
    if project_type == "nextjs":
        print("1. Import Sentry in your app (automatic with config files)")
        print("2. Test error tracking: throw new Error('Test error')")
        print("3. Check Sentry dashboard for errors")
    elif project_type == "react":
        print("1. Import Sentry in src/index.js:")
        print("   import './sentry';")
        print("2. Test error tracking: throw new Error('Test error')")
        print("3. Check Sentry dashboard for errors")
    elif project_type == "node":
        print("1. Import Sentry at the top of your main file:")
        print("   const Sentry = require('./sentry');")
        print("2. Test error tracking: throw new Error('Test error')")
        print("3. Check Sentry dashboard for errors")
    elif project_type == "python":
        print("1. Import Sentry in your main file:")
        print("   from sentry_config import *")
        print("2. Test error tracking: raise Exception('Test error')")
        print("3. Check Sentry dashboard for errors")

if __name__ == "__main__":
    main()
