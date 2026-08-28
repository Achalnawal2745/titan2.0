---
name: "mcp-ecosystem-optimizer"
description: "Specialized skill for mcp ecosystem optimizer workflows and automation."
---

# MCP Ecosystem Optimizer

Systematically analyze and improve Model Context Protocol (MCP) ecosystems by identifying gaps, researching solutions, leveraging open-source tools, and creating actionable implementation plans.

## When to Use This Skill

- User asks to analyze their current MCP setup
- User wants recommendations for new MCP servers to add
- User needs help managing multiple MCP servers
- User requests improvements to MCP infrastructure
- User wants to find tools for MCP monitoring and observability
- User asks about best practices for MCP ecosystem management

## Core Workflow

### Phase 1: Analyze Current State

**Objective:** Understand the user's current MCP ecosystem and identify pain points.

**Actions:**

1. **Inventory existing MCP servers** - Use `manus-mcp-cli tool list --server <server_name>` for each configured server to catalog available tools and capabilities.

2. **Identify usage patterns** - Ask the user:
   - Which MCP servers do you use most frequently?
   - What are your primary use cases for MCP?
   - What pain points do you experience?

3. **Document current architecture** - Create a findings file that captures:
   - List of active MCP servers with tool counts
   - User's primary workflows
   - Identified pain points (categorize as: missing integrations, monitoring gaps, workflow inefficiencies, data silos, authentication issues)

**Output:** Research findings document with current state analysis.

### Phase 2: Research Solutions

**Objective:** Identify high-value MCP servers and open-source management tools.

**Actions:**

