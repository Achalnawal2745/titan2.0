# File-by-File Adaptation Checklist

This checklist provides exact file paths and line numbers for adapting the FLEXX FIBER platform to a new vertical.

---

## Phase 1: Setup

### ✅ 1. Clone Base Platform
```bash
cp -r /home/ubuntu/sales-roleplay-dashboard /home/ubuntu/my-vertical-platform
cd /home/ubuntu/my-vertical-platform
```

### ✅ 2. Update `package.json`
- **Line 2:** Change `"name"` to your platform name (lowercase-with-hyphens)
- **Line 3:** Change `"description"` to your platform description

### ✅ 3. Update `README.md`
- **Line 1:** Change title to your platform name
- **Line 3-10:** Update description and overview

---

## Phase 2: Domain Configuration

### ✅ 4. Update `server/hume-service.ts`

**Domain Config (Lines 50-60)**
```typescript
const { archetype, difficulty, practiceMode, scriptContent, roleplayMode = "standard" } = params;

// Replace these values with your config
domain: {
  traineeRole: "YOUR_TRAINEE_ROLE", // e.g., "therapist", "man approaching"
  aiRole: "YOUR_AI_ROLE", // e.g., "client", "woman being approached"
  goal: "YOUR_GOAL", // e.g., "help client process emotions"
  context: "YOUR_CONTEXT", // e.g., "You're in a therapy session..."
  roleReminder: "YOUR_ROLE_REMINDER" // e.g., "You are the client seeking help, NOT providing therapy."
}
```

**Archetype Descriptions (Lines 70-120)**
```typescript
const archetypeDescriptions = {
  persona1_id: "PERSONA 1 PERSONALITY DESCRIPTION",
  persona2_id: "PERSONA 2 PERSONALITY DESCRIPTION",
  persona3_id: "PERSONA 3 PERSONALITY DESCRIPTION",
  persona4_id: "PERSONA 4 PERSONALITY DESCRIPTION",
};
```

**Archetype Examples (Lines 125-145)**
```typescript
const archetypeExamples = {
  persona1_id: {
    responses: [
      "EXAMPLE RESPONSE 1",
      "EXAMPLE RESPONSE 2",
      "EXAMPLE RESPONSE 3",
      "EXAMPLE RESPONSE 4",
    ],
    objectionStyle: "HOW THIS PERSONA OBJECTS",
  },
  // ... repeat for all 4 personas
};
```

**Difficulty Modifiers (Lines 150-170)**
```typescript
const difficultyModifiers = {
  rookie: "ROOKIE BEHAVIOR PATTERN",
  intermediate: "INTERMEDIATE BEHAVIOR PATTERN",
  advanced: "ADVANCED BEHAVIOR PATTERN",
  expert: "EXPERT BEHAVIOR PATTERN",
  nightmare: "NIGHTMARE BEHAVIOR PATTERN",
};
```

**Mode Instructions (Lines 175-195)**
```typescript
const modeInstructions = {
  mode1_id: "MODE 1 INSTRUCTIONS",
  mode2_id: "MODE 2 INSTRUCTIONS",
  mode3_id: "MODE 3 INSTRUCTIONS",
  mode4_id: "MODE 4 INSTRUCTIONS",
  mode5_id: "MODE 5 INSTRUCTIONS",
  // Add more modes as needed (5-7 recommended)
};
```

**System Prompt Template (Lines 200-250)**
- **Line 200:** Update role statement: `🏠 YOU ARE THE {{aiRole}}. The user is the {{traineeRole}} interacting with YOU.`
- **Line 210:** Update personality description
- **Line 230:** Update role reminder
- **Line 240:** Update context

---

### ✅ 5. Update `client/src/pages/Practice.tsx`

**State Declarations (Lines 26-28)**
```typescript
const [archetype, setArchetype] = useState<"persona1" | "persona2" | "persona3" | "persona4">("persona1");
const [difficulty, setDifficulty] = useState<"rookie" | "intermediate" | "advanced" | "expert" | "nightmare">("rookie");
const [practiceMode, setPracticeMode] = useState<"mode1" | "mode2" | "mode3" | "mode4" | "mode5">("mode1");
```

**Archetype Select Dropdown (Lines 250-280)**
```tsx
<Label htmlFor="archetype">YOUR_PERSONA_LABEL (e.g., "Personality Type", "Client Presentation")</Label>
<Select value={archetype} onValueChange={(value) => setArchetype(value as any)}>
  <SelectTrigger id="archetype">
    <SelectValue placeholder="Select YOUR_PERSONA_LABEL" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="persona1_id">PERSONA 1 NAME - DESCRIPTION</SelectItem>
    <SelectItem value="persona2_id">PERSONA 2 NAME - DESCRIPTION</SelectItem>
    <SelectItem value="persona3_id">PERSONA 3 NAME - DESCRIPTION</SelectItem>
    <SelectItem value="persona4_id">PERSONA 4 NAME - DESCRIPTION</SelectItem>
  </SelectContent>
</Select>
```

