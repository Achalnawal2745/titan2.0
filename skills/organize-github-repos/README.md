# Organize GitHub Repos Skill

**Version**: 1.0.0  
**Status**: ✅ Ready for Use  
**Last Updated**: February 10, 2026

---

## Quick Start

### 1. Run Health Check

Verify all connections are working:

```bash
python3 /home/ubuntu/skills/organize-github-repos/scripts/health_check.py --mode=all
```

Expected output:
```
✅ Supabase Connection - Supabase MCP connected and tools available
✅ Github Cli - GitHub CLI authenticated
✅ Supabase Query - Supabase query execution successful
✅ Github Rate Limit - GitHub API rate limit OK
```

### 2. Verify All Repositories

Run full alignment verification:

```bash
python3 /home/ubuntu/skills/organize-github-repos/scripts/verify_alignment.py
```

Output saved to: `/tmp/alignment-report.md`

### 3. Check Single Repository

Focus on a specific repository:

```bash
python3 /home/ubuntu/skills/organize-github-repos/scripts/check_single_repo.py <repo-name>
```

Add `--fix` flag to automatically apply fixes:

```bash
python3 /home/ubuntu/skills/organize-github-repos/scripts/check_single_repo.py <repo-name> --fix
```

---

## What This Skill Does

This skill verifies and maintains alignment between **Supabase (Maverick Town)** and connected **GitHub repositories** to prevent data loss from miscommunication.

**Core Capabilities**:
1. **Repository State Verification** - Compare Supabase records with GitHub API
2. **Data Integrity Checks** - Ensure critical fields are populated and valid
3. **RAG-Based Historical Analysis** - Store and query historical states
4. **Alignment Report Generation** - Create comprehensive reports

---

## Scripts

### health_check.py

**Purpose**: System health check for connections and integrations

**Usage**:
```bash
python3 scripts/health_check.py [--mode=all|connections|queries]
```

**Modes**:
- `all` - Check everything (default)
- `connections` - Only test MCP and CLI connections
- `queries` - Only test query execution and rate limits

**Exit Codes**:
- `0` - All checks passed
- `1` - One or more checks failed

---

### verify_alignment.py

**Purpose**: Main verification script comparing Supabase and GitHub states

**Usage**:
```bash
python3 scripts/verify_alignment.py [markdown|json|csv]
```

**Output Formats**:
- `markdown` - Human-readable report (default)
- `json` - Machine-readable data
- `csv` - Spreadsheet-friendly format

**Output Location**: `/tmp/alignment-report.{md|json|csv}`

**What It Checks**:
- Repository exists on GitHub
- Visibility matches (public/private)
- Default branch matches
- Repository not archived

---

### check_single_repo.py

**Purpose**: Focused check on a single repository with auto-fix

**Usage**:
```bash
python3 scripts/check_single_repo.py <repo-name> [--fix]
```

**Flags**:
- `--fix` - Automatically apply fixes (updates Supabase)

**Output**: Detailed field-by-field comparison with recommendations

**Example**:
```bash
python3 scripts/check_single_repo.py my-awesome-repo --fix
```

---

## File Structure

```
organize-github-repos/
├── README.md                    # This file
├── SKILL.md                     # Full skill documentation
├── scripts/                     # Executable Python scripts
│   ├── verify_alignment.py      # Main verification (7.5 KB)
│   ├── check_single_repo.py     # Single repo check (7.5 KB)
│   └── health_check.py          # System health (5.6 KB)
├── references/                  # Documentation
│   ├── supabase_schema.md       # Database schema reference
│   └── github_tools_found.md    # Research findings
├── templates/                   # (empty)
└── rag-data/                    # Historical data storage
    ├── snapshots/               # Repository state snapshots
    ├── discrepancies/           # Logged misalignments
    └── resolutions/             # Applied fixes
```

---

## Requirements

### MCP Servers

- **Supabase MCP** - Must be configured and connected
- **GitHub MCP** - Optional (uses `gh` CLI if not available)

### CLI Tools

- **GitHub CLI (`gh`)** - Must be authenticated
- **Python 3.11+** - For running scripts

### Environment

