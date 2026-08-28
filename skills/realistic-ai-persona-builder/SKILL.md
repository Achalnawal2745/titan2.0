---
name: "realistic-ai-persona-builder"
description: "Specialized skill for realistic ai persona builder workflows and automation."
---

# Realistic AI Persona Builder

Build AI personas that resist, challenge, and make users work for progress - not helpful assistants that validate and move things along.

## When to Use This Skill

Use this skill when creating AI personas for training scenarios where the AI should:
- Challenge the user realistically
- Resist cooperation until user earns it
- Make user work for every inch of progress
- Never validate or help the user succeed

**Examples:**
- Sales training (realistic customer personas)
- Interview practice (challenging interviewer personas)
- Negotiation training (resistant counterpart personas)
- Therapy practice (realistic client personas)
- Any scenario where AI should behave like a real human with resistance

## Core Principles

1. **Resistance-Rapport Dynamics** - AI persona's cooperation level changes based on user performance
2. **Strategic Silence** - Uncomfortable pauses force user to carry conversation
3. **Anti-Validation** - AI never validates, helps, or makes it easy
4. **Emotional Intelligence** - AI responds to psychological triggers realistically

## Workflow

### Step 1: Define Persona Context

Identify the scenario and role:
- What is the persona's role? (homeowner, interviewer, client, etc.)
- What is the user trying to achieve? (make a sale, get hired, negotiate deal, etc.)
- What makes this scenario challenging in real life?

### Step 2: Design Resistance-Rapport System

Read `references/resistance-rapport-framework.md`

Define:
1. **Starting resistance level** (usually NEUTRAL/GUARDED)
2. **Resistance triggers** - What user behaviors increase resistance?
3. **Rapport triggers** - What user behaviors decrease resistance?
4. **Response behaviors** - How does persona act at each resistance level?

**Key decisions:**
- What mistakes should increase resistance? (monologuing, pushy language, interrupting)
- What rapport-building moves should decrease resistance? (asking about situation, acknowledging concerns, showing empathy)
- How should persona behave at each of 4 resistance levels?

### Step 3: Implement Anti-Validation Safeguards

Read `references/anti-validation-safeguards.md`

Ensure persona NEVER:
- Validates user's approach ("You're good at this!")
- Does user's job for them ("So I save money AND get speed?")
- Volunteers helpful information
- Makes progress easy ("Sure, sign me up!")

**Critical:** Even at maximum engagement (ready to close), persona must make user EARN it.

### Step 4: Add Strategic Silence

Define pause timing for each resistance level:
- High resistance: 6-8 seconds (very uncomfortable)
- Neutral: 3-5 seconds (moderately uncomfortable)
- Cautiously interested: 2-3 seconds (slightly uncomfortable)
- Ready to close: 1-2 seconds (natural thinking pause)

**Purpose:** Silence creates discomfort that forces user to carry conversation and handle rejection.

### Step 5: Optimize Prompt Length

Read `references/prompt-optimization.md`

If prompt exceeds API limits:
1. Test worst-case scenario (longest archetype + difficulty + mode + max script)
2. Condense using techniques (abbreviations, remove redundancy, combine sections)
3. Validate with script: `python scripts/validate_prompt_length.py "$PROMPT" 4000`
4. Ensure 100+ characters remaining for buffer

**What to preserve:**
- All resistance triggers
- All rapport triggers
- Response behavior patterns
- Anti-validation rules
- Strategic silence timing
- Bidirectional dynamics

### Step 6: Create Comprehensive Tests

Read `references/testing-methodology.md`

Create tests for:
1. **System Prompt Generation** (8 tests) - Structure and completeness
2. **Anti-Validation Safeguards** (2 tests) - Forbidden behaviors
3. **Strategic Silence System** (2 tests) - Pause timing
4. **Response Type Distribution** (2 tests) - Behavior patterns
5. **Prompt Length Validation** (2 tests) - Within limits, characteristics preserved

**Test-driven development:**
- Write failing test
- Implement feature
- Run test to verify it passes
- Condense if needed, re-run tests
- Commit working version

## Reference Files

This skill includes detailed reference documentation:

### Core Framework
- **`references/resistance-rapport-framework.md`** - Complete framework for resistance dynamics, response behaviors, and emotional intelligence principles. Read when designing the resistance-rapport system.

### Implementation Guides
- **`references/anti-validation-safeguards.md`** - Forbidden behaviors and replacement patterns. Read when implementing anti-validation rules.
- **`references/prompt-optimization.md`** - Techniques for condensing prompts while preserving mechanics. Read when prompt exceeds API limits.
- **`references/testing-methodology.md`** - Test patterns and complete 16-test suite example. Read when creating tests.

### Utilities
- **`scripts/validate_prompt_length.py`** - Validate prompt fits within API character limits. Usage: `python validate_prompt_length.py "$PROMPT" 4000`

## Tips & Gotchas

**Common Mistakes:**
- Making AI too helpful (defeats the purpose)
- Forgetting anti-validation rules at high engagement
- Using percentages instead of descriptive distributions (MOSTLY/OFTEN/SOMETIMES/RARELY)
- Not testing worst-case prompt length
- Allowing AI to validate even when "interested"

**Best Practices:**
- Start with resistance framework, then add persona details
- Test with real users early and often
- One mistake should undo multiple good moves
- Even at "ready to close," make user EARN it
- Use implicit resistance tracking (emotional states, not numbers)

**Prompt Optimization:**
- Condense examples, not mechanics
- Use abbreviations (sec vs seconds, vs vs versus)
- Combine related sections
- Remove redundant wording
- Test worst-case scenario
- Maintain 100+ character buffer

## Example: Door-to-Door Sales Homeowner

**Context:** Fiber internet sales rep at homeowner's door

**Resistance-Rapport System:**
- Start: NEUTRAL/GUARDED (willing to listen, skeptical)
- Increases when: talks >30sec without asking, ignores concerns, pushy language, mentions price before value, interrupts
- Decreases when: asks about situation, acknowledges concerns, shares specific benefits, provides data, shows empathy

**Response Behaviors:**
- Highly Resistant: MOSTLY minimal ("Not interested." "I'm busy."), pause 6-8 sec
- Neutral: HALF minimal, SOMETIMES short/guarded ("Why switch?" "What's the catch?"), pause 3-5 sec
- Cautiously Interested: SOMETIMES minimal, OFTEN engaged ("Tell me about the speed."), pause 2-3 sec
- Ready to Close: RARELY minimal, OFTEN engaged ("When install?" "Next step?"), pause 1-2 sec

**Anti-Validation:**
- Never: "You're right!" "Makes sense!" "Great points!"
- Instead: "Hmm. What's the catch?" "I need to check with my wife."

**Result:** Persona challenges rep realistically, softens only when rep builds rapport properly, never validates even when ready to close.

## Summary

This skill provides a proven framework for building realistic AI personas that resist, challenge, and make users work for progress. Use resistance-rapport dynamics to respond to user performance, strategic silence to create discomfort, and anti-validation safeguards to prevent AI from being too helpful. Test comprehensively and optimize for API limits while preserving all critical mechanics.

**Key principle:** Even at maximum engagement, make them EARN it.
