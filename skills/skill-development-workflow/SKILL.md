---
name: "skill-development-workflow"
description: "Specialized skill for skill development workflow workflows and automation."
---

# Skill Development Workflow

This skill automates the initial setup of a new skill, including creating the directory structure and validating it.

## Quick Start

To create a new skill called `my-new-skill`, run:

```bash
/home/ubuntu/skills/skill-development-workflow/scripts/run_workflow.sh my-new-skill
```

## The Workflow

This skill performs the following steps in order:

1.  **Initialize:** Uses the `skill-creator` skill to create the directory structure for the new skill.

2.  **Validate:** Uses the `skill-creator` skill to validate that the new skill's structure is correct.

3.  **Discover:** The `skillz` server will automatically discover the new skill, making it available as an MCP tool.

## What You Get

- A new skill directory created in `/home/ubuntu/skills/`
- A validated skill structure
- The new skill is immediately available via the `skillz` server

## Next Steps

After running the workflow, you need to:

1.  **Edit the `SKILL.md`** in your new skill's directory to describe what it does.
2.  **Add your scripts** to the `scripts/` directory.
3.  **Test your skill** to make sure it works as expected.

## Why This is a "Meta-Skill"

This skill is a "meta-skill" because it's a skill that helps you create other skills. It automates the repetitive parts of skill creation so you can focus on building the unique logic of your new skill.
