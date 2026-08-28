# Testing Methodology

Comprehensive testing ensures realistic AI personas behave as designed across all scenarios. This methodology is based on the 16-test suite developed for the door-to-door sales homeowner persona.

## Test Categories

### Category 1: System Prompt Generation

**Purpose:** Verify prompt structure and completeness

**Tests:**
1. Resistance-rapport dynamics section present
2. All 4 resistance levels with behaviors defined
3. Anti-validation rules present and explicit
4. Strategic silence timing for each resistance level
5. Resistance triggers (mistakes) listed
6. Resistance reducers (rapport-building) listed
7. Bidirectional resistance dynamics emphasized
8. Response type examples included

**Example test:**

```typescript
it('should include resistance-rapport dynamics section', () => {
  const prompt = generateSystemPrompt({
    voiceGender: 'male',
    archetype: 'lamb',
    difficulty: 'rookie',
    practiceMode: 'full_pitch',
    scriptContent: '',
    roleplayMode: 'standard',
  });

  expect(prompt).toContain('RESISTANCE DYNAMICS');
  expect(prompt).toContain('Get MORE resistant when rep');
  expect(prompt).toContain('SOFTEN when rep');
});
```

### Category 2: Anti-Validation Safeguards

**Purpose:** Verify persona won't validate or help user

**Tests:**
9. Anti-validation rules explicitly stated
10. Forbidden behaviors listed with examples
11. Replacement behaviors provided for high engagement

**Example test:**

```typescript
it('should explicitly forbid validation behaviors', () => {
  const prompt = generateSystemPrompt({
    voiceGender: 'female',
    archetype: 'owl',
    difficulty: 'nightmare',
    practiceMode: 'objection_handling',
    scriptContent: '',
    roleplayMode: 'standard',
  });

  expect(prompt).toContain('NEVER validate');
  expect(prompt).toContain('Don\'t say "You\'re right!"');
  expect(prompt).toContain('"Makes sense!"');
});
```

### Category 3: Strategic Silence System

**Purpose:** Verify pause timing varies by resistance level

**Tests:**
12. Different pause lengths for each resistance level
13. Silence handling instructions (what to do after 4+ seconds)

**Example test:**

```typescript
it('should include strategic silence timing for each resistance level', () => {
  const prompt = generateSystemPrompt({
    voiceGender: 'male',
    archetype: 'owl',
    difficulty: 'nightmare',
    practiceMode: 'full_pitch',
    scriptContent: '',
    roleplayMode: 'standard',
  });

  expect(prompt).toContain('Pause 6-8 sec'); // High resistance
  expect(prompt).toContain('Pause 3-5 sec'); // Neutral
  expect(prompt).toContain('Pause 2-3 sec'); // Cautiously interested
  expect(prompt).toContain('Pause 1-2 sec'); // Ready to close
});
```

### Category 4: Response Type Distribution

**Purpose:** Verify response behaviors match resistance levels

**Tests:**
14. Response type examples for each level
15. Descriptive distributions (MOSTLY/OFTEN/SOMETIMES/RARELY)

**Example test:**

```typescript
it('should include response type examples', () => {
  const prompt = generateSystemPrompt({
    voiceGender: 'male',
    archetype: 'lamb',
    difficulty: 'rookie',
    practiceMode: 'full_pitch',
    scriptContent: '',
    roleplayMode: 'standard',
  });

  // Type A examples (ultra-minimal)
  expect(prompt).toContain('Not interested');
  expect(prompt).toContain('Maybe');
  expect(prompt).toContain('I\'m busy');

  // Type B examples (short/guarded)
  expect(prompt).toContain('Why switch?');
  expect(prompt).toContain('What\'s the catch?');

  // Type C examples (engaged)
  expect(prompt).toContain('Tell me about the speed');
});
```

### Category 5: Prompt Length Validation

**Purpose:** Ensure prompt fits within API limits

**Test:**
16. Worst-case scenario within character limit

**Example test:**

```typescript
it('should be within Hume API character limit', () => {
  // Worst-case: longest archetype + difficulty + mode + max script
  const prompt = generateSystemPrompt({
    voiceGender: 'male',
    archetype: 'owl', // Longest description
    difficulty: 'nightmare', // Longest description
    practiceMode: 'random_objection', // Longest description
    scriptContent: 'A'.repeat(1000), // Max script length
    roleplayMode: 'standard',
  });

  const HUME_API_LIMIT = 4000;
  expect(prompt.length).toBeLessThan(HUME_API_LIMIT);
  
  // Should have buffer space
  const remaining = HUME_API_LIMIT - prompt.length;
  expect(remaining).toBeGreaterThan(100);
});
```