- Manus sandbox with MCP integration enabled
- Access to Supabase project with `repositories` table

---

## Configuration

### Supabase Schema

Expected table structure:

```sql
CREATE TABLE repositories (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,
    github_url TEXT NOT NULL,
    visibility TEXT NOT NULL,
    default_branch TEXT,
    description TEXT,
    last_sync TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    webhook_id TEXT,
    webhook_secret TEXT,
    UNIQUE(owner, name)
);
```

See `references/supabase_schema.md` for full schema documentation.

---

## Troubleshooting

### "Supabase MCP connection failed"

**Solution**:
```bash
manus-mcp-cli tool list --server supabase
```

If this fails, Supabase MCP is not configured. Check Manus MCP settings.

### "GitHub CLI not authenticated"

**Solution**:
```bash
gh auth login
```

Follow prompts to authenticate with GitHub.

### "Repository not found in Supabase"

**Possible causes**:
1. Repository name is incorrect
2. Repository is marked as `active = false`
3. Repository hasn't been added to Supabase yet

**Solution**: Check Supabase database directly:
```sql
SELECT * FROM repositories WHERE name LIKE '%<partial-name>%';
```

### "No discrepancies found but I know there are issues"

**Possible causes**:
1. Field mappings are incorrect
2. Supabase schema differs from expected
3. GitHub MCP returning incomplete data

**Solution**: Review `references/supabase_schema.md` and adjust scripts if needed.

---

## Testing

### Test Health Check

```bash
python3 scripts/health_check.py --mode=all
```

Expected: All checks should pass (5/5)

### Test with Known Repository

1. Pick a repository you know exists in both Supabase and GitHub
2. Run single repo check:
   ```bash
   python3 scripts/check_single_repo.py <repo-name>
   ```
3. Review output for accuracy

### Test Auto-Fix (Dry Run)

1. Intentionally create a mismatch in Supabase (e.g., wrong visibility)
2. Run check without `--fix`:
   ```bash
   python3 scripts/check_single_repo.py <repo-name>
   ```
3. Verify discrepancy is detected
4. Run with `--fix`:
   ```bash
   python3 scripts/check_single_repo.py <repo-name> --fix
   ```
5. Verify fix was applied

---

## Best Practices

1. **Run health check first** - Always verify connections before running verification
2. **Use dry-run mode** - Review discrepancies before applying auto-fixes
3. **Schedule regular audits** - Run weekly full verifications
4. **Monitor rate limits** - GitHub API has 5000 requests/hour limit
5. **Review reports** - Don't blindly trust auto-fix; understand root causes

---

## Known Limitations

1. **MCP response format** - Scripts assume certain response structure (may need adjustment)
2. **SQL injection risk** - Single repo check uses string interpolation (use with trusted input only)
3. **No webhook verification** - Doesn't check if webhooks are actually working
4. **No token refresh** - Can't automatically refresh expired API tokens
5. **Single project only** - Doesn't support multiple Supabase projects

---

## Future Enhancements

- [ ] Implement `query_history.py` for RAG queries
- [ ] Implement `auto_heal.py` with full rule set
- [ ] Add batch processing from file
- [ ] Add verbose mode flag (`-v`)
- [ ] Create snapshot storage logic
- [ ] Real-time monitoring with webhooks
- [ ] Predictive alerts with ML
- [ ] Multi-org support
- [ ] Slack notifications
- [ ] Web dashboard

---

## Credits

**Research**: Used github-gem-seeker skill to find existing solutions  
**Patterns borrowed from**:
- [github-audit-tool](https://github.com/EISMGard/github-audit-tool) - Org-wide scanning
- [GitVerify](https://github.com/kulkansecurity/gitverify) - Output formats

**Built with**: skill-development-workflow, mcp-builder patterns

---

## Support

For issues or questions:
1. Check `SKILL.md` for detailed documentation
2. Review `references/` directory for schema and API info
3. Run health check to diagnose connection issues
4. Check execution log for architectural decisions

---

## Changelog

### v1.0.0 (2026-02-10)
- ✅ Initial release
- ✅ Core verification scripts
- ✅ Health check system
- ✅ Comprehensive documentation
- ✅ RAG data structure defined
