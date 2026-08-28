---
name: "manus-mcp-configurator"
description: "Specialized skill for manus mcp configurator workflows and automation."
---

# Manus MCP Configurator

Automate the management of MCP (Model Context Protocol) servers in your Manus configuration.

## Quick Start

Add the two WADE MCP servers:

```bash
# Add wade-skillz server
python /home/ubuntu/skills/manus-mcp-configurator/scripts/add_server.py \
  --name "wade-skillz" \
  --url "http://127.0.0.1:8081/mcp" \
  --description "WADE Skill Hub: Exposes all local skills as MCP tools"

# Add wade-skill-tester server
python /home/ubuntu/skills/manus-mcp-configurator/scripts/add_server.py \
  --name "wade-skill-tester" \
  --url "http://127.0.0.1:8082/mcp" \
  --description "WADE Skill-Test-Runner: Automated skill testing tools"
```

## Operations

### Add a Server

```bash
python scripts/add_server.py --name <name> --url <url> [--description <desc>]
```

**Parameters:**
- `--name`: Unique server identifier (e.g., "wade-skillz")
- `--url`: Full MCP endpoint URL (e.g., "http://127.0.0.1:8081/mcp")
- `--description`: Optional human-readable description

**Example:**
```bash
python scripts/add_server.py \
  --name "my-custom-server" \
  --url "http://localhost:9000/mcp" \
  --description "My custom MCP server"
```

### List All Servers

```bash
python scripts/list_servers.py [--json]
```

**Options:**
- `--json`: Output as JSON instead of human-readable table

**Example output:**
```
📋 Configured MCP Servers (2 total):
================================================================================

1. wade-skillz
   URL: http://127.0.0.1:8081/mcp
   Description: WADE Skill Hub: Exposes all local skills as MCP tools

2. wade-skill-tester
   URL: http://127.0.0.1:8082/mcp
   Description: WADE Skill-Test-Runner: Automated skill testing tools
```

### Remove a Server

```bash
python scripts/remove_server.py --name <name>
```

**Parameters:**
- `--name`: Name of the server to remove

**Example:**
```bash
python scripts/remove_server.py --name "wade-skillz"
```

### Validate Configuration

```bash
python scripts/validate_config.py
```

Checks the configuration file for:
- Valid JSON syntax
- Required fields present
- Proper data types
- URL format correctness

## Configuration File

The scripts automatically locate your Manus MCP configuration file by searching these locations in order:

1. `~/.config/manus/mcp_config.json`
2. `~/.manus/mcp_config.json`
3. `~/Library/Application Support/Manus/mcp_config.json` (macOS)
4. `$MANUS_CONFIG_PATH` environment variable
5. `./manus_mcp_config.json` (fallback for testing)

For detailed format specification, see `references/config-format.md`.

## Troubleshooting

**"No Manus MCP configuration file found"**
- The configuration file doesn't exist yet
- Set `MANUS_CONFIG_PATH` environment variable to the correct location
- Or create a new file at `~/.config/manus/mcp_config.json`

**"Server already exists"**
- Use `remove_server.py` to remove the existing server first
- Or choose a different server name

**"Invalid JSON"**
- Run `validate_config.py` to see specific errors
- Check for missing commas, brackets, or quotes
- Restore from backup if available

## Best Practices

1. **Validate after changes**: Run `validate_config.py` after adding or removing servers
2. **Use descriptive names**: Choose clear, unique names for servers
3. **Add descriptions**: Include descriptions to document server purposes
4. **Backup configuration**: Keep a backup before making changes
5. **Test servers**: Verify servers are running before adding them

## Examples

**Add multiple servers at once:**
```bash
# Add all WADE servers
for server in "wade-skillz:8081" "wade-skill-tester:8082" "wade-registry:8083"; do
  IFS=':' read -r name port <<< "$server"
  python scripts/add_server.py \
    --name "$name" \
    --url "http://127.0.0.1:$port/mcp" \
    --description "WADE MCP Server: $name"
done
```

**List and validate:**
```bash
# Show current configuration
python scripts/list_servers.py

# Validate it
python scripts/validate_config.py
```

**Clean up test servers:**
```bash
# Remove all test servers
for name in "test-server-1" "test-server-2" "test-server-3"; do
  python scripts/remove_server.py --name "$name"
done
```