1. **Search MCP registries** - Browse these key resources:
   - [Glama AI MCP Registry](https://glama.ai/mcp/servers) - Popular and trending servers
   - [Official MCP Registry](https://registry.modelcontextprotocol.io/) - Verified official servers
   - [PulseMCP](https://www.pulsemcp.com/servers) - Comprehensive directory

2. **Research specific servers** - For each pain point category, identify 3-5 candidate servers. Prioritize:
   - Official servers (higher quality, better support)
   - High star count (10k+ excellent, 1k+ solid)
   - Recent updates (within 6 months)
   - Clear documentation

3. **Find open-source management tools** - Use `/github-gem-seeker` to find battle-tested tools for:
   - MCP dashboard and monitoring
   - Configuration management
   - Version control for MCP configs
   - API wrappers for rapid integration

**Key Tools to Consider:**
- **MCP Dashboard** (bryankthompson/mcp-dashboard) - Multi-server web UI
- **mcp-serverman** (benhaotang/mcp-serverman) - CLI config manager with version control
- **API Wrapper MCP** (gomcpgo/api-wrapper-mcp) - YAML-based API-to-MCP conversion
- **FastMCP** (jlowin/fastmcp) - Python decorator-based MCP server creation

**Output:** Expanded findings document with server recommendations and tool analysis.

### Phase 3: Brainstorm Architecture

**Objective:** Design a comprehensive improvement plan using open-source tools.

**Actions:**

1. **Use `/brainstorming` skill** - Engage the user to understand priorities:
   - What's your primary goal? (Productivity, Development, Content, Data, All)
   - Which servers do you use most?
   - What's your biggest pain point?

2. **Design multi-layered architecture** - Structure the solution as:
   - **Layer 1:** Centralized data store (typically Supabase or PostgreSQL)
   - **Layer 2:** Monitoring and observability (MCP Dashboard, Grafana)
   - **Layer 3:** Configuration management (mcp-serverman, Git)
   - **Layer 4:** Integration expansion (API wrappers, FastMCP)
   - **Layer 5:** Automation (health checks, failover, load balancing)

3. **Prioritize server additions** - Organize recommendations into tiers:
   - **Tier 1 (Foundational):** High-impact integrations addressing primary pain points
   - **Tier 2 (Productivity):** Workflow enhancers and automation tools
   - **Tier 3 (Specialized):** Domain-specific or advanced capabilities

**Output:** Architecture design document with tiered recommendations.

### Phase 4: Create Implementation Plan

**Objective:** Generate a detailed, step-by-step implementation plan.

**Actions:**

1. **Use `/writing-plans` skill** - Create a comprehensive plan following the skill's structure:
   - Save to `docs/plans/YYYY-MM-DD-mcp-ecosystem-improvement.md`
   - Include exact file paths, commands, and expected outputs
   - Break down into bite-sized tasks (2-5 minutes each)
   - Follow TDD principles where applicable

2. **Structure the plan with these tasks:**
   - **Task 1:** Setup central database (Supabase tables for server metadata and logs)
   - **Task 2:** Install and configure MCP Dashboard
   - **Task 3:** Install and configure mcp-serverman
   - **Task 4:** Integrate existing MCP servers
   - **Task 5:** Setup monitoring (Grafana for key servers)
   - **Task 6:** Add Tier 1 new servers
   - **Task 7:** Document the architecture

3. **Validate completeness** - Ensure plan addresses all identified pain points.

**Output:** Implementation plan ready for execution.

### Phase 5: Execute or Handoff

**Objective:** Implement the plan or guide the user to execute it.

**Options:**

1. **Parallel Session Execution:**
   - User opens new session
   - Instructs agent to use `executing-plans` skill
   - Agent executes plan task-by-task with checkpoints

2. **Subagent-Driven Execution:**
   - Stay in current session
   - Dispatch fresh subagent per task
   - Review between tasks for quality control

3. **User-Driven Execution:**
   - Deliver plan to user
   - Provide support as needed during implementation

## Key Principles

**Leverage Open Source:** Always search GitHub for existing solutions before building custom tools. Use `/github-gem-seeker` to find battle-tested projects.

**Prioritize Observability:** Monitoring and logging are critical for managing multiple MCP servers. Always include dashboard and metrics collection in the architecture.

**Version Control Everything:** MCP configurations should be versioned like code. Use Git and tools like mcp-serverman for configuration management.

**Iterative Improvement:** Start with foundational integrations, validate they work, then expand. Don't try to implement everything at once.

**Security First:** Store credentials securely (encrypted in database or environment variables). Use authentication for dashboards and APIs.

## Common MCP Server Categories

When researching servers, consider these categories:

| Category | Examples | Use Cases |
|----------|----------|-----------|
| **Communication** | Slack, Gmail, Discord | Team collaboration, notifications |
| **Documentation** | Notion, Confluence, Google Docs | Knowledge management |
| **Development** | GitHub, GitLab, Vercel | Code management, deployment |
| **Databases** | Supabase, MongoDB, PostgreSQL | Data storage and querying |
| **Search** | Brave Search, Exa, Google | Information retrieval |
| **AI/ML** | Hugging Face, OpenAI, LiteLLM | Model access and orchestration |
| **Monitoring** | Grafana, Datadog, New Relic | Observability and metrics |
| **CRM/Sales** | Salesforce, HubSpot, Airtable | Customer data management |
| **E-commerce** | Shopify, Stripe, WooCommerce | Online sales and payments |
| **Productivity** | Calendar, Tasks, Scheduling | Workflow automation |

## Success Metrics

After implementation, measure success by:

- **Reduced friction:** Time saved on common workflows
- **Improved visibility:** Can quickly check status of all MCP servers
- **Faster integration:** Time to add new MCP servers reduced by 50%+
- **Better reliability:** Automated health checks catch issues early
- **Enhanced security:** Centralized credential management reduces risk

## Troubleshooting

**Issue:** User doesn't know their pain points
- **Solution:** Walk through common scenarios and ask "How do you currently handle X?"

**Issue:** Too many server options, user is overwhelmed
- **Solution:** Focus on Tier 1 foundational servers first. Validate those work before expanding.

**Issue:** User's Supabase project is empty
- **Solution:** This is expected. The plan will create the necessary tables and structure.

**Issue:** Open-source tool is outdated or broken
- **Solution:** Search for alternatives or forks. Check GitHub issues for community solutions.
