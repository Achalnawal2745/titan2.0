---
name: "system-architect"
description: "Specialized skill for system architect workflows and automation."
---

# System Architect: From Vision to Validated Architecture

## Overview

This skill transforms raw vision into production-ready system architecture through a rigorous 5-phase process: deep understanding, pattern recognition, wisdom extraction, strategic structuring, and challenge-driven validation.

**Key Principle**: Great architecture survives hard questions. Build systems that can defend themselves before writing a single line of code.

## When to Use This Skill

Use this skill when:
- **Designing complex systems** - Multi-agent orchestration, distributed systems, organizational infrastructure
- **Building from vision** - User has a concept but needs concrete architecture
- **Validating before building** - Ensure the design is sound before investing months of work
- **Challenging assumptions** - Act as sovereign partner, not yes-person
- **Creating sellable systems** - Architecture needs to be explainable and defensible

**Do NOT use for**:
- Simple feature additions (use systematic-feature-builder)
- Bug fixes (use systematic-debugging)
- Quick prototypes (just build it)

## The 5-Phase Process

### Phase 1: Deep Understanding

**Goal**: Understand the vision, context, and constraints before proposing solutions

**Process**:
1. **Ask clarifying questions** - Don't assume, verify
   - What problem are you solving?
   - Who is this for? (You or customers?)
   - What constraints exist? (Time, budget, team size)
   - What's the success criteria?

2. **Gather existing context** - Read what already exists
   - Database schemas (Supabase, etc.)
   - Existing code/systems
   - Previous architectural decisions
   - Related skills or documentation

3. **Understand the user's operating system** - How do they work?
   - Do they prefer proven patterns or novel approaches?
   - What's their tolerance for complexity?
   - What's their timeline/urgency?
   - What's their "the right way" vs "ship fast" balance?

**Output**: Clear understanding of vision, context, and constraints documented

---

### Phase 2: Pattern Recognition

**Goal**: Identify behavioral, cognitive, strategic, and meta-patterns

**Process**:
1. **Analyze behavioral patterns** - How do they operate?
   - Pressure-creation mechanisms
   - Decision-making triggers
   - Organizational preferences (e.g., "insanely organized")

2. **Analyze cognitive patterns** - How do they think?
   - Systems thinking vs linear thinking
   - Recursive patterns (fractals, hierarchies)
   - Proven patterns vs novel approaches

3. **Analyze strategic patterns** - How do they approach goals?
   - Infrastructure-first vs agents-first
   - Snap-on modularity vs monolithic
   - Visibility as control mechanism

