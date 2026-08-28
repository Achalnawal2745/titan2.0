#!/usr/bin/env python3
"""
List all configured MCP servers in Manus.

Usage:
    python list_servers.py [--json]
"""

import json
import argparse
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


def list_servers(output_json=False):
    """List all configured MCP servers."""
    config_path = find_config_file()
    
    if not config_path or not config_path.exists():
        print("❌ No Manus MCP configuration file found.")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    servers = config.get("mcp_servers", [])
    
    if not servers:
        print("📭 No MCP servers configured.")
        return
    
    if output_json:
        print(json.dumps(servers, indent=2))
    else:
        print(f"📋 Configured MCP Servers ({len(servers)} total):")
        print("=" * 80)
        for i, server in enumerate(servers, 1):
            print(f"\n{i}. {server.get('name', 'Unnamed')}")
            print(f"   URL: {server.get('url', 'N/A')}")
            if server.get('description'):
                print(f"   Description: {server['description']}")
            if server.get('auth'):
                print(f"   Auth: {server['auth']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="List all configured MCP servers")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    list_servers(args.json)


if __name__ == "__main__":
    main()
