---
name: "project-handoff-ingestion"
description: "Specialized skill for project handoff ingestion workflows and automation."
---

# Project Handoff Ingestion

Systematic process for ingesting projects handed off from other development environments, verifying all components, and creating comprehensive deployment documentation.

## When to Use This Skill

Use this skill when you receive a project handoff and need to:
- Verify access to all project components (code, databases, APIs, deployments)
- Understand the current deployment status vs. documentation claims
- Identify gaps between documented and actual system state
- Create actionable deployment guides
- Document the complete system architecture

## Core Workflow

### Phase 1: Initial Documentation Analysis

Read and analyze all provided handoff documentation:
- Project overview documents
- Deployment guides
- Architecture diagrams
- Environment variable lists
- API documentation

Create an initial assessment document tracking:
- Claimed system status
- Required credentials
- Deployment platforms mentioned
- Known gaps or warnings

### Phase 2: Service Access Verification

Systematically verify access to each mentioned service:

**Live Services (HTTP/HTTPS)**
- Test health endpoints
- Verify API responses
- Check deployment status
- Record response times

**Databases**
- Use Supabase MCP if available
- Verify schema matches documentation
- Check for existing data
- Query table structures

**Source Code Repositories**
- Attempt to clone repositories
- If access denied, document the exact error
- Request collaborator access from user
- Verify repository structure matches documentation

**Deployment Platforms**
- Check Railway/Vercel/Netlify dashboards if accessible
- Verify environment variables
- Review deployment logs
- Check for authentication errors

### Phase 3: Discrepancy Identification

Compare documentation claims against actual findings:

Create a discrepancy table:
| Component | Documentation Claims | Actual Finding | Impact |
|-----------|---------------------|----------------|--------|
| Example | "95% complete" | "60% complete, payment system not deployed" | High |

Common discrepancies to check:
- Completion percentage vs. actual deployment
- Environment variables (claimed missing vs. actually configured)
- API endpoints (documented vs. actually deployed)
- Service integrations (documented vs. functional)

### Phase 4: Code Analysis

Once repository access is obtained:

**Examine Project Structure**
- List all directories and key files
- Identify main application files
- Find configuration files
- Locate deployment scripts

**Analyze Implementation**
- Read main server/application files
- Identify all API endpoints
- Check for payment/authentication logic
- Verify notification service integrations
- Review error handling

**Check Dependencies**
- Read package.json/requirements.txt
- Verify all dependencies are documented
- Check for version mismatches

### Phase 5: Endpoint Testing

Test all documented API endpoints:

```bash
# Health check
curl https://api-url/health

# POST endpoints
curl -X POST https://api-url/endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

Document results:
- ✅ Working as expected
- ⚠️ Working with errors
- ❌ Not found (404)
- ❌ Server error (500)

### Phase 6: Database Verification

If using Supabase MCP:

```bash
# List all tables
manus-mcp-cli tool call execute_sql --server supabase \
  --input '{"project_id":"PROJECT_ID","query":"SELECT table_name FROM information_schema.tables WHERE table_schema = '\''public'\'';"}'  

# Check table schema
manus-mcp-cli tool call execute_sql --server supabase \
  --input '{"project_id":"PROJECT_ID","query":"SELECT * FROM table_name LIMIT 5;"}'
```

Verify:
- Tables exist as documented
- Schema matches CREATE TABLE statements
- Sample data is present
- Data types are correct

### Phase 7: Execution Log Creation

Maintain a detailed execution log throughout the process:

```markdown
# Project Ingestion Log

## Phase 1: Documentation Analysis ✅
- Read handoff document
- Identified 5 services
- Found 12 environment variables

## Phase 2: Service Verification ⚠️
- API: ✅ Online (response time: 450ms)
- Database: ✅ Accessible via MCP
- Repository: ❌ Access denied
- Frontend: ✅ Deployed and responsive

## Phase 3: Discrepancies Found
1. Payment endpoints documented but not deployed
2. Stripe keys claimed missing but actually configured
...
```

### Phase 8: Comprehensive Documentation

Create final deliverables:

**System Health Report**
- Executive summary
- Component status table
- Discrepancy analysis
- Actionable recommendations

**Deployment Guide**
- Step-by-step deployment instructions
- Corrected environment variable lists
- Testing procedures
- Troubleshooting section

## GitHub Access Pattern

When repository access is denied:

1. **Verify the error**: Attempt clone and capture exact error message
2. **Check authentication**: Run `gh auth status` to verify GitHub CLI is authenticated
3. **Request access**: Ask user to add collaborator via Settings → Collaborators
4. **Provide guidance**: Give user step-by-step instructions with screenshots if needed
5. **Alternative approach**: Suggest making repository temporarily public
6. **Confirm access**: Once granted, clone immediately and notify user they can revert to private

## Database Exploration Pattern

When exploring unknown databases:

1. **List all schemas**: Query `information_schema` for all tables
2. **Check for configuration tables**: Look for tables named `*config*`, `*secret*`, `*setting*`
3. **Examine project registry**: Check for `project_registry` or similar metadata tables
4. **Query app secrets**: Look for credential storage tables
5. **Verify data integrity**: Sample data from main tables to ensure schema matches docs

## Common Pitfalls

**Don't assume documentation is accurate**: Always verify claims against actual system state.

**Don't skip endpoint testing**: Even if documentation says endpoints exist, test them.

**Don't forget to log discrepancies**: Track every difference between docs and reality.

**Don't overlook environment variables**: Check deployment platforms directly, not just documentation.

**Don't proceed without repository access**: Code analysis is critical for understanding implementation.

## Deliverables Checklist

- [ ] Execution log with all phases documented
- [ ] System health report with component status
- [ ] Discrepancy analysis table
- [ ] Comprehensive deployment guide
- [ ] API endpoint test results
- [ ] Database schema verification
- [ ] Actionable next steps

## Success Criteria

The ingestion is complete when you can answer:
- What is the actual system status (not claimed status)?
- What works and what doesn't?
- What are the exact steps to deploy missing components?
- What credentials are needed and where to get them?
- What are the known issues and how to fix them?
