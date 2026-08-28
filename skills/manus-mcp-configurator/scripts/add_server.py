#!/usr/bin/env python3
"""
Add a new MCP server to Manus configuration.

Usage:
    python add_server.py --name <name> --url <url> [--description <desc>]
"""

import json
import argparse
import sys
from pathlib import Path


def find_config_file():
    """Locate the Manus MCP configuration file."""
    import os
    
    # Check environment variable first
    env_path_str = os.environ.get("MANUS_CONFIG_PATH", "")
    if env_path_str:
        env_path = Path(env_path_str)
        if env_path.exists() and env_path.is_file():
            return env_path
    
    # Check known locations
    possible_locations = [
        Path.home() / ".config" / "manus" / "mcp_config.json",
        Path.home() / ".manus" / "mcp_config.json",
        Path.home() / "Library" / "Application Support" / "Manus" / "mcp_config.json",
    ]
    
    for path in possible_locations:
        if path.exists() and path.is_file():
            return path
    
    # Return default location (will be created if doesn't exist)
    return Path.home() / ".config" / "manus" / "mcp_config.json"


def load_config(config_path):
    """Load the MCP configuration file."""
    if not config_path or not config_path.exists() or config_path.is_dir():
        # Create default structure
        return {"mcp_servers": []}
    
    with open(config_path, 'r') as f:
        return json.load(f)


def save_config(config_path, config):
    """Save the MCP configuration file."""
    # Ensure we have a valid file path
    if not config_path or config_path.is_dir():
        config_path = Path.home() / ".config" / "manus" / "mcp_config.json"
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def add_server(name, url, description=None):
    """Add a new MCP server to the configuration."""
    config_path = find_config_file()
    config = load_config(config_path)
    
    # Check if server already exists
    if "mcp_servers" not in config:
        config["mcp_servers"] = []
    
    for server in config["mcp_servers"]:
        if server.get("name") == name:
            print(f"❌ Error: Server '{name}' already exists in configuration.")
            print(f"   Use remove_server.py to remove it first, or choose a different name.")
            return False
    
    # Create new server entry
    new_server = {
        "name": name,
        "url": url,
        "auth": None
    }
    
    if description:
        new_server["description"] = description
    
    # Add to config
    config["mcp_servers"].append(new_server)
    
    # Save
    save_config(config_path, config)
    
    print(f"✅ Successfully added MCP server '{name}'")
    print(f"   URL: {url}")
    if description:
        print(f"   Description: {description}")
    print(f"   Config file: {config_path}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Add a new MCP server to Manus configuration")
    parser.add_argument("--name", required=True, help="Server name (e.g., 'wade-skillz')")
    parser.add_argument("--url", required=True, help="Server URL (e.g., 'http://127.0.0.1:8081/mcp')")
    parser.add_argument("--description", help="Optional server description")
    
    args = parser.parse_args()
    
    success = add_server(args.name, args.url, args.description)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    import os
    main()
