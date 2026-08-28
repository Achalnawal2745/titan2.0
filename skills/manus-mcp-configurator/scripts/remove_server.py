#!/usr/bin/env python3
"""
Remove an MCP server from Manus configuration.

Usage:
    python remove_server.py --name <name>
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
    
    return None


def remove_server(name):
    """Remove an MCP server from the configuration."""
    config_path = find_config_file()
    
    if not config_path or not config_path.exists():
        print("❌ No Manus MCP configuration file found.")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    servers = config.get("mcp_servers", [])
    
    # Find and remove the server
    original_count = len(servers)
    config["mcp_servers"] = [s for s in servers if s.get("name") != name]
    
    if len(config["mcp_servers"]) == original_count:
        print(f"❌ Server '{name}' not found in configuration.")
        return False
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Successfully removed MCP server '{name}'")
    print(f"   Config file: {config_path}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Remove an MCP server from Manus configuration")
    parser.add_argument("--name", required=True, help="Server name to remove")
    
    args = parser.parse_args()
    
    success = remove_server(args.name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