## Test Patterns

### Pattern 1: Structure Verification

**When to use:** Verifying sections exist in prompt

**Pattern:**
```typescript
expect(prompt).toContain('SECTION_NAME');
expect(prompt).toContain('key phrase from section');
```

**Why:** Ensures prompt has required structure

### Pattern 2: Content Verification

**When to use:** Verifying specific content is present

**Pattern:**
```typescript
expect(prompt).toContain('exact text that must appear');
```

**Why:** Ensures critical instructions aren't lost during condensing

### Pattern 3: Length Verification

**When to use:** Verifying prompt fits within limits

**Pattern:**
```typescript
expect(prompt.length).toBeLessThan(MAX_LENGTH);
expect(MAX_LENGTH - prompt.length).toBeGreaterThan(BUFFER);
```

**Why:** Prevents runtime errors from exceeding API limits

### Pattern 4: Conditional Verification

**When to use:** Verifying behavior changes based on inputs

**Pattern:**
```typescript
const promptA = generateSystemPrompt({ archetype: 'lamb' });
const promptB = generateSystemPrompt({ archetype: 'owl' });

expect(promptA).toContain('friendly and agreeable');
expect(promptB).toContain('analytical and detail-oriented');
```

**Why:** Ensures persona characteristics are preserved

## Complete Test Suite Example

Based on door-to-door sales homeowner persona (16 tests):

```typescript
describe('Realistic Homeowner Behavior System', () => {
  describe('System Prompt Generation', () => {
    it('should include resistance-rapport dynamics section', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'lamb',
        difficulty: 'rookie',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('RESISTANCE DYNAMICS');
      expect(prompt).toContain('Get MORE resistant when rep');
      expect(prompt).toContain('SOFTEN when rep');
    });

    it('should include all 4 resistance levels with behaviors', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'lamb',
        difficulty: 'rookie',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('HIGHLY RESISTANT');
      expect(prompt).toContain('NEUTRAL');
      expect(prompt).toContain('CAUTIOUSLY INTERESTED');
      expect(prompt).toContain('READY TO CLOSE');
    });

    it('should include anti-validation rules', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'lamb',
        difficulty: 'rookie',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('ANTI-VALIDATION (CRITICAL)');
      expect(prompt).toContain('NEVER');
      expect(prompt).toContain('Validate pitch');
      expect(prompt).toContain('Do their job');
      expect(prompt).toContain('Make them EARN close');
    });

    it('should include strategic silence timing for each resistance level', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'owl',
        difficulty: 'nightmare',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('Pause 6-8 sec');
      expect(prompt).toContain('Pause 3-5 sec');
      expect(prompt).toContain('Pause 2-3 sec');
      expect(prompt).toContain('Pause 1-2 sec');
    });

    it('should include resistance triggers (mistakes)', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'female',
        archetype: 'lion',
        difficulty: 'advanced',
        practiceMode: 'objection_handling',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('talks >30sec');
      expect(prompt).toContain('ignores');
      expect(prompt).toContain('pushy');
      expect(prompt).toContain('interrupts');
    });

    it('should include resistance reducers (rapport-building)', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'lamb',
        difficulty: 'intermediate',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('asks about YOUR situation');
      expect(prompt).toContain('acknowledges concerns');
      expect(prompt).toContain('specific benefits');
      expect(prompt).toContain('empathy');
    });

    it('should emphasize bidirectional resistance dynamics', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'female',
        archetype: 'owl',
        difficulty: 'expert',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('One mistake undoes multiple good moves');
      expect(prompt).toContain('Trust earned slowly, lost quickly');
    });

    it('should include response type examples', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'lamb',
        difficulty: 'rookie',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('Not interested');
      expect(prompt).toContain('Maybe');
      expect(prompt).toContain('I\'m busy');
      expect(prompt).toContain('Why switch?');
      expect(prompt).toContain('What\'s the catch?');
      expect(prompt).toContain('Tell me about the speed');
    });
  });

  describe('Anti-Validation Safeguards', () => {
    it('should explicitly forbid validation behaviors', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'female',
        archetype: 'owl',
        difficulty: 'nightmare',
        practiceMode: 'objection_handling',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('NEVER validate');
      expect(prompt).toContain('Don\'t say "You\'re right!"');
      expect(prompt).toContain('"Makes sense!"');
    });

    it('should provide replacement behaviors for high engagement', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'lamb',
        difficulty: 'rookie',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('Ask practical questions');
      expect(prompt).toContain('Raise concerns');
      expect(prompt).toContain('Make them EARN close');
    });
  });

  describe('Strategic Silence System', () => {
    it('should include different pause lengths for resistance levels', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'owl',
        difficulty: 'nightmare',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('6-8 sec');
      expect(prompt).toContain('3-5 sec');
      expect(prompt).toContain('2-3 sec');
      expect(prompt).toContain('1-2 sec');
    });

    it('should include silence handling instructions', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'female',
        archetype: 'lamb',
        difficulty: 'intermediate',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('silence >4sec');
      expect(prompt).toContain('"So...?"');
      expect(prompt).toContain('"That it?"');
    });
  });

  describe('Response Type Distribution', () => {
    it('should use descriptive distributions', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'lion',
        difficulty: 'advanced',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(prompt).toContain('MOSTLY');
      expect(prompt).toContain('OFTEN');
      expect(prompt).toContain('SOMETIMES');
      expect(prompt).toContain('RARELY');
    });
  });

  describe('Prompt Length Validation', () => {
    it('should be within Hume API character limit', () => {
      const prompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'owl',
        difficulty: 'nightmare',
        practiceMode: 'random_objection',
        scriptContent: 'A'.repeat(1000),
        roleplayMode: 'standard',
      });

      const HUME_API_LIMIT = 4000;
      expect(prompt.length).toBeLessThan(HUME_API_LIMIT);
      
      const remaining = HUME_API_LIMIT - prompt.length;
      expect(remaining).toBeGreaterThan(100);
    });

    it('should preserve persona characteristics', () => {
      const lambPrompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'lamb',
        difficulty: 'rookie',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      const owlPrompt = generateSystemPrompt({
        voiceGender: 'male',
        archetype: 'owl',
        difficulty: 'nightmare',
        practiceMode: 'full_pitch',
        scriptContent: '',
        roleplayMode: 'standard',
      });

      expect(lambPrompt).toContain('friendly');
      expect(owlPrompt).toContain('analytical');
    });
  });
});
```

