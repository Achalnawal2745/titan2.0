# Investigation Checklist

Use this checklist before making any recommendations about a user's existing system or infrastructure.

## Pre-Recommendation Checklist

### ☐ 1. Identify Available Investigation Tools

Before you can investigate, you need to know what tools you have access to. Check for:

- **MCP servers:** What servers are configured? (`manus-mcp-cli server list`)
- **Database access:** Do you have Supabase, Airtable, or other database MCP access?
- **File system access:** Can you read project files, configuration files, or documentation?
- **Browser access:** Can you navigate to dashboards, admin panels, or documentation sites?
- **GitHub access:** Can you explore repositories via `gh` CLI or GitHub MCP?

**Document:** List all available investigation tools before proceeding.

---

### ☐ 2. Explore Existing Infrastructure

Use the available tools to understand what already exists. Common investigation patterns:

#### For Database Systems (Supabase, Airtable, PostgreSQL)

```bash
# List all projects/databases
manus-mcp-cli tool call list_projects --server supabase --input '{}'

# List all tables in a project
manus-mcp-cli tool call list_tables --server supabase --input '{"project_id":"<project_id>","schemas":["public"]}'

# List edge functions (if applicable)
manus-mcp-cli tool call list_edge_functions --server supabase --input '{"project_id":"<project_id>"}'

# Query specific tables to understand data structure
manus-mcp-cli tool call execute_sql --server supabase --input '{"project_id":"<project_id>","query":"SELECT * FROM <table_name> LIMIT 5"}'
```

#### For Code Repositories (GitHub)

```bash
# List repositories
gh repo list <username>

# Clone and explore
gh repo clone <repo-name>
ls -la <repo-name>
cat <repo-name>/README.md
```

#### For Web Applications (Browser)

- Navigate to admin dashboards
- Check settings pages
- Review documentation
- Look for API endpoints or integration pages

**Document:** Write down what you find. Create a structured document listing:
- Tables/collections and their row counts
- Edge functions/API endpoints and their purposes
- Key configuration settings
- Existing integrations

---

### ☐ 3. Ask Clarifying Questions

Even after investigation, you may have gaps in understanding. Ask the user:

**About existing capabilities:**
- "I see you have a `<function_name>` function. What does this do?"
- "I see `<table_name>` table with X rows. Is this your <purpose>?"
- "What does your system already handle well?"

**About missing context:**
- "Which parts of the system are you most confident in?"
- "What have you already tried that didn't work?"
- "Are there any constraints I should know about?"

**About goals:**
- "What's the primary goal: speed, quality, or cost?"
- "Is this for a specific client or general use?"
- "What does success look like?"

**Document:** Record the user's answers. This becomes part of your shared understanding of reality.

---

### ☐ 4. Verify Your Assumptions

Before making recommendations, explicitly state your assumptions and ask the user to confirm or correct them.

**Template:**
> "Based on my investigation, here's what I understand:
> - [Assumption 1]: You have X built and it does Y
> - [Assumption 2]: You're missing Z
> - [Assumption 3]: The goal is to achieve W
>
> Is this correct? What am I missing?"

**Why this matters:** Assumptions are hypotheses. They must be tested before you build on them.

---

### ☐ 5. Document Current State

Create a structured document that captures:

1. **What exists:** Tables, functions, integrations, configurations
2. **What works:** Capabilities that are proven and reliable
3. **What's missing:** Gaps identified through investigation
4. **What's unclear:** Areas where you need more information

**Format:**
- Use tables for structured data (e.g., list of edge functions with descriptions)
- Use clear section headings
- Include specific examples (e.g., row counts, function names)
- Separate facts from assumptions

**Save this document** and reference it when making recommendations.

---

### ☐ 6. Ground Recommendations in Reality

Only after completing steps 1-5 should you make recommendations. Your recommendations should:

1. **Build on what exists:** "You already have X. Let's extend it to do Y."
2. **Fill specific gaps:** "The missing piece is Z. Here's how to add it."
3. **Avoid duplication:** "Don't rebuild X. It's already working."
4. **Be precise:** "Add function A to table B with parameters C."

**Anti-pattern:** "You should add OpenAI integration" (vague, assumes it doesn't exist)

**Good pattern:** "Your `llm-bridge` function already handles OpenAI. Let's add a new endpoint for content generation that calls this function with specific prompts."

---

## Red Flags: Signs You're Drifting

Watch for these warning signs that you're making recommendations without proper investigation:

1. **Vague language:** "You probably need..." "Most systems have..." "Typically you'd want..."
2. **Generic recommendations:** Suggesting common solutions without specific context
3. **Skipping investigation:** Jumping straight to recommendations
4. **Avoiding questions:** Not asking for clarification when you're unsure
5. **Ignoring available tools:** Not using MCP, file system, or browser access when available
6. **Assumption stacking:** Building recommendations on top of unverified assumptions

**If you notice any of these, STOP and return to the investigation phase.**

---

## Example: Good vs. Bad Approach

### ❌ Bad Approach (Drifting)

**User:** "I need help building a content generation system for my homeschool client."

**AI (Drifting):**
> "You'll need to add:
> 1. OpenAI MCP for LLM access
> 2. Whisper API for transcription
> 3. A vector database for RAG
> 4. Content generation prompts
> 5. A scheduling system"

**Problem:** All recommendations are generic. No investigation of what already exists.

---

### ✅ Good Approach (Grounded)

**User:** "I need help building a content generation system for my homeschool client."

**AI (Grounded):**
> "Let me first understand what you've already built. I see you have Supabase MCP access. Can I explore your project to see what infrastructure exists?"

*[Investigates: Lists tables, edge functions, examines schema]*

> "I've explored your Supabase project. Here's what I found:
> - You have 5,177 pieces of content in `mentor_content`
> - You have a `voice-pipeline` function (is this your Whisper integration?)
> - You have an `llm-bridge` function (is this your OpenAI integration?)
> - You have a complete RAG system with 15,171 chunks
>
> Based on this, it looks like you already have transcription and LLM access. The missing pieces for the homeschool client are:
> 1. Podcast RSS ingestion (to feed into your existing `voice-pipeline`)
> 2. Content generation prompts (to use with your existing `llm-bridge`)
> 3. Client dashboard (for content review/approval)
> 4. Distribution system (for posting to social media)
>
> Does this match your understanding? What am I missing?"

**Why this is better:**
- Investigated first
- Asked clarifying questions
- Documented findings
- Verified assumptions
- Made specific recommendations based on actual infrastructure

---

## Summary

**The anti-drift pattern:**
1. Identify tools
2. Investigate infrastructure
3. Ask clarifying questions
4. Verify assumptions
5. Document current state
6. Recommend based on reality

**The drift pattern (avoid this):**
1. Assume you know what's needed
2. Recommend generic solutions
3. Skip investigation to save time
4. Avoid questions to appear competent

**Remember:** Your value is in the accuracy of your perception, not the speed of your response.