**Difficulty Select Dropdown (Lines 290-320)**
```tsx
<Label htmlFor="difficulty">YOUR_DIFFICULTY_LABEL (e.g., "Receptiveness Level", "Defensiveness Level")</Label>
<Select value={difficulty} onValueChange={(value) => setDifficulty(value as any)}>
  <SelectTrigger id="difficulty">
    <SelectValue placeholder="Select YOUR_DIFFICULTY_LABEL" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="rookie">ROOKIE LABEL - DESCRIPTION</SelectItem>
    <SelectItem value="intermediate">INTERMEDIATE LABEL - DESCRIPTION</SelectItem>
    <SelectItem value="advanced">ADVANCED LABEL - DESCRIPTION</SelectItem>
    <SelectItem value="expert">EXPERT LABEL - DESCRIPTION</SelectItem>
    <SelectItem value="nightmare">NIGHTMARE LABEL - DESCRIPTION</SelectItem>
  </SelectContent>
</Select>
```

**Practice Mode Select Dropdown (Lines 330-370)**
```tsx
<Label htmlFor="practiceMode">YOUR_MODE_LABEL (e.g., "Practice Scenario", "Session Focus")</Label>
<Select value={practiceMode} onValueChange={(value) => setPracticeMode(value as any)}>
  <SelectTrigger id="practiceMode">
    <SelectValue placeholder="Select YOUR_MODE_LABEL" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="mode1_id">MODE 1 NAME - DESCRIPTION</SelectItem>
    <SelectItem value="mode2_id">MODE 2 NAME - DESCRIPTION</SelectItem>
    <SelectItem value="mode3_id">MODE 3 NAME - DESCRIPTION</SelectItem>
    <SelectItem value="mode4_id">MODE 4 NAME - DESCRIPTION</SelectItem>
    <SelectItem value="mode5_id">MODE 5 NAME - DESCRIPTION</SelectItem>
    <!-- Add more modes as needed -->
  </SelectContent>
</Select>
```

---

## Phase 3: Branding

### ✅ 6. Update `client/src/index.css`

**CSS Variables (Lines 10-30)**
```css
:root {
  --background: YOUR_BACKGROUND_COLOR; /* e.g., #0a1628 for navy */
  --foreground: YOUR_FOREGROUND_COLOR; /* e.g., #f8fafc for light text */
  --primary: YOUR_PRIMARY_COLOR; /* e.g., #00d4ff for electric blue */
  --primary-foreground: YOUR_PRIMARY_FOREGROUND; /* e.g., #0a1628 for text on primary */
  --secondary: YOUR_SECONDARY_COLOR; /* e.g., #0ea5e9 */
  --accent: YOUR_ACCENT_COLOR; /* e.g., #3b82f6 */
  --border: YOUR_BORDER_COLOR; /* e.g., #1e293b */
  --card: YOUR_CARD_BACKGROUND; /* e.g., #1a2942 */
}
```

### ✅ 7. Replace Logo Files

**Copy your logo:**
```bash
cp /path/to/your-logo.png client/public/your-logo.png
```

**Update `client/src/components/BrandHeader.tsx`**
- **Line 15:** Change logo src: `<img src="/your-logo.png" alt="YOUR COMPANY NAME" />`
- **Line 18:** Change company name: `<span className="text-xl font-bold">YOUR COMPANY NAME</span>`
- **Line 19:** Change subtitle: `<span className="text-sm text-muted-foreground">YOUR SUBTITLE</span>`

### ✅ 8. Update Terminology Throughout

**Find/Replace across entire codebase:**
- "sales rep" → YOUR_TRAINEE_ROLE
- "sales representative" → YOUR_TRAINEE_ROLE
- "homeowner" → YOUR_AI_ROLE
- "practice session" → YOUR_SESSION_TERM
- "archetype" → YOUR_PERSONA_TERM (optional)
- "difficulty" → YOUR_DIFFICULTY_TERM (optional)

**Key files to check:**
- `client/src/pages/Practice.tsx`
- `client/src/pages/History.tsx`
- `client/src/pages/Analytics.tsx`
- `client/src/components/VoiceCall.tsx`

---

## Phase 4: Coaching Prompts

### ✅ 9. Update Coaching Feedback Generation

**Find coaching logic in `server/routers.ts` or `server/practice-router.ts`**

Search for: `generateCoaching` or `coaching feedback` or `invokeLLM`

**Update system prompt:**
```typescript
const systemPrompt = `You are an expert YOUR_DOMAIN coach analyzing a YOUR_SESSION_TYPE. Provide constructive feedback focusing on: 1) YOUR_SKILL_1, 2) YOUR_SKILL_2, 3) YOUR_SKILL_3, 4) YOUR_SKILL_4, 5) YOUR_SKILL_5. Be specific, actionable, and encouraging.`;
```