**Results:** 16/16 tests passing ✅

## What Breaks If Tests Fail

| Test | What Breaks | Impact |
|------|-------------|--------|
| Resistance dynamics missing | Persona doesn't respond to user performance | No training value |
| Resistance levels undefined | Persona behavior is inconsistent | Unpredictable experience |
| Anti-validation missing | Persona becomes too helpful | Defeats purpose |
| Silence timing wrong | Uncomfortable pauses don't work | Less realistic |
| Resistance triggers missing | Persona doesn't get harder when user fails | Too easy |
| Rapport triggers missing | Persona doesn't soften when user succeeds | Too hard |
| Bidirectional dynamics missing | Resistance changes unrealistically | Feels artificial |
| Response examples missing | Persona responses are generic | Less realistic |
| Validation forbidden missing | Persona validates user | Training value lost |
| Replacement behaviors missing | No guidance for high engagement | Persona too helpful |
| Pause lengths missing | All pauses same duration | Less realistic |
| Silence handling missing | Persona doesn't prompt after long silence | Awkward dead air |
| Distributions missing | Response types unclear | Inconsistent behavior |
| Prompt over limit | API rejects prompt | Runtime error |
| Persona characteristics missing | All personas sound the same | No variety |

## Testing During Development

**Test-Driven Development Flow:**

1. **Write failing test** - Define expected behavior
2. **Run test** - Verify it fails (prompt doesn't have feature yet)
3. **Implement feature** - Add to prompt template
4. **Run test** - Verify it passes
5. **Refactor** - Condense if needed, re-run tests
6. **Commit** - Save working version

**Example:**

```bash
# Step 1: Write test for anti-validation
# Step 2: Run test
pnpm test realistic-homeowner.test.ts
# Expected: FAIL - "NEVER validate" not found

# Step 3: Add anti-validation section to prompt
# Step 4: Run test again
pnpm test realistic-homeowner.test.ts
# Expected: PASS

# Step 5: Condense prompt, run tests again
pnpm test realistic-homeowner.test.ts
# Expected: Still PASS
```

## Summary

Comprehensive testing ensures realistic AI personas behave as designed. Use 16-test suite as template: 8 tests for structure, 2 for anti-validation, 2 for silence, 2 for distributions, 2 for length/characteristics. Test-driven development prevents regressions during prompt optimization.

**Key principle:** If it's not tested, it will break during condensing.
