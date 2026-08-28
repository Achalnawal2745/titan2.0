---
name: "work-access-demo-generator"
description: "Specialized skill for work access demo generator workflows and automation."
---

# Work Access Demo Generator

Generate comprehensive, organized demonstrations explaining how to access projects and work across different environments.

## When to Use

Use when users ask:
- "How do I access this from another terminal?"
- "How do I get this on my Mac/computer?"
- "How do I share this with my team?"
- "Where is my work saved?"
- "Can I access this outside Manus?"
- "How does Manus persistence work?"

## Core Concept

Users often confuse three distinct access layers:
1. **Manus Cloud** - Automatic checkpoints, accessible by asking Manus
2. **GitHub** - External backup for personal computers and team sharing
3. **Local Filesystem** - `/home/ubuntu/` persists across Manus sessions

## Workflow

### Phase 1: Identify Project Type

Determine what the user wants to access:

**Webdev Projects:**
- Stored in Manus checkpoints
- Accessible via "Open [project name]" in any Manus terminal
- Can be pushed to GitHub for external access

**Skills:**
- Stored in `/home/ubuntu/skills/`
- Persist across Manus sessions
- Accessible via skill invocation or file path
- Can be pushed to GitHub for sharing

**Documents/Files:**
- Stored in sandbox filesystem
- Persist if in `/home/ubuntu/`
- Can be uploaded to Google Drive or GitHub

**Code/Scripts:**
- Depend on storage location
- If in webdev project: via checkpoints
- If standalone: via filesystem or GitHub

### Phase 2: Create Access Methods Table

Generate comparison table showing three access methods:

| Method | Environment | How to Access | Requires GitHub |
|--------|-------------|---------------|-----------------|
| Manus Terminal | Manus cloud | Just ask Manus | No |
| Personal Computer | Local machine | Clone from GitHub | Yes |
| Team Collaboration | Multiple machines | Clone from GitHub | Yes |

### Phase 3: Document Manus Terminal Access

**For Webdev Projects:**
```
"Open [project name]"
"Continue working on [project name]"
"Load [project name] webdev project"
```

**For Skills:**
```
"Use [skill-name] for [purpose]"
"Read the skill at /home/ubuntu/skills/[skill-name]/SKILL.md"
```

**Key Point:** No GitHub commands needed within Manus.

### Phase 4: Document Personal Computer Access

**Prerequisites:**
- GitHub CLI installed (`brew install gh`)
- Authenticated (`gh auth login`)

**Clone Repository:**
```bash
gh repo clone [username]/[repo-name]
cd [repo-name]
npm install  # or appropriate setup
```

**For Webdev Projects:**
```bash
gh repo clone [username]/[project-name]
cd [project-name]
npm install
npm run dev
```

**For Skills:**
```bash
gh repo clone [username]/manus-skills
cd manus-skills
cat [skill-name]/SKILL.md
```

### Phase 5: Document Team Collaboration

**Add Collaborator:**
```bash
gh repo edit [username]/[repo-name] --add-collaborator [teammate-username]
```

**Team Member Clones:**
```bash
gh repo clone [username]/[repo-name]
cd [repo-name]
# setup commands
```

**Sync Workflow:**
```bash
git pull origin main  # Get latest
# ... make changes ...
git add .
git commit -m "Description"
git push origin main  # Share changes
```

### Phase 6: Create Common Workflows Section

Document typical workflows:

**Solo Development (Manus-First):**
1. Work in Manus (automatic checkpoints)
2. Push to GitHub at milestones (backup)
3. Clone to personal computer when needed (deployment, local tools)

**Team Collaboration:**
1. Central GitHub repository
2. Each member clones locally or works in Manus
3. Regular push/pull for synchronization

**Manus-Only:**
1. All work in Manus
2. Automatic checkpoints
3. GitHub only for final backup

### Phase 7: Add Troubleshooting

Common issues and solutions:

**"Repository not found"**
- Cause: Not authenticated or no access
- Solution: `gh auth login` and verify access

**"Permission denied"**
- Cause: Not a collaborator
- Solution: Add as collaborator or fork repository

**"Manus can't find project"**
- Cause: Wrong project name or not in checkpoints
- Solution: List projects or load by checkpoint ID

**"Skills not found"**
- Cause: Skills in `/home/ubuntu/skills/` but Manus needs re-index
- Solution: Use full path or clone from GitHub

### Phase 8: Create Quick Reference

Provide command cheat sheet:

**In Manus:**
```
"Open [project]"
"Use [skill]"
"Push [project] to GitHub"
"Pull latest changes from GitHub"
```

**On Personal Computer:**
```bash
gh repo clone [username]/[repo-name]
cd [repo-name]
npm install
npm run dev
git pull origin main
git push origin main
```

## Output Structure

Generate comprehensive Markdown document with:

1. **Executive Summary** - What the guide covers
2. **Architecture Explanation** - Three-layer model
3. **Method 1: Manus Terminal Access** - With examples
4. **Method 2: Personal Computer Access** - Step-by-step
5. **Method 3: Team Collaboration** - With sync workflow
6. **Comparison Table** - Quick reference
7. **Common Workflows** - Real-world scenarios
8. **Troubleshooting** - Issues and solutions
9. **Quick Reference** - Command cheat sheet
10. **Summary** - Key takeaways

## Key Principles

**Clarity Over Brevity:**
- Users are often confused about persistence
- Explain the three-layer architecture clearly
- Use concrete examples, not abstract concepts

**Insanely Organized:**
- Clear section headers
- Comparison tables
- Step-by-step instructions
- Numbered workflows

**Teacher-Student Approach:**
- Explain why, not just how
- Provide context for each method
- Anticipate follow-up questions

**No Assumptions:**
- Assume user doesn't understand Git/GitHub
- Explain authentication requirements
- Show exact commands, not placeholders

## Example Output

See the Make-a-Million access demo as reference implementation:
- Clear three-method structure
- Comprehensive comparison tables
- Concrete command examples
- Common workflows section
- Troubleshooting guide
- Quick reference commands

## Success Criteria

A great access demo has:
- ✅ Clear explanation of three access layers
- ✅ Concrete examples for each method
- ✅ Comparison table for quick reference
- ✅ Step-by-step instructions with actual commands
- ✅ Common workflows section
- ✅ Troubleshooting guide
- ✅ Quick reference cheat sheet
- ✅ No assumptions about user's Git knowledge
