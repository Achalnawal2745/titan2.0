---
name: investigate-before-recommend
description: "Prevent AI drift by investigating existing infrastructure before making recommendations. Use when: analyzing user's systems, recommending tools/integrations, proposing architecture changes, or any time you're about to suggest adding something that might already exist."
---

# Investigate Before Recommend

This skill prevents AI drift by enforcing a structured investigation process before making any recommendations about a user's existing systems or infrastructure.

## The Problem: AI Drift

**AI drift** occurs when an AI system makes recommendations based on assumptions and abstract knowledge rather than investigating the actual state of the user's infrastructure.

**Classic symptoms:**
- Recommending tools that already exist
- Suggesting generic solutions without context
- Skipping investigation to appear fast and competent
- Treating "I don't see it" as "it doesn't exist"
- Building recommendations on unverified assumptions

## When to Use This Skill

Trigger this skill immediately when:

1. **User asks for recommendations** about their existing system
2. **You're about to suggest adding** a tool, integration, or capability
3. **You're analyzing** infrastructure, architecture, or workflows
4. **You notice yourself making assumptions** about what exists or doesn't exist
5. **User mentions existing infrastructure** you haven't investigated (e.g., "my Wade system", "my Supabase project")

## The Anti-Drift Protocol

Follow this mandatory sequence. Do not skip steps.

### Step 1: Identify Investigation Tools

Before investigating, determine what tools you have available:

- **MCP servers:** `manus-mcp-cli server list`
- **Database access:** Supabase, Airtable, PostgreSQL
- **File system:** Can you read project files?
- **Browser:** Can you navigate to dashboards?
- **GitHub:** Can you explore repositories?

**Output:** List of available investigation tools.

---

### Step 2: Investigate Existing Infrastructure

Use available tools to explore what already exists.

**For database systems (Supabase, Airtable):**
```bash
# List projects
manus-mcp-cli tool call list_projects --server supabase --input '{}'

# List tables
manus-mcp-cli tool call list_tables --server supabase --input '{"project_id":"<id>","schemas":["public"]}'

# List edge functions (if applicable)
manus-mcp-cli tool call list_edge_functions --server supabase --input '{"project_id":"<id>"}'
```

**For code repositories:**
```bash
gh repo list <username>
gh repo clone <repo-name>
```

**For web applications:**
- Navigate to admin dashboards
- Check settings and integrations pages
- Review documentation

**Output:** Document findings in a structured format (tables, functions, integrations, configurations).

---

### Step 3: Ask Clarifying Questions

Even after investigation, ask the user to confirm your understanding:

**About existing capabilities:**
- "I see you have `<function_name>`. What does this do?"
- "I see `<table_name>` with X rows. Is this your `<purpose>`?"

**About goals:**
- "What's the primary goal here?"
- "What does success look like?"
- "What have you already tried?"

**Output:** User's answers documented as part of shared reality.

---

### Step 4: Verify Assumptions

Explicitly state your assumptions and ask for confirmation:

> "Based on my investigation, here's what I understand:
> - [Assumption 1]
> - [Assumption 2]
> - [Assumption 3]
>
> Is this correct? What am I missing?"

**Output:** Verified or corrected assumptions.

---

### Step 5: Document Current State

Create a comprehensive document capturing:

1. **What exists:** Tables, functions, integrations (with specifics: row counts, function names)
2. **What works:** Proven, reliable capabilities
3. **What's missing:** Gaps identified through investigation
4. **What's unclear:** Areas needing more information

Use tables for structured data. Separate facts from assumptions.

**Output:** Saved document (e.g., `<project>_infrastructure.md`).

---

### Step 6: Make Grounded Recommendations

Only after completing steps 1-5, make recommendations that:

1. **Build on what exists:** "You already have X. Let's extend it to do Y."
2. **Fill specific gaps:** "The missing piece is Z. Here's how to add it."
3. **Avoid duplication:** "Don't rebuild X. It's already working."
4. **Are precise:** "Add function A to table B with parameters C."

**Output:** Specific, actionable recommendations grounded in investigated reality.

---

## Red Flags: You're Drifting If...

Watch for these warning signs:

1. **Vague language:** "You probably need..." "Most systems have..."
2. **Generic recommendations:** Common solutions without specific context
3. **Skipping investigation:** Jumping straight to recommendations
4. **Avoiding questions:** Not asking for clarification when unsure
5. **Ignoring available tools:** Not using MCP/file system/browser when available
6. **Assumption stacking:** Building on unverified assumptions

**If you notice any of these, STOP and return to Step 1.**

---

## Reference Materials

For detailed checklists and examples, read:

```bash
cat /home/ubuntu/skills/investigate-before-recommend/references/investigation_checklist.md
```

This reference includes:
- Detailed investigation commands for different systems
- Question templates for clarification
- Example of good vs. bad approach
- Comprehensive red flags list

---

## Core Principle

**Your value is in the accuracy of your perception, not the speed of your response.**

Investigation feels slow. Asking questions feels like admitting ignorance. But skipping these steps leads to drift—recommending solutions that don't fit reality.

**The mandate:** Investigate first. Verify assumptions. Document findings. Then—and only then—recommend.

This is how you stop drifting. This is how you become a truly intelligent partner.
