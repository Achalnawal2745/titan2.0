#!/usr/bin/env python3
"""
Single Repository Alignment Check

Focused verification of a single repository with detailed output
and optional auto-fix capability.
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, Optional

def run_mcp_command(tool_name: str, server: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP CLI command and return parsed JSON result"""
    cmd = [
        "manus-mcp-cli", "tool", "call", tool_name,
        "--server", server,
        "--input", json.dumps(input_data)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running MCP command: {e.stderr}", file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing MCP response: {e}", file=sys.stderr)
        return {}

def fetch_repo_from_supabase(repo_name: str) -> Optional[Dict[str, Any]]:
    """Fetch specific repository from Supabase"""
    query = f"SELECT * FROM repositories WHERE name = '{repo_name}' LIMIT 1"
    
    result = run_mcp_command(
        tool_name="execute_sql",
        server="supabase",
        input_data={"sql": query}
    )
    
    repos = result.get("data", [])
    return repos[0] if repos else None

def fetch_github_repo_state(owner: str, repo_name: str) -> Optional[Dict[str, Any]]:
    """Fetch repository state from GitHub via gh CLI"""
    cmd = [
        "gh", "repo", "view", f"{owner}/{repo_name}",
        "--json", "name,url,visibility,defaultBranchRef,isArchived,isPrivate,description,updatedAt"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        return None
    except json.JSONDecodeError:
        return None

def compare_detailed(supabase_repo: Dict[str, Any], github_repo: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Detailed comparison with field-by-field analysis"""
    comparison = {
        "exists_on_github": github_repo is not None,
        "field_comparisons": {},
        "discrepancies": [],
        "recommendations": []
    }
    
    if github_repo is None:
        comparison["discrepancies"].append("Repository not found on GitHub")
        comparison["recommendations"].append("Remove from Supabase or verify repository name/owner")
        return comparison
    
    # Compare each field
    fields_to_compare = [
        ("visibility", lambda s, g: s.get("visibility", "").lower(), lambda g: "private" if g.get("isPrivate") else "public"),
        ("default_branch", lambda s, g: s.get("default_branch", ""), lambda g: g.get("defaultBranchRef", {}).get("name", "")),
        ("description", lambda s, g: s.get("description", ""), lambda g: g.get("description", "")),
    ]
    
    for field_name, supabase_extractor, github_extractor in fields_to_compare:
        supabase_value = supabase_extractor(supabase_repo, github_repo)
        github_value = github_extractor(github_repo)
        
        matches = supabase_value == github_value
        comparison["field_comparisons"][field_name] = {
            "supabase": supabase_value,
            "github": github_value,
            "matches": matches
        }
        
        if not matches and supabase_value and github_value:
            comparison["discrepancies"].append(f"{field_name}: Supabase='{supabase_value}' vs GitHub='{github_value}'")
            comparison["recommendations"].append(f"Update Supabase {field_name} to '{github_value}'")
    
    # Check if archived
    if github_repo.get("isArchived"):
        comparison["discrepancies"].append("Repository is archived on GitHub")
        comparison["recommendations"].append("Mark as inactive in Supabase or remove")
    
    return comparison

def apply_fixes(repo_name: str, comparison: Dict[str, Any]) -> bool:
    """Apply automatic fixes based on comparison results"""
    if not comparison["exists_on_github"]:
        print("⚠️  Cannot fix: Repository doesn't exist on GitHub")
        return False
    
    updates = []
    for field, data in comparison["field_comparisons"].items():
        if not data["matches"] and data["github"]:
            updates.append(f"{field} = '{data['github']}'")
    
    if not updates:
        print("✅ No fixes needed")
        return True
    
    # Build UPDATE query
    update_query = f"UPDATE repositories SET {', '.join(updates)} WHERE name = '{repo_name}'"
    
    print(f"📝 Applying fixes: {update_query}")
    
    result = run_mcp_command(
        tool_name="execute_sql",
        server="supabase",
        input_data={"sql": update_query}
    )
    
    if result:
        print("✅ Fixes applied successfully")
        return True
    else:
        print("❌ Failed to apply fixes")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_single_repo.py <repo-name> [--fix]")
        sys.exit(1)
    
    repo_name = sys.argv[1]
    should_fix = "--fix" in sys.argv
    
    print(f"🔍 Checking repository: {repo_name}")
    print("=" * 60)
    
    # Fetch from Supabase
    print("\n📊 Fetching from Supabase...")
    supabase_repo = fetch_repo_from_supabase(repo_name)
    
    if not supabase_repo:
        print(f"❌ Repository '{repo_name}' not found in Supabase")
        sys.exit(1)
    
    owner = supabase_repo.get("owner")
    print(f"✅ Found in Supabase: {owner}/{repo_name}")
    
    # Fetch from GitHub
    print(f"\n🐙 Fetching from GitHub...")
    github_repo = fetch_github_repo_state(owner, repo_name)
    
    if github_repo:
        print(f"✅ Found on GitHub: {github_repo.get('url')}")
    else:
        print(f"❌ Not found on GitHub")
    
    # Compare
    print(f"\n🔎 Comparing states...")
    comparison = compare_detailed(supabase_repo, github_repo)
    
    # Display results
    print("\n" + "=" * 60)
    print("📋 COMPARISON RESULTS")
    print("=" * 60)
    
    if comparison["exists_on_github"]:
        print("\n✅ Repository exists on GitHub")
        
        print("\n📊 Field-by-Field Comparison:")
        for field, data in comparison["field_comparisons"].items():
            status = "✅" if data["matches"] else "⚠️ "
            print(f"\n  {status} {field.upper()}:")
            print(f"     Supabase: {data['supabase']}")
            print(f"     GitHub:   {data['github']}")
    else:
        print("\n❌ Repository does NOT exist on GitHub")
    
    if comparison["discrepancies"]:
        print(f"\n⚠️  DISCREPANCIES FOUND ({len(comparison['discrepancies'])}):")
        for i, disc in enumerate(comparison["discrepancies"], 1):
            print(f"  {i}. {disc}")
    else:
        print("\n✅ No discrepancies found - perfect alignment!")
    
    if comparison["recommendations"]:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(comparison["recommendations"], 1):
            print(f"  {i}. {rec}")
    
    # Apply fixes if requested
    if should_fix and comparison["discrepancies"]:
        print("\n" + "=" * 60)
        print("🔧 APPLYING FIXES")
        print("=" * 60)
        apply_fixes(repo_name, comparison)
    elif should_fix:
        print("\n✅ No fixes needed")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
