---
name: "organize-github-repos"
description: "Specialized skill for organize github repos workflows and automation."
---

# Organize GitHub Repos

## Overview

This skill provides comprehensive tools for verifying and maintaining alignment between Supabase (Maverick Town) databases and connected GitHub repositories. It prevents data loss by detecting miscommunications, validating synchronization states, and providing auto-healing capabilities when discrepancies are found.

## When to Use This Skill

Use this skill when:
- **Auditing repository states** - Verify that GitHub repos match Supabase records
- **Detecting misalignments** - Find discrepancies between Supabase and GitHub
- **Preventing data loss** - Ensure synchronization before critical operations
- **Recovering from errors** - Identify and fix broken connections
- **Onboarding new repos** - Validate proper setup of new GitHub repositories
- **Troubleshooting sync issues** - Debug why data isn't flowing correctly

## Core Capabilities

### 1. Repository State Verification

**Purpose**: Compare Supabase records with actual GitHub repository states

**Process**:
1. Query Supabase for all registered repositories
2. Use GitHub MCP to fetch actual repository data
3. Compare metadata (name, URL, visibility, default branch, etc.)
4. Generate discrepancy report

**MCP Tools Used**:
- `supabase` MCP: Query repository tables
- `github` MCP (via `gh` CLI): Fetch repository details

**Example Command**:
```bash
manus-mcp-cli tool call supabase_query --server supabase --input '{
  "query": "SELECT * FROM repositories WHERE active = true"
}'
```

### 2. Data Integrity Checks

**Purpose**: Ensure critical data fields are populated and valid

**Checks**:
- Repository URLs are accessible
- Webhook configurations are present
- API tokens are valid and not expired
- Database foreign keys are intact
- Timestamps are reasonable (not in future, not too old)

**Auto-Healing Actions**:
- Refresh expired tokens
- Recreate missing webhooks
- Update stale metadata
- Fix broken foreign key relationships

### 3. RAG-Based Historical Analysis

**Purpose**: Store and query historical repository states to detect patterns

**Implementation**:
- Store snapshots of repository states in vector database
- Query historical data to find when misalignments occurred
- Identify recurring issues or patterns
- Provide context-aware recommendations

**Storage Location**: `/home/ubuntu/skills/organize-github-repos/rag-data/`

**Example Queries**:
- "When did repo X last sync successfully?"
- "What repos have had sync failures in the past week?"
- "Show me all repos that were deleted from GitHub but still in Supabase"

### 4. Alignment Report Generation

**Purpose**: Create comprehensive reports of current alignment status

**Report Sections**:
1. **Executive Summary** - Overall health score, critical issues
2. **Repository Inventory** - All repos in Supabase vs GitHub
3. **Discrepancies** - Detailed list of misalignments
4. **Recommendations** - Prioritized action items
5. **Historical Trends** - Changes over time

**Output Formats**:
- Markdown (human-readable)
- JSON (machine-readable)
- CSV (for spreadsheet analysis)

## Workflow

### Quick Start: Full Audit

```bash
# 1. Fetch all repositories from Supabase
manus-mcp-cli tool call supabase_query --server supabase --input '{
  "query": "SELECT id, name, github_url, last_sync FROM repositories"
}'

# 2. For each repo, verify GitHub state
gh repo view <owner>/<repo> --json name,url,visibility,defaultBranchRef

# 3. Compare and generate report
python3 /home/ubuntu/skills/organize-github-repos/scripts/verify_alignment.py

# 4. Review discrepancies
cat /tmp/alignment-report.md
```

### Workflow Decision Tree

**Start Here**: What do you need to do?

1. **"I want to verify everything is aligned"**
   → Run Full Audit (see Quick Start above)

2. **"I suspect a specific repo is out of sync"**
   → Run Single Repository Check:
   ```bash
   python3 scripts/check_single_repo.py <repo-name>
   ```

3. **"I need to find all broken connections"**
   → Run Connection Health Check:
   ```bash
   python3 scripts/health_check.py --mode=connections
   ```

4. **"I want to see historical sync patterns"**
   → Query RAG Database:
   ```bash
   python3 scripts/query_history.py "show sync failures last 7 days"
   ```

5. **"I need to fix misalignments automatically"**
   → Run Auto-Heal:
   ```bash
   python3 scripts/auto_heal.py --dry-run  # Preview changes
   python3 scripts/auto_heal.py --execute  # Apply fixes
   ```

## Scripts

### scripts/verify_alignment.py
**Purpose**: Main verification script that compares Supabase and GitHub states

**Usage**:
```bash
python3 scripts/verify_alignment.py [--output-format=markdown|json|csv]
```

