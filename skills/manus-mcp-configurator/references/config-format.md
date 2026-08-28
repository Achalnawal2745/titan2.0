# Manus MCP Configuration Format

## File Structure

The Manus MCP configuration is stored as a JSON file with the following structure:

```json
{
  "mcp_servers": [
    {
      "name": "server-name",
      "url": "http://127.0.0.1:8081/mcp",
      "description": "Optional description",
      "auth": null
    }
  ]
}
```

## Field Specifications

### `mcp_servers` (required)
- **Type:** Array
- **Description:** List of configured MCP servers

### Server Object Fields

#### `name` (required)
- **Type:** String
- **Description:** Unique identifier for the server
- **Example:** `"wade-skillz"`, `"skill-test-runner"`

#### `url` (required)
- **Type:** String
- **Description:** Full URL to the MCP server endpoint
- **Format:** Must start with `http://` or `https://`
- **Example:** `"http://127.0.0.1:8081/mcp"`

#### `description` (optional)
- **Type:** String
- **Description:** Human-readable description of the server's purpose
- **Example:** `"WADE Skill Hub: Exposes all local skills"`

#### `auth` (optional)
- **Type:** String or null
- **Description:** Authentication configuration
- **Default:** `null` (no authentication)

## Example Configuration

```json
{
  "mcp_servers": [
    {
      "name": "wade-skillz",
      "url": "http://127.0.0.1:8081/mcp",
      "description": "WADE Skill Hub: Exposes all local skills in /home/ubuntu/skills as MCP tools.",
      "auth": null
    },
    {
      "name": "wade-skill-tester",
      "url": "http://127.0.0.1:8082/mcp",
      "description": "WADE Skill-Test-Runner: Provides tools to run automated tests against skills.",
      "auth": null
    }
  ]
}
```

## Configuration File Locations

The configuration file may be located at:

1. `~/.config/manus/mcp_config.json` (Linux/macOS)
2. `~/.manus/mcp_config.json`
3. `~/Library/Application Support/Manus/mcp_config.json` (macOS)
4. Custom location via `MANUS_CONFIG_PATH` environment variable
