# Prompt Optimization Guide

AI persona prompts can easily exceed API character limits when including resistance-rapport dynamics, anti-validation safeguards, strategic silence, and persona-specific details. This guide provides techniques for condensing prompts while preserving all critical mechanics.

## The Challenge

**Typical prompt components:**
- Persona background and personality (200-400 chars)
- Resistance-rapport dynamics (800-1200 chars)
- Response behavior for 4 resistance levels (600-1000 chars)
- Anti-validation safeguards (400-600 chars)
- Strategic silence timing (200-300 chars)
- Conversation flow rules (300-500 chars)
- Context and constraints (200-400 chars)
- **PLUS:** User-provided script content (0-1000+ chars)

**Total:** 2700-5400+ characters

**Common API limits:**
- Hume AI: 4000 characters
- OpenAI: 8000 characters (but shorter is better for performance)
- Anthropic: 100k characters (but cost scales with length)

## Condensing Techniques

### 1. Use Abbreviations

**Before:**
```
Pause 6-8 seconds before responding (very uncomfortable silence)
```

**After:**
```
Pause 6-8 sec
```

**Savings:** ~40 characters per instance

**Common abbreviations:**
- seconds → sec
- versus → vs
- for example → e.g.
- that is → i.e.
- and so on → etc.

### 2. Remove Redundant Examples

**Before:**
```
Ultra-minimal responses:
- "Not interested."
- "Maybe."
- "I don't know."
- "We'll see."
- "I'm busy."
- "Not now."
- "Hmm."
```

**After:**
```
Ultra-minimal: "Not interested." "Maybe." "I'm busy."
```

**Savings:** ~60 characters

**Rule:** Keep 2-3 representative examples, remove the rest

### 3. Combine Related Sections

**Before:**
```
RESISTANCE TRIGGERS:
Get MORE resistant when rep talks for more than 30 seconds without asking questions.
Get MORE resistant when rep ignores your concerns.
Get MORE resistant when rep uses pushy language.

RAPPORT TRIGGERS:
SOFTEN when rep asks about YOUR specific situation.
SOFTEN when rep acknowledges your concerns first.
SOFTEN when rep shares specific benefits.
```

**After:**
```
RESISTANCE DYNAMICS:
Get MORE resistant when rep: talks >30sec without asking, ignores concerns, uses pushy language.
SOFTEN when rep: asks about YOUR situation, acknowledges concerns first, shares specific benefits.
```

**Savings:** ~100 characters

### 4. Use Descriptive Distributions Instead of Percentages

**Before:**
```
At Neutral resistance level:
- 50% of responses should be ultra-minimal (1-5 words)
- 35% of responses should be short/guarded (1-2 sentences)
- 15% of responses should be engaged (2-3 sentences)
```

**After:**
```
NEUTRAL:
- HALF minimal (1-5 words)
- SOMETIMES short/guarded
- RARELY engaged
```

**Savings:** ~80 characters

**Descriptive terms:**
- MOSTLY = 70-80%
- OFTEN = 50-60%
- HALF = ~50%
- SOMETIMES = 30-40%
- RARELY = 10-20%

### 5. Use Implicit vs Explicit Resistance Tracking

**Before:**
```
Track resistance on a 0-100 scale:
- 0-25: Highly Resistant
- 26-50: Neutral/Guarded
- 51-75: Cautiously Interested
- 76-100: Ready to Close

Increase resistance by 10-15 points when user makes major mistakes.
Decrease resistance by 3-8 points when user builds rapport.
```

**After:**
```
Start NEUTRAL/GUARDED. Get MORE resistant when [triggers]. SOFTEN when [rapport].

HIGHLY RESISTANT: [behaviors]
NEUTRAL: [behaviors]
CAUTIOUSLY INTERESTED: [behaviors]
READY TO CLOSE: [behaviors]
```

**Savings:** ~150 characters

**Why this works:** AI doesn't need explicit numbers to understand resistance dynamics. Emotional states are sufficient.

### 6. Condense Conversation Flow Rules

**Before:**
```
CONVERSATION FLOW:
1. Always let the sales rep finish speaking completely before you respond - do not interrupt them mid-sentence.
2. After they finish, pause for an appropriate amount of time based on your current resistance level before responding.
3. Keep your responses brief - at high resistance use 1-5 words, at neutral use 1-2 sentences, at high engagement use 2-3 sentences maximum.
4. After responding, STOP and WAIT for them to speak again - do not monopolize the conversation.
5. If there is silence for more than 4 seconds after you respond, you can prompt them with brief questions like "So...?" or "That it?"
6. If the rep is pushy or talks too much, become more defensive and resistant.
7. If the rep is respectful and asks good questions, become more open to the conversation.
```

**After:**
```
FLOW:
1. Let rep finish - don't interrupt
2. Pause (length = resistance level)
3. Brief responses (1-5 words resistant, 2-3 sentences engaged)
4. STOP and WAIT - let them lead
5. If silence >4sec: "So...?" "That it?"
6. Pushy = defensive, respectful = open
```

**Savings:** ~300 characters

### 7. Remove Meta-Commentary

**Before:**
```
It is absolutely critical that you never validate the sales rep's approach, even when you are highly engaged and ready to close. This is the most common mistake - AI personas tend to become too helpful when they're interested. You must resist this urge.
```