**Update user prompt template:**
```typescript
const userPrompt = `Analyze this YOUR_SESSION_TYPE and provide coaching feedback:

YOUR_PERSONA_LABEL: ${archetype}
YOUR_DIFFICULTY_LABEL: ${difficulty}
YOUR_MODE_LABEL: ${practiceMode}

Transcript:
${transcript}

Provide specific, actionable coaching feedback.`;
```

---

## Phase 5: Optional Schema Updates

### ✅ 10. Update `drizzle/schema.ts` (Optional)

**Only if you want to change terminology in database:**

- **Line 50:** `repCode` column → rename if needed
- **Line 80:** `archetype` column → rename if needed
- **Line 81:** `difficulty` column → rename if needed
- **Line 82:** `practiceMode` column → rename if needed

**After changes, run:**
```bash
pnpm db:push
```

---

## Phase 6: Testing

### ✅ 11. TypeScript Compilation
```bash
pnpm exec tsc --noEmit
```
**Expected:** No errors

### ✅ 12. Start Dev Server
```bash
pnpm dev
```
**Expected:** Server starts on port 3000

### ✅ 13. Test Each Persona
- [ ] Persona 1 at Rookie difficulty
- [ ] Persona 2 at Intermediate difficulty
- [ ] Persona 3 at Advanced difficulty
- [ ] Persona 4 at Expert difficulty
- [ ] Random persona at Nightmare difficulty

**Verify:** AI behavior matches your config

### ✅ 14. Test Each Practice Mode
- [ ] Mode 1
- [ ] Mode 2
- [ ] Mode 3
- [ ] Mode 4
- [ ] Mode 5
- [ ] Additional modes (if any)

**Verify:** Mode-specific instructions work correctly

### ✅ 15. Test Coaching Feedback
- [ ] Complete a session
- [ ] Generate coaching feedback
- [ ] Verify feedback is domain-specific and actionable

---

## Phase 7: Deployment

### ✅ 16. Update Environment Variables

**Use `webdev_request_secrets` tool:**
```typescript
await webdev_request_secrets({
  secrets: [
    {
      key: "VITE_APP_TITLE",
      value: "YOUR PLATFORM NAME",
      description: "Platform name shown in browser tab"
    },
    {
      key: "VITE_APP_LOGO",
      value: "/your-logo.png",
      description: "Path to platform logo"
    }
  ]
});
```

### ✅ 17. Save Checkpoint

**Use `webdev_save_checkpoint` tool:**
```typescript
await webdev_save_checkpoint({
  description: "YOUR VERTICAL NAME platform - initial deployment"
});
```

### ✅ 18. Publish

- Click **Publish** button in Manus UI
- Test published version
- Share with users

---

## Troubleshooting Checklist

### AI Behavior Issues
- [ ] Verified all persona descriptions are clear and distinct
- [ ] Added 4 concrete response examples per persona
- [ ] Specified explicit difficulty metrics (turn counts, pause lengths)
- [ ] Added role reminders throughout prompt

### UI Issues
- [ ] All Select dropdowns show correct options
- [ ] Terminology is consistent across all pages
- [ ] Branding colors applied correctly
- [ ] Logo displays properly

### TypeScript Errors
- [ ] All persona IDs match between hume-service.ts and Practice.tsx
- [ ] All difficulty levels match
- [ ] All practice modes match
- [ ] No typos in type definitions

### Coaching Feedback Issues
- [ ] System prompt is domain-specific
- [ ] User prompt template includes all relevant context
- [ ] Feedback is actionable and encouraging

---

## Final Checklist

- [ ] All 4 personas defined with examples
- [ ] All 5 difficulty levels defined with explicit metrics
- [ ] All 5-7 practice modes defined with instructions
- [ ] Coaching prompt updated for your domain
- [ ] Branding colors applied
- [ ] Logo replaced
- [ ] Terminology updated throughout
- [ ] TypeScript compiles without errors
- [ ] All personas tested
- [ ] All practice modes tested
- [ ] Coaching feedback tested
- [ ] Environment variables updated
- [ ] Checkpoint saved
- [ ] Published and tested

---

## Estimated Time

- **Phase 1 (Setup):** 15 minutes
- **Phase 2 (Domain Config):** 30 minutes
- **Phase 3 (Branding):** 20 minutes
- **Phase 4 (Coaching):** 15 minutes
- **Phase 5 (Schema - Optional):** 10 minutes
- **Phase 6 (Testing):** 30 minutes
- **Phase 7 (Deployment):** 15 minutes

**Total:** ~2 hours for complete adaptation

---

## Support

If you encounter issues:
1. Review the original FLEXX FIBER files for working examples
2. Check `references/vertical-config-schema.ts` for expected structure
3. Consult `references/vertical-roleplay-architecture-analysis.md` for architecture details
