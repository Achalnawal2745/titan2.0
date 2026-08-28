#!/usr/bin/env python3
"""Setup feature flags system for web applications"""
import os, sys, json

def detect_framework(project_dir):
    if os.path.exists(os.path.join(project_dir, "next.config.js")): return "nextjs"
    if os.path.exists(os.path.join(project_dir, "package.json")): return "react"
    return "unknown"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 setup_flags.py <project_dir>")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    framework = detect_framework(project_dir)
    print(f"✅ Detected: {framework}")
    print(f"📦 Installing feature flag dependencies...")
    os.system("npm install @vercel/flags")
    
    # Create flags config
    flags_config = {
        "flags": [
            {"key": "new_feature", "description": "Enable new feature", "origin": "https://example.com"},
            {"key": "beta_access", "description": "Beta features", "origin": "https://example.com"}
        ]
    }
    
    config_path = os.path.join(project_dir, "flags.json")
    with open(config_path, "w") as f:
        json.dump(flags_config, f, indent=2)
    
    print(f"✅ Feature flags setup complete!")

if __name__ == "__main__":
    main()