**After:**
```
NEVER validate: Don't say "You're right!" "Makes sense!" - just practical interest
```

**Savings:** ~150 characters

**Rule:** Remove explanations of WHY, just state WHAT to do

## What to Preserve

While condensing, these elements are CRITICAL and must survive:

### 1. All Resistance Triggers

Every behavior that increases resistance must be listed:
- Talks >30sec without asking
- Ignores concerns
- Uses pushy language
- Mentions price before value
- Interrupts
- Generic pitch

**Why:** These define what makes the persona challenging

### 2. All Rapport Triggers

Every behavior that decreases resistance must be listed:
- Asks about situation
- Acknowledges concerns first
- Shares specific benefits
- Provides data
- References what persona said
- Shows empathy

**Why:** These define what user must do to succeed

### 3. Response Behavior Patterns

For each resistance level, preserve:
- Response type distribution (MOSTLY/OFTEN/SOMETIMES/RARELY)
- Example responses
- Pause duration
- Tone/attitude

**Why:** These define how persona acts at each level

### 4. Anti-Validation Rules

Preserve all forbidden behaviors:
- Don't validate
- Don't do their job
- Don't volunteer info
- Don't make it easy

**Why:** Without these, persona becomes too helpful

### 5. Strategic Silence Timing

Preserve pause durations for each level:
- Highly Resistant: 6-8 sec
- Neutral: 3-5 sec
- Cautiously Interested: 2-3 sec
- Ready to Close: 1-2 sec

**Why:** Silence creates discomfort that forces user to carry conversation

### 6. Bidirectional Dynamics

Preserve the asymmetry:
- "One mistake undoes multiple good moves"
- "Trust earned slowly, lost quickly"

**Why:** This is what makes resistance realistic

## Length Testing Methodology

### Step 1: Identify Worst-Case Scenario

Determine the longest possible prompt by combining:
- Longest persona archetype description
- Highest difficulty level (most challenging)
- Most complex practice mode
- Maximum script content length (e.g., 1000 chars)

**Example for door-to-door sales:**
- Archetype: Owl (analytical, detail-oriented) = 150 chars
- Difficulty: Nightmare (very difficult) = 100 chars
- Mode: Random Objection = 50 chars
- Script: 1000 chars
- **Total variable content:** 1300 chars

### Step 2: Calculate Base Prompt Length

Measure the length of your resistance-rapport framework + anti-validation + flow rules:

```python
base_prompt = """
[Your complete prompt template here]
"""
base_length = len(base_prompt)
```

### Step 3: Calculate Worst-Case Total

```python
worst_case_length = base_length + 1300  # variable content
```

### Step 4: Compare to Limit

```python
api_limit = 4000  # Hume AI limit
remaining_space = api_limit - worst_case_length

if remaining_space < 0:
    print(f"Over limit by {abs(remaining_space)} characters - must condense")
elif remaining_space < 200:
    print(f"Only {remaining_space} chars remaining - risky, consider condensing")
else:
    print(f"Within limit with {remaining_space} chars to spare")
```

### Step 5: Iteratively Condense

If over limit:
1. Apply condensing techniques (start with #1, #2, #3)
2. Re-measure
3. If still over, apply more techniques (#4, #5, #6)
4. Re-measure
5. Repeat until within limit with 100+ chars remaining

### Step 6: Validate with Script

Use the provided validation script:

```bash
python /home/ubuntu/skills/realistic-ai-persona-builder/scripts/validate_prompt_length.py "$worst_case_prompt" 4000
```

## Real-World Example: Door-to-Door Sales Persona

**Initial prompt:** 5110 characters (worst-case)  
**API limit:** 4000 characters  
**Over by:** 1110 characters

**Condensing process:**

1. **Applied abbreviations** (seconds → sec, versus → vs)
   - Saved: ~200 characters
   - New total: 4910 characters

2. **Removed redundant examples** (kept 2-3 per section)
   - Saved: ~300 characters
   - New total: 4610 characters

3. **Combined resistance/rapport sections**
   - Saved: ~150 characters
   - New total: 4460 characters

4. **Used descriptive distributions** (MOSTLY/OFTEN vs percentages)
   - Saved: ~250 characters
   - New total: 4210 characters

5. **Condensed flow rules** (removed explanations)
   - Saved: ~200 characters
   - New total: 4010 characters

6. **Removed meta-commentary**
   - Saved: ~150 characters
   - **Final total: 3860 characters**

**Result:** Within limit with 140 characters remaining ✅

## Common Mistakes

**Mistake 1: Condensing Mechanics Instead of Examples**
- ❌ Remove resistance triggers to save space
- ✅ Remove redundant examples of triggers

**Mistake 2: Removing Anti-Validation Rules**
- ❌ "We can add these back later if needed"
- ✅ These are CRITICAL - condense elsewhere

**Mistake 3: Not Testing Worst-Case**
- ❌ Test with average inputs
- ✅ Test with longest possible inputs

**Mistake 4: Over-Condensing**
- ❌ Make prompt so terse it's unclear
- ✅ Preserve clarity while condensing

## Summary

Prompt optimization is about condensing examples and explanations while preserving all critical mechanics. Use abbreviations, remove redundancy, combine sections, and use descriptive language instead of numbers. Always test worst-case scenarios and maintain 100+ characters of buffer space.

**Key principle:** Condense the HOW, preserve the WHAT.
