---
name: "mcp-connector-tester"
description: "Specialized skill for mcp connector tester workflows and automation."
---

# MCP Connector Tester

Test and document MCP connectors systematically by exploring capabilities, verifying authentication, demonstrating features, and creating comprehensive documentation.

## When to Use

Use this skill when the user wants to:
- Test an MCP connector to see if it works
- Explore what an MCP connector can do
- Demonstrate features of an MCP connector
- Create documentation for an MCP connector
- Troubleshoot MCP connector authentication issues
- Show examples of using an MCP connector

## Testing Workflow

Follow this systematic approach for testing any MCP connector:

### Phase 1: Explore Capabilities

**List available tools:**
```bash
manus-mcp-cli tool list --server <server_name>
```

This returns a summary of all tools with descriptions. The detailed tool information is saved to a file in `~/.mcp/tool-lists/`.

**Key information to extract:**
- Total number of tools available
- Tool categories (group by functionality)
- Required vs optional parameters for each tool
- Authentication requirements mentioned in descriptions

**Save findings** to a text file for reference throughout testing.

### Phase 2: Test Authentication

**Check authentication status:**
```bash
manus-mcp-cli auth status --server <server_name>
```

**Common authentication patterns:**

1. **OAuth-based**: Requires `manus-mcp-cli auth login --server <server_name>`
2. **API Key/Token**: Requires configuration in MCP server settings
3. **No auth**: STDIO servers that work immediately

**Test connection with a simple tool:**
```bash
manus-mcp-cli tool call <simple_tool_name> --server <server_name> --input '{}'
```

Choose the simplest tool (usually a "list" or "get" operation) for initial testing.

**Common authentication errors:**

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Unauthorized" | Missing or invalid credentials | Configure API key/token in MCP settings |
| "JWT could not be decoded" | Wrong token type | Verify using correct credential type |
| "OAuth required" | Need to authenticate | Run `auth login` command |
| Connection timeout | Network or server issue | Check connectivity and server status |

### Phase 3: Demonstrate Features

**Select representative tools** from different categories to demonstrate:
- Basic operations (list, get, search)
- Create/modify operations (if safe to test)
- Advanced features (specific to the connector)

**For each demonstration:**
1. Explain what the tool does
2. Show the command with parameters
3. Execute and capture results
4. Explain the output
5. Save interesting results to files

**Safety considerations:**
- Avoid destructive operations (delete, drop, destroy) unless explicitly requested
- Use read-only operations when possible
- Warn before operations that incur costs
- Test on non-production resources when available

### Phase 4: Create Documentation

Generate comprehensive documentation covering:

1. **Overview Section**
   - Connector purpose and use cases
   - Total number of tools
   - Main capability categories

2. **Capabilities Section**
   - Organize tools by category
   - Describe what each category enables
   - Highlight unique or powerful features

3. **Authentication Setup**
   - Required credentials and where to get them
   - Step-by-step configuration instructions
   - Common authentication issues and solutions
   - Credential types and their purposes

4. **Example Operations**
   - Real examples with sample input/output
   - Common use cases
   - Best practices

5. **Troubleshooting Guide**
   - Common errors and solutions
   - Configuration verification steps
   - Support resources

**Documentation format:**
- Use clear section headings
- Include code blocks for commands
- Provide tables for comparisons
- Add real examples from testing
- Keep explanations concise but complete

## Authentication Configuration Guidance

When authentication is required, guide users through the configuration process:

### For API Key/Token Authentication

1. **Identify the credential type** from error messages or documentation
2. **Show where to obtain credentials** (usually a dashboard or settings page)
3. **Navigate to the credential page** using browser tools if helpful
4. **Document the configuration process:**
   - Where to input the credential in Manus
   - Environment variable names (if applicable)
   - Configuration file locations (if applicable)
5. **Verify configuration** by testing a simple operation
6. **Troubleshoot** if verification fails

### For OAuth Authentication

1. **Initiate OAuth flow:**
   ```bash
   manus-mcp-cli auth login --server <server_name>
   ```
2. **Follow the authentication prompts**
3. **Verify successful authentication:**
   ```bash
   manus-mcp-cli auth status --server <server_name>
   ```

## Documentation Templates

Use the templates in the `templates/` directory for consistent documentation:

- `connector_overview.md` - Main documentation structure
- `authentication_guide.md` - Authentication setup instructions
- `troubleshooting_guide.md` - Common issues and solutions

Customize these templates for each connector based on testing results.

## Best Practices

**Exploration:**
- Start with tool listing to understand scope
- Group tools by functionality for clarity
- Identify the simplest tool for initial testing

**Authentication:**
- Always check auth status first
- Document credential types clearly
- Distinguish between different credential purposes
- Provide visual guides when helpful

**Testing:**
- Test read-only operations first
- Use real data when available (with permission)
- Save interesting results for documentation
- Note any unexpected behavior

**Documentation:**
- Write for users who are new to the connector
- Include real examples from testing
- Provide troubleshooting for common issues
- Keep language clear and concise

**Safety:**
- Warn before destructive operations
- Avoid operations that incur costs without confirmation
- Test on non-production resources when possible
- Respect user data and privacy

## Output Deliverables

Provide users with:

1. **Capabilities overview document** - Summary of what the connector can do
2. **Authentication guide** - Step-by-step setup instructions
3. **Example demonstrations** - Real operations with results
4. **Troubleshooting guide** - Common issues and solutions
5. **Complete reference** - Comprehensive documentation combining all above

Save all documentation as Markdown files and deliver as attachments.

## Common MCP Connector Patterns

**Project/Resource Management:**
- List projects/resources
- Get details about specific items
- Create new projects/resources
- Update configurations
- Delete/archive items

**Data Operations:**
- Query/search data
- Execute operations (SQL, API calls)
- Import/export data
- Transform data

**Monitoring & Logs:**
- Get logs or events
- Check status/health
- Get metrics or analytics

**Configuration:**
- List settings
- Update configurations
- Manage credentials/keys

**Development Tools:**
- Deploy code/functions
- Run tests
- Generate types/schemas
- Manage versions

Identify which patterns apply to the connector being tested and organize documentation accordingly.
