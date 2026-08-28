#!/usr/bin/env python3
"""
Repository Alignment Verification Script

Compares Supabase repository records with actual GitHub repository states
to detect misalignments and prevent data loss.
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

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

def fetch_supabase_repos() -> List[Dict[str, Any]]:
    """Fetch all repositories from Supabase"""
    print("📊 Fetching repositories from Supabase...")
    
    query = "SELECT id, name, github_url, owner, visibility, default_branch, last_sync, active FROM repositories WHERE active = true"
    
    result = run_mcp_command(
        tool_name="execute_sql",
        server="supabase",
        input_data={"sql": query}
    )
    
    # TODO: Parse actual MCP response format
    # This is a placeholder - adjust based on actual Supabase MCP response structure
    repos = result.get("data", [])
    print(f"✅ Found {len(repos)} repositories in Supabase")
    return repos

def fetch_github_repo_state(owner: str, repo_name: str) -> Optional[Dict[str, Any]]:
    """Fetch repository state from GitHub via gh CLI"""
    cmd = [
        "gh", "repo", "view", f"{owner}/{repo_name}",
        "--json", "name,url,visibility,defaultBranchRef,isArchived,isPrivate"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        return None  # Repo doesn't exist or not accessible
    except json.JSONDecodeError:
        return None

def compare_repos(supabase_repo: Dict[str, Any], github_repo: Optional[Dict[str, Any]]) -> List[str]:
    """Compare Supabase and GitHub repo states, return list of discrepancies"""
    discrepancies = []
    
    if github_repo is None:
        discrepancies.append("Repository not found on GitHub (deleted or inaccessible)")
        return discrepancies
    
    # Compare visibility
    supabase_visibility = supabase_repo.get("visibility", "").lower()
    github_visibility = "private" if github_repo.get("isPrivate") else "public"
    if supabase_visibility != github_visibility:
        discrepancies.append(f"Visibility mismatch: Supabase={supabase_visibility}, GitHub={github_visibility}")
    
    # Compare default branch
    supabase_branch = supabase_repo.get("default_branch", "")
    github_branch = github_repo.get("defaultBranchRef", {}).get("name", "")
    if supabase_branch and github_branch and supabase_branch != github_branch:
        discrepancies.append(f"Default branch mismatch: Supabase={supabase_branch}, GitHub={github_branch}")
    
    # Check if archived
    if github_repo.get("isArchived"):
        discrepancies.append("Repository is archived on GitHub but marked active in Supabase")
    
    return discrepancies

def generate_report(results: List[Dict[str, Any]], output_format: str = "markdown") -> str:
    """Generate alignment report in specified format"""
    if output_format == "markdown":
        return generate_markdown_report(results)
    elif output_format == "json":
        return json.dumps(results, indent=2)
    elif output_format == "csv":
        return generate_csv_report(results)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

def generate_markdown_report(results: List[Dict[str, Any]]) -> str:
    """Generate Markdown format report"""
    timestamp = datetime.now().isoformat()
    total_repos = len(results)
    repos_with_issues = sum(1 for r in results if r["discrepancies"])
    
    lines = [
        "# Repository Alignment Report",
        "",
        f"**Generated**: {timestamp}",
        f"**Total Repositories**: {total_repos}",
        f"**Repositories with Issues**: {repos_with_issues}",
        f"**Health Score**: {((total_repos - repos_with_issues) / total_repos * 100):.1f}%",
        "",
        "---",
        ""
    ]
    
    if repos_with_issues == 0:
        lines.extend([
            "## ✅ All Repositories Aligned",
            "",
            "No discrepancies detected. All Supabase records match GitHub states."
        ])
    else:
        lines.extend([
            "## ⚠️ Discrepancies Detected",
            ""
        ])
        
        for result in results:
            if result["discrepancies"]:
                lines.extend([
                    f"### {result['repo_name']}",
                    "",
                    f"**Owner**: {result['owner']}",
                    f"**Supabase ID**: {result['supabase_id']}",
                    "",
                    "**Issues**:",
                    ""
                ])
                for disc in result["discrepancies"]:
                    lines.append(f"- {disc}")
                lines.append("")
    
    return "\n".join(lines)

def generate_csv_report(results: List[Dict[str, Any]]) -> str:
    """Generate CSV format report"""
    lines = ["repo_name,owner,has_issues,issue_count,issues"]
    
    for result in results:
        issues = "; ".join(result["discrepancies"])
        lines.append(f"{result['repo_name']},{result['owner']},{len(result['discrepancies']) > 0},{len(result['discrepancies'])},\"{issues}\"")
    
    return "\n".join(lines)

def main():
    """Main verification workflow"""
    output_format = sys.argv[1] if len(sys.argv) > 1 else "markdown"
    
    print("🔍 Starting Repository Alignment Verification")
    print("=" * 60)
    
    # Fetch Supabase repositories
    supabase_repos = fetch_supabase_repos()
    
    if not supabase_repos:
        print("❌ No repositories found in Supabase or error fetching data")
        sys.exit(1)
    
    # Verify each repository
    results = []
    for repo in supabase_repos:
        repo_name = repo.get("name")
        owner = repo.get("owner")
        
        print(f"\n🔎 Checking {owner}/{repo_name}...")
        
        github_state = fetch_github_repo_state(owner, repo_name)
        discrepancies = compare_repos(repo, github_state)
        
        results.append({
            "repo_name": repo_name,
            "owner": owner,
            "supabase_id": repo.get("id"),
            "discrepancies": discrepancies
        })
        
        if discrepancies:
            print(f"   ⚠️  Found {len(discrepancies)} issue(s)")
        else:
            print(f"   ✅ Aligned")
    
    # Generate report
    print("\n" + "=" * 60)
    print("📄 Generating report...")
    
    report = generate_report(results, output_format)
    
    # Save report
    output_file = f"/tmp/alignment-report.{output_format if output_format != 'markdown' else 'md'}"
    with open(output_file, "w") as f:
        f.write(report)
    
    print(f"✅ Report saved to: {output_file}")
    print("\n" + report)

if __name__ == "__main__":
    main()
