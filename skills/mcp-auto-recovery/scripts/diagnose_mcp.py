#!/usr/bin/env python3
"""
MCP Server Diagnostic Tool

This script runs a series of checks to diagnose common issues with MCP server connections.
It checks server availability, authentication, and provides actionable recommendations.
"""

import subprocess
import json
import argparse
import sys

def run_command(command):
    """Runs a shell command and returns its output, error, and status code."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def check_server_availability(server_name):
    """Checks if the MCP server is available by listing its tools."""
    print(f"[1/4] Checking server availability for \033[36m{server_name}\033[0m...")
    command = f"manus-mcp-cli tool list --server {server_name}"
    stdout, stderr, code = run_command(command)
    if code == 0 and "Tools available" in stdout:
        print("\t\033[32m✅ Server is available and responsive.\033[0m")
        return True, "Server available."
    else:
        print("\t\033[31m❌ Server not available or not responding.\033[0m")
        return False, stderr.strip() if stderr else "Unknown error"

def check_authentication(server_name):
    """Checks for authentication issues by running a simple read-only command."""
    print(f"[2/4] Checking authentication for \033[36m{server_name}\033[0m...")
    
    # Try a generic list command that should work on most servers
    command = f"manus-mcp-cli tool list --server {server_name}"
    stdout, stderr, code = run_command(command)
    
    if code == 0:
        print("\t\033[32m✅ Authentication successful.\033[0m")
        return True, "Authentication successful."
    elif "OAuth" in stderr or "authentication" in stderr.lower() or "401" in stderr:
        print("\t\033[33m⚠️  Authentication may be required or has expired.\033[0m")
        return False, "Authentication required or expired."
    else:
        print("\t\033[31m❌ Command failed. Could be a permissions or configuration issue.\033[0m")
        return False, stderr.strip() if stderr else "Unknown error"

def check_permissions(server_name):
    """Checks for basic read/write permissions (conceptual)."""
    print(f"[3/4] Checking permissions for \033[36m{server_name}\033[0m...")
    # This is a conceptual check. A real implementation would need a safe write/delete operation.
    # For now, we rely on the auth check.
    print("\t\033[34mℹ️  Permission check is conceptual. Relying on previous checks.\033[0m")
    return True, "Permissions check passed (conceptual)."

def list_available_servers():
    """Lists all configured MCP servers."""
    print(f"[4/4] Listing all available MCP servers...")
    command = "manus-mcp-cli server list 2>&1 || echo 'Server list command not available'"
    stdout, stderr, code = run_command(command)
    
    # Try alternative: list from config or just show a message
    if "not available" in stdout or code != 0:
        # Fallback: try to infer from error messages
        print("\t\033[34mℹ️  Cannot list servers programmatically.\033[0m")
        return False, "Server list command not available. Check session MCP configuration."
    
    print("\t\033[32m✅ Available servers:\033[0m")
    print(stdout)
    return True, stdout

def main():
    parser = argparse.ArgumentParser(description="Diagnose MCP server connection issues.")
    parser.add_argument("server_name", help="The name of the MCP server to diagnose.")
    args = parser.parse_args()

    print(f"\n\033[1mStarting MCP Diagnostics for server: {args.server_name}\033[0m\n")

    report = {}

    # Run checks
    available, msg_avail = check_server_availability(args.server_name)
    report["server_availability"] = {"success": available, "message": msg_avail}

    if available:
        authenticated, msg_auth = check_authentication(args.server_name)
        report["authentication"] = {"success": authenticated, "message": msg_auth}

        if authenticated:
            permissions, msg_perm = check_permissions(args.server_name)
            report["permissions"] = {"success": permissions, "message": msg_perm}
    else:
        # If server is not available, list other servers
        listed, msg_list = list_available_servers()
        report["server_list"] = {"success": listed, "message": msg_list}

    # Generate final summary
    print("\n\033[1m--- Diagnostic Summary ---\033[0m")
    if report.get("server_availability", {}).get("success"):
        print("\033[32m✅ MCP server is available and responding.\033[0m")
        if report.get("authentication", {}).get("success"):
            print("\033[32m✅ Authentication is valid.\033[0m")
            print("\n\033[1mRecommendation:\033[0m The issue is likely not with the MCP connection itself, but with the specific tool call or its parameters. Please double-check the tool name, arguments, and required permissions (e.g., does the user have access to the requested resource?).")
        else:
            print("\033[31m❌ Authentication failed or is required.\033[0m")
            print(f"\tError details: {report['authentication']['message']}")
            print("\n\033[1mRecommendation:\033[0m The MCP server requires authentication. Please follow the interactive prompts to log in. If you are already logged in, your session may have expired. Try running the original command again to trigger re-authentication.")
    else:
        print("\033[31m❌ MCP server is not available.\033[0m")
        print(f"\tError details: {report['server_availability']['message']}")
        if report.get("server_list", {}).get("success"):
            print("\n\033[1mRecommendation:\033[0m Check if the server name is spelled correctly. The following servers are available:")
            print(report['server_list']['message'])
        else:
            print("\n\033[1mRecommendation:\033[0m MCP may not be configured correctly in this session. Please check the session settings or verify that MCP servers are enabled.")

    print("\n\033[1m--- End of Report ---\033[0m\n")
    
    # Return exit code based on success
    if report.get("server_availability", {}).get("success") and report.get("authentication", {}).get("success"):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
