---
name: "skill-demo-builder"
description: "Specialized skill for skill demo builder workflows and automation."
---

# Skill Demo Builder

## Overview

This skill provides a systematic 6-phase workflow for creating professional, comprehensive demonstrations of any skill. It captures the proven process of choosing complementary examples, building them with best practices, documenting thoroughly, and delivering professionally.

**Key Principle**: Great demos showcase different aspects through complementary examples, not just different technologies.

## When to Use This Skill

Use this skill when:
- **Demonstrating a new skill** - Show what it can do with concrete examples
- **Creating reference implementations** - Build examples others can learn from
- **Showcasing capabilities** - Prove a skill works in practice
- **Building portfolio pieces** - Create professional demo projects
- **Teaching others** - Provide hands-on examples

## The 6-Phase Workflow

### Phase 1: Design Demonstration Examples

**Goal**: Choose 2+ complementary examples that showcase different aspects

**Process**:
1. Identify the skill's core capabilities
2. Choose examples that demonstrate different strengths
3. Ensure examples are complementary (not just different tech stacks)
4. Verify examples are realistic and practical

**Example from MCP Builder Demo**:
- Example 1: JSONPlaceholder (TypeScript) - Comprehensive CRUD, HTTP transport
- Example 2: NASA APOD (Python) - Workflow-oriented, stdio transport
- **Complementary because**: Different design philosophies, not just different languages

**Decision Framework**:
```
Do the examples showcase:
✅ Different use cases? (CRUD vs workflow)
✅ Different patterns? (comprehensive vs focused)
✅ Different transports? (HTTP vs stdio)
✅ Different complexity levels? (simple vs advanced)
```

**Output**: List of 2-3 complementary examples with justification

---

### Phase 2: Research & Preparation

**Goal**: Gather information needed to build each example

**Process**:
1. Research APIs/services for each example
2. Document key endpoints/features
3. Identify authentication requirements
4. Note any gotchas or limitations
5. Save research notes

**Tools to Use**:
- Browser for API documentation
- `/github-gem-seeker` for existing solutions
- API testing tools (curl, Postman)

**Output**: Research notes with API details, authentication, rate limits, examples

---

### Phase 3: Build Examples

**Goal**: Create production-ready examples following best practices

**Process**:
1. Set up project structure for each example
2. Implement core functionality
3. Add validation and error handling
4. Test with real API calls
5. Create individual READMEs

**Best Practices**:
- ✅ Use proper validation (Zod for TS, Pydantic for Python)
- ✅ Comprehensive error handling with clear messages
- ✅ Follow language/framework conventions
- ✅ Include comments for complex logic
- ✅ Test before moving to next phase

**Quality Checklist**:
```
For each example:
□ Syntax valid (no compilation/parsing errors)
□ Dependencies installed and working
□ Error handling comprehensive
□ README explains setup and usage
□ Tested with real data
```

**Output**: 2-3 fully functional examples with individual READMEs

---

### Phase 4: Create Documentation

**Goal**: Write comprehensive documentation that explains everything

**Documents to Create**:

1. **Main Demo Document** (`{skill-name}-demo.md`)
   - Executive summary
   - What was built (with comparison table)
   - Key takeaways
   - Usage examples
   - Next steps
   
2. **Execution Log** (`{skill-name}-execution-log.md`)
   - Phase-by-phase breakdown
   - Key architectural decisions
   - Lessons learned and gotchas
   - Testing results
   - Files created

3. **Session Review** (optional, for multi-deliverable sessions)
   - Overview of all deliverables
   - Metrics and statistics
   - Links and commands
   - Meta-reflection

**Documentation Principles**:
- Be comprehensive but scannable
- Use tables for comparisons
- Include concrete examples
- Document decisions and trade-offs
- Capture "gotchas" for future reference

**Templates**: See `templates/` directory for structures

---

### Phase 5: Package & Upload

**Goal**: Package everything professionally for distribution

**Process**:
1. Create zip archives of each example
2. Upload to Google Drive
3. Get shareable links
4. Organize in clearly named folders

**Folder Naming Convention**:
```
{skill-name}-demo-{timestamp}
```

**What to Include**:
- Zip files of each example
- Main demo document
- Execution log
- Session review (if applicable)

**Output**: Google Drive folder with shareable link

---

### Phase 6: Deliver Results

**Goal**: Provide comprehensive review and next steps

