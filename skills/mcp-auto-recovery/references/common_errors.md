# MCP Common Error Patterns

This document lists common error messages from `manus-mcp-cli` and their likely causes and solutions.

## Connection and Server Errors

### Error: `Server '<name>' not found`

**Cause:** The server name provided with `--server` is incorrect or not configured for this session.

**Solution:** Run `manus-mcp-cli server list` to see all available servers. Correct the spelling in your command.

### Error: `Connection refused` or `Timeout`

**Cause:** The MCP server is not responding, possibly due to network issues or the server being down.

**Solution:** 
1. Check your internet connection
2. Wait a few moments and retry
3. Verify the server is operational (check status page if available)

## Authentication Errors

### Error: `OAuth flow failed` or `401 Unauthorized`

**Cause:** Your authentication token for the MCP server has expired or is invalid.

**Solution:** The system should automatically trigger a new OAuth flow. Follow the prompts in the user interface to re-authorize the connection. This cannot be done programmatically.

### Error: `403 Forbidden`

**Cause:** You are authenticated, but do not have permission to perform the requested action.

**Solution:** 
1. Verify you have the necessary permissions in the service (e.g., Supabase project access)
2. Check if your API key or token has the required scopes
3. Contact the service administrator to grant appropriate permissions

## Tool and Command Errors

### Error: `Tool '<tool_name>' not found on server '<server_name>'`

**Cause:** The tool name you are trying to call does not exist on the specified server.

**Solution:** Run `manus-mcp-cli tool list --server <server_name>` to see all available tools. Check for typos in the tool name.

### Error: `Invalid input: JSON parsing failed`

**Cause:** The string provided to the `--input` flag is not valid JSON. This is often due to unescaped quotes or trailing commas.

**Solution:** 
1. Carefully validate your JSON string
2. Use an online JSON validator if necessary
3. Ensure all string values are enclosed in double quotes
4. Remove any trailing commas after the last element in an object or array
5. Escape special characters properly in shell commands

**Example of correct JSON:**
```bash
--input '{"key": "value", "number": 123, "array": [1, 2, 3]}'
```

## Supabase-Specific Errors

### Error: `role "anon" is not permitted to access table "<table_name>"`

**Cause:** The API key being used (often the `anon` key) does not have the required Row Level Security (RLS) permissions to access the specified table.

**Solution:**
1. Go to the Supabase dashboard
2. Navigate to `Authentication` → `Policies`
3. Find the table in question and ensure a policy exists that allows the `anon` role to perform the desired action (SELECT, INSERT, UPDATE, DELETE)
4. If no policy exists, create one. Be specific about what is allowed

### Error: `error: invalid input syntax for type uuid: "<value>"`

**Cause:** You are passing a non-UUID value to a column that expects a UUID.

**Solution:** Ensure the ID you are providing is a valid UUID string (e.g., `a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11`). Do not pass names or other identifiers to UUID columns.

### Error: `relation "<table_name>" does not exist`

**Cause:** The table you are trying to query does not exist in the database, or you are querying the wrong schema.

**Solution:**
1. Verify the table name is spelled correctly
2. Check that you are connected to the correct Supabase project
3. Ensure the table exists in the `public` schema (or specify the correct schema)

## Airtable-Specific Errors

### Error: `INVALID_PERMISSIONS_OR_MODEL_NOT_FOUND`

**Cause:** Either the `baseId` or `tableId` is incorrect, or the API token does not have permission to access the resource.

**Solution:**
1. Call `list_bases` to verify the correct `baseId`
2. Call `list_tables` with the correct `baseId` to verify the `tableId`
3. Ensure your Airtable API token has access to the base
4. Check that the base is not in a restricted workspace

## General Troubleshooting Tips

1. **Always check spelling** - Server names, tool names, and parameters are case-sensitive
2. **Validate JSON carefully** - Use a JSON validator before passing complex input
3. **Check permissions** - Many errors are due to insufficient access rights
4. **Read error messages fully** - The error often contains specific details about what went wrong
5. **Use the diagnostic script** - Run `/home/ubuntu/skills/mcp-auto-recovery/scripts/diagnose_mcp.py` for systematic troubleshooting
