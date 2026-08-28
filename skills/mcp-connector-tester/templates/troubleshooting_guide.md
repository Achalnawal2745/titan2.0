# [Connector Name] MCP Connector - Troubleshooting Guide

## Common Issues and Solutions

### Authentication Errors

#### "Unauthorized" Error

**Symptoms**: Connection fails with "Unauthorized" message when trying to use any tool.

**Causes**:
- Credentials not configured in Manus
- Credentials expired or invalid
- Wrong credential type used
- Configuration not loaded after setup

**Solutions**:
1. Verify you're using the correct credential type ([credential type])
2. Check that the credential hasn't expired in the [service] dashboard
3. Ensure the credential is properly configured in Manus settings
4. Try restarting Manus completely after configuration
5. Generate a fresh credential if the issue persists

**Verification**:
```bash
manus-mcp-cli auth status --server [server_name]
```

---

#### "[Specific Error Message]" Error

**Symptoms**: [Description of what the user sees]

**Causes**:
- [Cause 1]
- [Cause 2]

**Solutions**:
1. [Step-by-step solution]
2. [Alternative approach]

---

### Connection Issues

#### Connection Timeout

**Symptoms**: Operations hang or timeout without completing.

**Causes**:
- Network connectivity issues
- Firewall blocking API access
- Service outage or maintenance
- Rate limiting

**Solutions**:
1. Check your internet connection
2. Verify [service] API is accessible by visiting [test URL] in a browser
3. Check if your organization's network blocks API access
4. Try using a different network to isolate the issue
5. Check [service] status page for outages: [status URL]

---

#### MCP Server Not Responding

**Symptoms**: Commands fail immediately or server appears offline.

**Causes**:
- MCP server not installed or enabled
- Server crashed or needs restart
- Configuration file corrupted

**Solutions**:
1. Verify the [Connector Name] MCP server is installed and enabled in Manus
2. Check server status: `manus-mcp-cli server check --server [server_name]`
3. Restart Manus to reinitialize the MCP server
4. Check Manus logs for any error messages about the MCP server

---

### Data and Operation Issues

#### Empty or Unexpected Results

**Symptoms**: Queries return no data or unexpected data.

**Causes**:
- Incorrect parameters in the query
- Resource doesn't exist
- Insufficient permissions
- Wrong [project/resource] ID

**Solutions**:
1. Verify you're using the correct [resource] ID in your queries
2. Check that you have the necessary permissions in your [service] account
3. Ensure the resource you're querying actually exists
4. Review the tool's required parameters to ensure you're passing correct values
5. Try listing all [resources] first to verify IDs

---

#### Operation Failed or Rejected

**Symptoms**: Create, update, or delete operations fail with errors.

**Causes**:
- Insufficient permissions
- Resource constraints (quotas, limits)
- Invalid data or parameters
- Dependencies not met

**Solutions**:
1. Check your account permissions and subscription level
2. Verify you haven't exceeded quotas or limits
3. Validate input data matches required format
4. Check for dependencies (e.g., can't delete a resource that's in use)
5. Review the error message for specific guidance

---

### Configuration Issues

#### Credential Type Confusion

**Symptoms**: Using the wrong type of credential for the MCP connector.

**Common Mistake**: Using [wrong credential type] instead of [correct credential type].

**Identification**:
- [Correct credential type] format: `[format example]`
- [Wrong credential type] format: `[format example]`

**Solution**:
1. Go to [location in service dashboard]
2. Generate or copy the correct [credential type]
3. Reconfigure Manus with the correct credential
4. Restart Manus

---

#### Configuration Not Taking Effect

**Symptoms**: After configuring credentials, the connector still shows as unauthorized.

**Causes**:
- Manus not restarted after configuration
- Configuration saved to wrong location
- Environment variable not set correctly

**Solutions**:
1. **Always restart Manus completely** after changing configuration
2. Verify configuration was saved (check Manus settings)
3. If using environment variables, verify they're set: `echo $[ENV_VAR_NAME]`
4. Try configuring through a different method (UI vs environment variable)

---

## Diagnostic Commands

Use these commands to diagnose issues:

### Check Server Status
```bash
manus-mcp-cli server check --server [server_name]
```
Shows if the server is connected and how many tools are available.

### Check Authentication Status
```bash
manus-mcp-cli auth status --server [server_name]
```
Shows authentication method and status.

### List Available Tools
```bash
manus-mcp-cli tool list --server [server_name]
```
Verifies the server is responding and shows available tools.

### Test Simple Operation
```bash
manus-mcp-cli tool call [simple_tool] --server [server_name] --input '{}'
```
Tests basic connectivity with a simple, safe operation.

---

## Getting Help

If you've tried the solutions above and still have issues:

1. **Check [service] status**: [status page URL]
2. **Review [service] documentation**: [docs URL]
3. **Check Manus logs**: Look for error messages in the Manus application
4. **Contact support**: [support URL or email]

When reporting issues, include:
- The exact error message
- The command you were trying to run
- Your [service] account type/plan
- Whether authentication was successful
- Any relevant logs or screenshots

---

## Prevention Tips

### Avoid Common Mistakes

1. **Always use the correct credential type** - [correct type] for MCP, not [wrong type]
2. **Restart Manus after configuration** - Changes don't take effect until restart
3. **Keep credentials secure** - Don't commit to git or share publicly
4. **Monitor credential expiration** - Set reminders to rotate before expiry
5. **Test after setup** - Always verify connection with a simple operation

### Maintain Healthy Configuration

1. **Regular credential rotation** - Update credentials every [time period]
2. **Clean up unused credentials** - Remove old credentials from [service] dashboard
3. **Document your setup** - Note which credentials are used where
4. **Monitor usage** - Check [service] dashboard for unexpected activity
5. **Keep Manus updated** - Update to latest version for bug fixes

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| "Unauthorized" | Verify credentials, restart Manus |
| Connection timeout | Check network, verify API accessible |
| Wrong credential type | Use [correct type], not [wrong type] |
| Empty results | Verify resource ID and permissions |
| Server not responding | Check server status, restart Manus |
| Config not working | Restart Manus after any config change |

---

## Still Having Issues?

If this guide doesn't solve your problem:

1. Try the diagnostic commands above to gather more information
2. Check if the issue is specific to one tool or affects all operations
3. Test with a different [resource] to isolate the problem
4. Review recent changes to your [service] account or Manus configuration
5. Ask me to help troubleshoot - I can run diagnostic commands and analyze results