**Deliverables**:
1. Main demo document (attached)
2. Execution log (attached)
3. Packaged archives (attached or linked)
4. Google Drive link
5. Sync commands (if using autonomous-sync-script)

**Delivery Message Structure**:
```markdown
## Demo Complete! 🎉

### What Was Built
- Example 1: [description]
- Example 2: [description]

### Key Achievements
- ✅ [achievement 1]
- ✅ [achievement 2]

### Documentation Included
1. [document 1]
2. [document 2]

### Next Steps
[actionable next steps]

### Links
- Google Drive: [link]
- Sync commands: [commands]
```

---

## Best Practices

### Choosing Complementary Examples

**Good Complementary Pairs**:
- ✅ Simple + Complex (show range)
- ✅ Read-only + CRUD (show different operations)
- ✅ Public API + Authenticated API (show auth patterns)
- ✅ Workflow-oriented + Comprehensive (show design philosophies)

**Poor Complementary Pairs**:
- ❌ Two similar APIs (redundant)
- ❌ Same pattern, different language (not complementary)
- ❌ Both overly complex (overwhelming)
- ❌ Both trivial (not impressive)

### Documentation Quality

**Execution Log Should Include**:
- Phase-by-phase breakdown
- Key decisions with rationale
- Alternatives considered
- Gotchas encountered
- Code snippets for critical parts
- Testing results

**Demo Document Should Include**:
- Executive summary (what was built)
- Comparison table (side-by-side)
- Key features highlighted
- Usage examples
- Next steps

### Testing Before Delivery

**Minimum Testing**:
```
□ Syntax validation (compile/parse)
□ Dependencies install correctly
□ Scripts execute without errors
□ Documentation is accurate
□ Links work
□ Zip files contain correct contents
```

---

## Common Patterns

### Pattern 1: Two-Language Demo

**Use when**: Demonstrating language-agnostic concepts

**Structure**:
- Example 1: TypeScript/JavaScript
- Example 2: Python

**Benefits**: Shows portability, appeals to different audiences

**Example**: MCP Builder Demo (TypeScript + Python)

---

### Pattern 2: Simple-to-Complex Demo

**Use when**: Teaching or onboarding

**Structure**:
- Example 1: Minimal, focused
- Example 2: Full-featured, comprehensive

**Benefits**: Progressive learning, shows scalability

---

### Pattern 3: Different Use Case Demo

**Use when**: Skill has multiple applications

**Structure**:
- Example 1: Use case A
- Example 2: Use case B

**Benefits**: Shows versatility, targets different user needs

---

## Troubleshooting

### "Examples aren't complementary enough"

**Symptom**: Examples feel redundant or too similar

**Solution**:
1. Review the decision framework in Phase 1
2. Identify what makes each example unique
3. Consider different use cases, not just different tech
4. Ask: "What does Example 2 show that Example 1 doesn't?"

### "Documentation is too long"

**Symptom**: Documents exceed 20 pages

**Solution**:
1. Use tables instead of paragraphs for comparisons
2. Move detailed code to appendices
3. Focus on key decisions, not every detail

### "Examples don't work"

**Symptom**: Errors when running examples

**Solution**:
1. Test each example independently
2. Verify dependencies are documented
3. Check API keys/authentication
4. Run in clean environment

---

## Examples of Great Demos

### MCP Builder Demo

**Examples**:
1. JSONPlaceholder MCP (TypeScript) - 10 tools, HTTP transport
2. NASA APOD MCP (Python) - 4 tools, stdio transport

**Why it's great**:
- ✅ Complementary design philosophies (comprehensive vs focused)
- ✅ Different transports (HTTP vs stdio)
- ✅ Both production-ready
- ✅ Comprehensive documentation
- ✅ Tested and validated

---

## Templates

Use the templates in `templates/` directory for:
- Demo document structure
- Execution log structure
- Research notes structure

---

## Related Skills

- **/mcp-builder** - Build MCP servers
- **/skill-development-workflow** - Create new skills
- **/autonomous-sync-script** - Sync demos to GitHub
- **/github-gem-seeker** - Find existing solutions

---

## Success Criteria

A great demo has:
- ✅ 2-3 complementary examples (not just different tech)
- ✅ All examples fully functional and tested
- ✅ Comprehensive documentation (demo doc + execution log)
- ✅ Professional packaging (zips + Google Drive)
- ✅ Clear next steps for users
- ✅ Captures lessons learned and gotchas
