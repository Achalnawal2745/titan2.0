---
name: mcp-auto-recovery
description: "Automatically diagnose and recover from MCP server connection issues. Use when any `manus-mcp-cli` command fails due to connection, authentication, or availability errors."
---

# MCP Auto-Recovery

This skill provides a systematic workflow to diagnose and resolve common issues when interacting with Model Context Protocol (MCP) servers via the `manus-mcp-cli` tool.

## When to Use This Skill

**Trigger this skill immediately if a `manus-mcp-cli` command fails with errors related to:**
- Connection refused / timeout
- Server not found
- Authentication required / token expired
- Permission denied
- Any unexpected non-zero exit code

## The Workflow

Follow these steps sequentially. Do not skip steps.

### Step 1: Identify the Failing Server

From the failed command, identify the server name specified with the `--server` flag. For example, in `manus-mcp-cli tool list --server supabase`, the server name is `supabase`.

### Step 2: Run the Diagnostic Script

Execute the bundled diagnostic script, passing the server name as an argument. This script will perform a series of automated checks and provide a summary report with recommended actions.

**Command:**
```bash
python3 /home/ubuntu/skills/mcp-auto-recovery/scripts/diagnose_mcp.py <server_name>
```

**Example:**
```bash
python3 /home/ubuntu/skills/mcp-auto-recovery/scripts/diagnose_mcp.py supabase
```

### Step 3: Interpret the Diagnostic Report

The script will output a clear summary. Follow its recommendation:

| Report Outcome | Recommended Action |
|----------------|-------------------|
| **Server Not Available** | Check the server name for typos against the list of available servers provided. Retry the command with the correct name. |
| **Authentication Failed** | Follow the interactive OAuth prompts if they appear. The script cannot do this for you. After authenticating, retry the original command. |
| **All Checks Pass** | The issue is not with the connection. The problem lies with the specific tool call itself. Carefully review the tool's required parameters, your input JSON, and any necessary permissions (e.g., does the user have access to the requested resource?). |

### Step 4: Retry the Original Command

After following the recommendation from the diagnostic report, retry the original `manus-mcp-cli` command that failed. If it still fails, do not run the diagnostic script again. Instead, inform the user about the persistent failure and the steps you've already taken.

### Advanced: Common Error Patterns

If the issue persists, consult the reference file for common error messages and their solutions.

**Command:**
```bash
cat /home/ubuntu/skills/mcp-auto-recovery/references/common_errors.md
```

## Example Usage

### Scenario: Supabase Connection Fails

**Failed Command:**
```bash
manus-mcp-cli tool call execute_sql --server supabase --input '{"query": "SELECT * FROM users"}'
```

**Error:**
```
Error: failed to get server config: server 'supabase' not found
```

**Recovery Steps:**

1. **Identify server:** `supabase`

2. **Run diagnostic:**
```bash
python3 /home/ubuntu/skills/mcp-auto-recovery/scripts/diagnose_mcp.py supabase
```

3. **Read report:** Script shows server is not available and lists all configured servers

4. **Take action:** Check spelling, verify MCP is enabled in session settings

5. **Retry:** Run the original command again

## Notes

- The diagnostic script is **non-destructive** and safe to run multiple times
- It only performs read operations to check server status
- Authentication flows must be completed interactively by the user
- If all diagnostics pass but the command still fails, the issue is with the specific tool call parameters, not the MCP connection
