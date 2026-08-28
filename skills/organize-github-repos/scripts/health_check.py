#!/usr/bin/env python3
"""
System Health Check

Verifies that all required connections and integrations are working properly.
"""

import json
import subprocess
import sys
from typing import Dict, List, Tuple

def check_supabase_connection() -> Tuple[bool, str]:
    """Test Supabase MCP connection"""
    try:
        cmd = ["manus-mcp-cli", "tool", "list", "--server", "supabase"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        
        if "execute_sql" in result.stdout or "list_tables" in result.stdout:
            return True, "Supabase MCP connected and tools available"
        else:
            return False, "Supabase MCP connected but tools not found"
    except subprocess.TimeoutExpired:
        return False, "Supabase MCP connection timeout"
    except subprocess.CalledProcessError as e:
        return False, f"Supabase MCP error: {e.stderr}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def check_github_cli() -> Tuple[bool, str]:
    """Test GitHub CLI authentication"""
    try:
        cmd = ["gh", "auth", "status"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if "Logged in to github.com" in result.stderr or "Logged in to github.com" in result.stdout:
            return True, "GitHub CLI authenticated"
        else:
            return False, "GitHub CLI not authenticated"
    except subprocess.TimeoutExpired:
        return False, "GitHub CLI timeout"
    except FileNotFoundError:
        return False, "GitHub CLI not installed"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def check_github_mcp() -> Tuple[bool, str]:
    """Test GitHub MCP connection (if configured)"""
    try:
        cmd = ["manus-mcp-cli", "tool", "list", "--server", "github"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            return True, "GitHub MCP connected (optional)"
        else:
            return True, "GitHub MCP not configured (using gh CLI instead)"
    except Exception:
        return True, "GitHub MCP not configured (using gh CLI instead)"

def test_supabase_query() -> Tuple[bool, str]:
    """Test actual Supabase query execution"""
    try:
        cmd = [
            "manus-mcp-cli", "tool", "call", "execute_sql",
            "--server", "supabase",
            "--input", json.dumps({"sql": "SELECT 1 as test"})
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=15)
        
        return True, "Supabase query execution successful"
    except subprocess.TimeoutExpired:
        return False, "Supabase query timeout"
    except subprocess.CalledProcessError as e:
        return False, f"Supabase query failed: {e.stderr}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def test_github_api_rate_limit() -> Tuple[bool, str]:
    """Check GitHub API rate limit status"""
    try:
        cmd = ["gh", "api", "rate_limit"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        
        data = json.loads(result.stdout)
        core = data.get("resources", {}).get("core", {})
        remaining = core.get("remaining", 0)
        limit = core.get("limit", 0)
        
        if remaining > 100:
            return True, f"GitHub API rate limit OK ({remaining}/{limit} remaining)"
        elif remaining > 0:
            return True, f"GitHub API rate limit low ({remaining}/{limit} remaining)"
        else:
            return False, f"GitHub API rate limit exhausted (0/{limit} remaining)"
    except Exception as e:
        return False, f"Could not check rate limit: {str(e)}"

def run_health_check(mode: str = "all") -> Dict[str, Tuple[bool, str]]:
    """Run health checks based on mode"""
    checks = {}
    
    if mode in ["all", "connections"]:
        print("🔌 Checking Connections...")
        checks["supabase_connection"] = check_supabase_connection()
        checks["github_cli"] = check_github_cli()
        checks["github_mcp"] = check_github_mcp()
    
    if mode in ["all", "queries"]:
        print("\n🔍 Testing Query Execution...")
        checks["supabase_query"] = test_supabase_query()
        checks["github_rate_limit"] = test_github_api_rate_limit()
    
    return checks

def print_results(checks: Dict[str, Tuple[bool, str]]):
    """Print health check results"""
    print("\n" + "=" * 60)
    print("📊 HEALTH CHECK RESULTS")
    print("=" * 60 + "\n")
    
    passed = 0
    failed = 0
    
    for check_name, (success, message) in checks.items():
        status = "✅" if success else "❌"
        print(f"{status} {check_name.replace('_', ' ').title()}")
        print(f"   {message}\n")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"📈 Summary: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

def main():
    mode = "all"
    if len(sys.argv) > 1 and sys.argv[1].startswith("--mode="):
        mode = sys.argv[1].split("=")[1]
    
    if mode not in ["all", "connections", "queries"]:
        print("Usage: python3 health_check.py [--mode=all|connections|queries]")
        sys.exit(1)
    
    print("🏥 System Health Check")
    print("=" * 60)
    print(f"Mode: {mode}\n")
    
    checks = run_health_check(mode)
    all_passed = print_results(checks)
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
