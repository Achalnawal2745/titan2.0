#!/usr/bin/env python3
"""
Validate the Manus MCP configuration file.

Usage:
    python validate_config.py
"""

import json
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


def validate_config():
    """Validate the MCP configuration file."""
    config_path = find_config_file()
    
    if not config_path or not config_path.exists():
        print("❌ No Manus MCP configuration file found.")
        return False
    
    print(f"📋 Validating: {config_path}")
    print("=" * 80)
    
    errors = []
    warnings = []
    
    # Try to parse JSON
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    
    # Check structure
    if "mcp_servers" not in config:
        errors.append("Missing 'mcp_servers' key in configuration")
    elif not isinstance(config["mcp_servers"], list):
        errors.append("'mcp_servers' must be a list")
    else:
        servers = config["mcp_servers"]
        print(f"\n✅ Found {len(servers)} server(s)")
        
        # Validate each server
        for i, server in enumerate(servers, 1):
            print(f"\nServer {i}: {server.get('name', 'UNNAMED')}")
            
            # Required fields
            if "name" not in server:
                errors.append(f"Server {i}: Missing 'name' field")
            elif not server["name"]:
                errors.append(f"Server {i}: 'name' cannot be empty")
            
            if "url" not in server:
                errors.append(f"Server {i}: Missing 'url' field")
            elif not server["url"]:
                errors.append(f"Server {i}: 'url' cannot be empty")
            elif not server["url"].startswith(("http://", "https://")):
                warnings.append(f"Server {i}: URL should start with http:// or https://")
            
            # Optional fields
            if "description" in server:
                print(f"  Description: {server['description']}")
            
            if "auth" in server and server["auth"] is not None:
                print(f"  Auth: {server['auth']}")
    
    # Print results
    print("\n" + "=" * 80)
    
    if errors:
        print(f"\n❌ Validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ Configuration is valid!")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"   - {warning}")
    
    return len(errors) == 0


def main():
    validate_config()


if __name__ == "__main__":
    main()