**What it does**:
1. Queries Supabase for all repositories
2. Fetches corresponding GitHub data via MCP
3. Compares fields and identifies discrepancies
4. Generates alignment report

### scripts/check_single_repo.py
**Purpose**: Focused check on a single repository

**Usage**:
```bash
python3 scripts/check_single_repo.py <repo-name> [--fix]
```

**What it does**:
1. Looks up repo in Supabase
2. Fetches GitHub state
3. Shows detailed comparison
4. Optionally applies fixes if `--fix` flag is used

### scripts/health_check.py
**Purpose**: System-wide health check for connections and integrations

**Usage**:
```bash
python3 scripts/health_check.py [--mode=all|connections|webhooks|tokens]
```

**What it does**:
1. Tests Supabase connection
2. Validates GitHub MCP availability
3. Checks webhook endpoints
4. Verifies API token validity

### scripts/query_history.py
**Purpose**: Query RAG database for historical patterns

**Usage**:
```bash
python3 scripts/query_history.py "<natural language query>"
```

**Examples**:
```bash
python3 scripts/query_history.py "repos with sync failures last week"
python3 scripts/query_history.py "when did repo X last update"
python3 scripts/query_history.py "show all deleted repos"
```

### scripts/auto_heal.py
**Purpose**: Automatically fix detected misalignments

**Usage**:
```bash
python3 scripts/auto_heal.py [--dry-run] [--execute] [--repo=<name>]
```

**What it does**:
1. Runs verification to find issues
2. Applies fixes based on predefined rules
3. Logs all changes for audit trail
4. Supports dry-run mode for safety

**Auto-Healing Rules**:
- Update stale metadata from GitHub
- Recreate missing webhooks
- Refresh expired tokens (if refresh token available)
- Remove Supabase entries for deleted GitHub repos (with confirmation)
- Fix broken foreign key relationships

## References

### references/supabase_schema.md
Documentation of the Maverick Town Supabase schema, including:
- `repositories` table structure
- `sync_logs` table structure
- Foreign key relationships
- Expected data types and constraints

### references/github_api_reference.md
GitHub API endpoints and MCP tool mappings:
- Repository metadata endpoints
- Webhook management
- Authentication patterns
- Rate limiting considerations

### references/common_issues.md
Catalog of known misalignment patterns and solutions:
- Webhook delivery failures
- Token expiration issues
- Repository rename handling
- Organization transfer scenarios

## RAG Data Storage

**Location**: `/home/ubuntu/skills/organize-github-repos/rag-data/`

**Structure**:
```
rag-data/
├── snapshots/           # Historical repository state snapshots
│   └── YYYY-MM-DD/
│       └── repo-name.json
├── discrepancies/       # Logged misalignments
│   └── YYYY-MM-DD.jsonl
└── resolutions/         # Applied fixes and outcomes
    └── YYYY-MM-DD.jsonl
```

**Snapshot Format**:
```json
{
  "timestamp": "2026-02-10T12:00:00Z",
  "repo_name": "example-repo",
  "supabase_state": { ... },
  "github_state": { ... },
  "discrepancies": [ ... ]
}
```

## Best Practices

1. **Run audits regularly** - Schedule weekly full audits to catch drift early
2. **Use dry-run first** - Always preview auto-heal changes before executing
3. **Review discrepancy reports** - Don't blindly auto-fix; understand root causes
4. **Monitor RAG data growth** - Archive old snapshots to prevent storage bloat
5. **Validate after fixes** - Re-run verification after auto-healing to confirm success
6. **Document manual interventions** - Log any manual fixes in `resolutions/` for future reference

## Troubleshooting

**"MCP connection failed"**
- Verify Supabase MCP server is configured: `manus-mcp-cli tool list --server supabase`
- Check GitHub CLI is authenticated: `gh auth status`

**"No discrepancies found but I know there are issues"**
- Check if verification script has correct field mappings
- Review Supabase schema in `references/supabase_schema.md`
- Ensure GitHub MCP is returning complete data

**"Auto-heal made incorrect changes"**
- Review `rag-data/resolutions/` to see what was changed
- Restore from Supabase backup if needed
- Adjust auto-healing rules in `scripts/auto_heal.py`

**"RAG queries returning no results"**
- Verify snapshots are being created: `ls rag-data/snapshots/`
- Check snapshot format matches expected structure
- Ensure query syntax is correct (see examples above)

## Future Enhancements

- **Real-time monitoring** - Webhook-based live sync status
- **Predictive alerts** - ML-based detection of potential issues before they occur
- **Multi-org support** - Handle multiple GitHub organizations
- **Slack notifications** - Alert on critical misalignments
- **Web dashboard** - Visual interface for alignment status