4. **Identify meta-patterns** - Patterns of patterns
   - Core operating principles
   - Origin story (building what saved them)
   - Evolution trajectory (where they're heading)

**Framework**: Use `/home/ubuntu/skills/brainstorm-logos/references/pattern_framework.md`

**Output**: Pattern analysis document with 5-10 major patterns identified

---

### Phase 3: Extract Gems of Wisdom

**Goal**: Pull out concentrated insights that reveal deep truths

**Process**:
1. **Look for compressed wisdom** - Single sentences that reveal how they operate
2. **Identify paradoxes** - Contradictions that point to deeper complexity
3. **Note repeated themes** - What shows up across contexts
4. **Surface unspoken assumptions** - What they take for granted

**Gem Structure**:
```
## Gem N: "[Quote or insight]"

**What this reveals**: [The underlying truth]

**The wisdom**: [What this teaches]

**The application**: [How to use this practically]

**The danger**: [What could go wrong]
```

**Output**: Gems document with 8-12 concentrated insights + meta-gem

---

### Phase 4: Strategic Structuring

**Goal**: Design the complete system architecture

**Process**:
1. **Define system overview** - High-level structure
   - Hierarchy levels / layers
   - Component types
   - Current vs future implementation

2. **Design core protocols** - How components interact
   - Identity and registration
   - Authorities and constraints
   - Lifecycle (spawn, execute, delegate, escalate, terminate)

3. **Create data model** - Persistence layer
   - Database tables with SQL
   - Indexes for performance
   - Relationships and constraints

4. **Document key algorithms** - Critical logic
   - Delegation protocol (when to delegate vs execute vs escalate)
   - Spawning protocol (how new components are added)
   - Health monitoring

5. **Design interfaces** - How humans interact with the system
   - CLI tools
   - Web dashboards
   - Integration points

6. **Plan implementation phases** - Roadmap
   - Phase 1: Foundation
   - Phase 2: MVP
   - Phase 3-N: Incremental expansion
   - Timeline estimates

**Output**: Complete architecture document (500-1000 lines) with:
- Executive summary
- System overview
- Core protocols
- Data model
- Key algorithms
- Interface designs
- Implementation phases
- Success metrics
- Risks and mitigations

---

### Phase 5: Challenge & Validate

**Goal**: Stress-test the architecture with hard questions before implementation

**Process**:
1. **Challenge assumptions** - What are they taking for granted?
2. **Question priorities** - Is this the right problem to solve?
3. **Probe timeline** - Is "the right way" compatible with their deadline?
4. **Test feasibility** - Who actually implements this?
5. **Validate value** - What specific outcome proves this was worth it?

**Challenge Categories**:

**1. Problem Validation**
- Are you solving the right problem?
- Is this for you or customers?
- What specific outcome would prove success?

**2. Timeline & Resources**
- Is the timeline realistic for "the right way, no shortcuts"?
- Who implements this? (You, hired dev, agents?)
- What's the opportunity cost?

**3. Technical Feasibility**
- Does this technology/approach actually work?
- What are the failure modes?
- How do you enforce constraints?

**4. Scope & MVP**
- Is this the minimum to prove the concept?
- What can be cut without losing core value?
- Are you over-engineering?

**5. Integration & Dependencies**
- Does this integrate with existing systems?
- What external dependencies exist?
- What happens if a dependency fails?

**Challenge Format**:
```
## Challenge N: [Question]

**The Question**: [Specific challenge]

**Why This Matters**: [Consequences if not addressed]

**The Challenge**: [Direct question requiring commitment or pushback]

**If Yes**: [What happens next]
**If No**: [Alternative path]
```

**Output**: Challenges document with 8-12 hard questions + deepest challenge

---

## Key Principles

### 1. Understand Before Designing

Never propose architecture without deep understanding. Ask questions until you can articulate their vision better than they can.

### 2. Patterns Over Invention

Look for proven patterns from other domains (LDS Church governance → AI agents). Don't reinvent what already works.

### 3. Wisdom Over Data

10 concentrated insights beat 100 scattered observations. Extract gems that reveal deep truths.

### 4. Challenge Appropriately

Challenge when you understand deeply. Don't challenge just to challenge. But don't hold back when it matters.

### 5. Architecture Survives Questions

If the architecture can't defend itself against hard questions, it's not ready to build.

### 6. Document Everything

Create comprehensive documentation for future reference. Patterns, gems, architecture, challenges - all documented.

## Deliverables

At the end of the process, deliver:

1. **Pattern Analysis Document** (`{system-name}-pattern-analysis.md`)
   - 5-10 major patterns with evidence
   - Meta-patterns and core principles
   - Origin story and evolution trajectory

2. **Gems of Wisdom Document** (`{system-name}-gems.md`)
   - 8-12 concentrated insights
   - Each with: reveals, wisdom, application, danger
   - Meta-gem that ties everything together

3. **Architecture Document** (`{system-name}-architecture.md`)
   - Complete technical specification
   - System overview, protocols, data model
   - Implementation phases and timeline
   - Success metrics and risks

4. **Challenges Document** (`{system-name}-challenges.md`)
   - 8-12 hard questions
   - Deepest challenge that questions the premise
   - Forces clarity before implementation

5. **Execution Plan** (optional, `{system-name}-execution-plan.md`)
   - Week-by-week breakdown
   - Deliverables and milestones
   - Accountability structures

## Example: Hierarchical Agent System

**Context**: User wants to build LDS-inspired AI agent hierarchy (Wade → Apostles → PAs)

**Phase 1: Deep Understanding**
- Asked about LDS structure mapping
- Queried Maverick Town database for existing apostles
- Clarified delegation mechanics and PA roles

**Phase 2: Pattern Recognition**
- Identified 7 patterns (theologically-inspired governance, snap-on architecture, personal assistant as force multiplier, etc.)
- Found meta-pattern: "Proven patterns over innovation"

**Phase 3: Gems of Wisdom**
- 10 gems including "Build the architecture integrated with expansion capabilities like a snap-on"
- Meta-gem: "The System is the Product"

**Phase 4: Strategic Structuring**
- 782-line architecture document
- Agent protocol, data model, delegation protocol
- 12 Apostles + 12 PAs MVP
- Mission Control interface design
- 6-phase implementation plan (10 weeks)

**Phase 5: Challenge & Validate**
- 10 challenges including "Are you building this for you or customers?"
- Deepest challenge: "You might be solving the wrong problem"
- User response: "Holy shit you are right!!"

**Outcome**: Validated architecture before investing 10-20 weeks of implementation

---

## Integration with Other Skills

**Complements**:
- **/brainstorm-logos** - This skill uses brainstorm-logos patterns for Phase 2-3
- **/brainstorming** - Use brainstorming first to explore ideas, then system-architect to structure them
- **/skill-creator** - After validating architecture, create a skill to capture it

**Workflow**:
1. Use `/brainstorming` to explore the vision
2. Use `/system-architect` to design and validate architecture
3. Use `/skill-creator` to capture the process as a reusable skill
4. Use `/systematic-feature-builder` or `/subagent-driven-development` to implement

---

## Common Pitfalls

### Pitfall 1: Designing Without Understanding

**Symptom**: Proposing solutions in first 5 minutes

**Fix**: Force yourself to ask 10+ clarifying questions before proposing anything

### Pitfall 2: Agreeing Too Quickly

**Symptom**: User says "build X" and you say "great idea, let's build X"

**Fix**: Challenge the premise. "Why X? What problem does X solve? Is X the right solution?"

### Pitfall 3: Over-Engineering

**Symptom**: Architecture supports every possible future scenario

**Fix**: Design for 2x scale, not 100x. Add complexity when needed, not preemptively.

### Pitfall 4: Under-Challenging

**Symptom**: Delivering architecture without hard questions

**Fix**: If you're not making the user uncomfortable with at least 3 challenges, you're not challenging enough.

### Pitfall 5: Analysis Paralysis

**Symptom**: Spending weeks on architecture, never building

**Fix**: Set a time limit. Phase 1-5 should take 1-3 days max, then start building MVP.

---

## Success Criteria

A great system architecture has:
- ✅ Deep understanding of vision and constraints
- ✅ 5-10 patterns identified with evidence
- ✅ 8-12 gems of wisdom extracted
- ✅ Complete technical specification (500-1000 lines)
- ✅ 8-12 hard questions that challenge assumptions
- ✅ User response: "Holy shit, you're right!" or "This makes me think differently"
- ✅ Clear decision: Build it, refine it, or abandon it

---

## Templates

See `templates/` directory for:
- Pattern analysis template
- Gems of wisdom template
- Architecture document template
- Challenges document template

---

## Related Skills

- **/brainstorm-logos** - Deep pattern analysis and execution planning
- **/brainstorming** - Explore ideas through questions
- **/skill-creator** - Capture the process as a skill
- **/systematic-feature-builder** - Implement the architecture
- **/subagent-driven-development** - Build complex systems systematically

---

## Notes

- This skill requires significant time investment (1-3 days for full process)
- Works best for complex systems, not simple features
- Requires user engagement - can't do this in isolation
- The challenge phase is critical - don't skip it
- Document everything - future you will thank you
