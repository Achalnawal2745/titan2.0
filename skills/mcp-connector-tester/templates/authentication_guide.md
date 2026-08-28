# How to Connect the [Connector Name] MCP Connector

## Step 1: Generate Credentials

The [Connector Name] MCP connector requires **[credential type]** to authenticate with the [service name].

### To generate credentials:

1. Go to **[Service Dashboard]**: [URL]
2. Navigate to **[Section]** → **[Subsection]**
3. Click **[Button Name]**
4. [Additional steps as needed]
5. **Copy the credential immediately** - it will only be shown once!

The credential format should look like: `[format example]`

## Step 2: Configure the MCP Connector in Manus

### Option A: Through Manus UI (Recommended)

1. Open **Manus** application
2. Go to **Settings** or **Preferences**
3. Find **MCP Servers** or **Integrations** section
4. Locate **[Connector Name]** in the list of available connectors
5. Click **Configure** or **Settings** button
6. Paste your **[credential name]** in the designated field
7. Click **Save** or **Apply**
8. **Restart Manus** to ensure the configuration takes effect

### Option B: Through Environment Variable (Alternative)

If the UI method doesn't work, you can set it as an environment variable:

```bash
export [ENV_VAR_NAME]="your-credential-here"
```

Add this to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) to make it permanent.

## Step 3: Verify the Connection

After configuration, verify the connection is working:

1. Open a new task in Manus
2. Ask me to run: `manus-mcp-cli tool call [simple_tool] --server [server_name] --input '{}'`
3. You should see [expected result]

If you see an error, the credential may be:
- Not properly saved in the configuration
- Expired or invalid
- Not yet loaded (try restarting Manus again)

## Step 4: Test Basic Operations

Once connected, you can test these operations:

### [Operation 1]:
```bash
manus-mcp-cli tool call [tool_name] --server [server_name] --input '{}'
```

### [Operation 2] (replace [PARAMETER]):
```bash
manus-mcp-cli tool call [tool_name] --server [server_name] --input '{"param":"value"}'
```

## Troubleshooting

### "[Error Message]" Error
- **Verify credential is correct**: Copy it again from [service] dashboard
- **Check credential hasn't expired**: Generate a new one if needed
- **Restart Manus completely**: Close and reopen the application
- **Check environment variables**: Ensure `[ENV_VAR_NAME]` is set if using that method

### "[Another Error]" Error
- [Cause and solution]

### MCP Server Not Found
- Ensure the [Connector Name] MCP connector is installed in Manus
- Check that the server name is exactly "[server_name]" (lowercase)
- Verify MCP integration is enabled in Manus settings

### Connection Timeout
- Check your internet connection
- Verify [service] API is accessible: [test URL]
- Check if there's a firewall blocking the connection

## Important Notes

### Credential Types - Don't Confuse Them!

[Service Name] has multiple types of credentials:

1. **[Credential Type 1]** ✅ **USE THIS FOR MCP**
   - Format: `[format]`
   - Used for: [purpose]
   - Found in: [location]
   - Purpose: [what it enables]

2. **[Credential Type 2]** ❌ **NOT FOR MCP**
   - Format: `[format]`
   - Used for: [purpose]
   - Found in: [location]
   - Purpose: [what it enables]

**The MCP connector needs [Credential Type 1], not [other types]!**

## Security Best Practices

1. **Never share your credentials** - they have access to your [service] account
2. **Rotate credentials regularly** - generate new ones periodically
3. **Use descriptive names** - helps you identify credentials later
4. **Revoke unused credentials** - remove credentials you're no longer using
5. **Don't commit credentials to git** - keep them out of version control
6. **Use environment variables** - for additional security in production

## What You Can Do Once Connected

Once the connector is properly configured, you can:

- ✅ [Capability 1]
- ✅ [Capability 2]
- ✅ [Capability 3]
- ✅ [Capability 4]
- ✅ [Capability 5]

All through natural language commands to Manus!
