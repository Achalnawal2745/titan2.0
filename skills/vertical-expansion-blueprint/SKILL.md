---
name: "vertical-expansion-blueprint"
description: "Specialized skill for vertical expansion blueprint workflows and automation."
---

# Vertical Expansion Blueprint

## Overview

This skill provides a **proven blueprint** for adapting the FLEXX FIBER sales roleplay platform to **any vertical industry** where roleplay training is valuable:

- 🎯 **Sales Training** (door-to-door, B2B, retail)
- 💕 **Dating/Social Skills Coaching**
- 🧠 **Therapy/Counseling Training**
- 📞 **Customer Service Training**
- 🏥 **Medical Simulation** (doctor-patient)
- 💼 **Interview Preparation**
- 🎭 **Any scenario-based training**

**Value Proposition:** Reduces vertical deployment from **$50k-100k custom builds** to **$5k-10k config-driven adaptations** (90% time savings).

---

## What You Get

1. **Architecture Analysis** - Deep dive into the 10 reusable components
2. **Config Schema** - TypeScript interface defining all customization points
3. **3 Complete Examples** - Sales (FLEXX FIBER), Dating Coach, Therapy Training
4. **Cloning Guide** - Step-by-step instructions for adaptation
5. **Adaptation Checklist** - File-by-file modification guide

---

## The 10 Reusable Components

Only **10% of the platform changes per vertical**. Here's what stays the same vs. what you customize:

### Stays the Same (90%)
- Database schema (5 tables: users, sessions, scripts, rep_codes, manager_assignments)
- Frontend pages (Practice, History, Analytics, Scripts, Profile)
- Voice integration layer (Hume AI WebSocket)
- AI coaching feedback engine
- Progress tracking system
- Authentication & user management

### Changes Per Vertical (10%)
1. **Domain Config** - Trainee role, AI role, goal
2. **4 AI Personas** - Personality types with examples
3. **5-7 Practice Modes** - Focused training scenarios
4. **Coaching Prompt** - Post-session feedback template
5. **Branding** - Colors, logo, terminology

---

## Quick Start: 3-Step Process

### Step 1: Choose Your Vertical Config

Review the 3 example configs in `configs/`:

- `sales-fiber-door-to-door.json` - Door-to-door sales (FLEXX FIBER)
- `dating-coach-training.json` - Social skills and dating
- `therapy-training-relationships.json` - Couples therapy training

**Or create your own** by copying one of these and modifying the 10 components.

### Step 2: Clone the FLEXX FIBER Platform

```bash
# Clone the sales roleplay dashboard project
cd /home/ubuntu
cp -r sales-roleplay-dashboard my-new-vertical-platform
cd my-new-vertical-platform
```

### Step 3: Apply Your Config

Follow the **Adaptation Checklist** (see `references/adaptation-checklist.md`) to modify:

1. `server/hume-service.ts` - AI prompt generation
2. `client/src/pages/Practice.tsx` - Practice mode UI
3. `client/src/index.css` - Branding colors
4. `client/public/` - Logo files
5. `drizzle/schema.ts` - Terminology (optional)

---

## Detailed Cloning Guide

### Phase 1: Setup (15 min)

1. **Clone the base platform**
   ```bash
   cp -r /home/ubuntu/sales-roleplay-dashboard /home/ubuntu/my-vertical-platform
   cd /home/ubuntu/my-vertical-platform
   ```

2. **Update project metadata**
   - Edit `package.json` - Change name, description
   - Edit `README.md` - Update title and description

3. **Install dependencies**
   ```bash
   pnpm install
   ```

### Phase 2: Domain Configuration (30 min)

4. **Update `server/hume-service.ts`**
   - Line 50-60: Update `domain` object with your config
   - Line 70-120: Replace `archetypeDescriptions` with your personas
   - Line 125-145: Replace `archetypeExamples` with your examples
   - Line 150-170: Replace `difficultyModifiers` with your difficulty levels
   - Line 175-195: Replace `modeInstructions` with your practice modes

5. **Update `client/src/pages/Practice.tsx`**
   - Line 26: Update archetype options
   - Line 27: Update difficulty options
   - Line 28: Update practice mode options
   - Line 250-350: Update Select dropdowns with your terminology

### Phase 3: Branding (20 min)

6. **Update `client/src/index.css`**
   - Line 10-30: Replace CSS variables with your brand colors
   - Use your config's `branding.primaryColor`, `backgroundColor`, etc.

7. **Replace logo files**
   ```bash
   cp /path/to/your-logo.png client/public/your-logo.png
   ```
   - Update `client/src/components/BrandHeader.tsx` - Line 15: Logo path
   - Update `client/src/components/BrandHeader.tsx` - Line 18: Company name

8. **Update terminology throughout**
   - Find/replace "sales rep" → your `traineeRole`
   - Find/replace "homeowner" → your `aiRole`
   - Find/replace "practice session" → your terminology

### Phase 4: Coaching Prompts (15 min)

9. **Update `server/routers.ts` or create `server/coaching-service.ts`**
   - Find the coaching feedback generation logic
   - Replace system prompt with your `coachingPrompt.systemPrompt`
   - Update user prompt template with your `coachingPrompt.userPromptTemplate`

### Phase 5: Testing (30 min)

10. **Test TypeScript compilation**
    ```bash
    pnpm exec tsc --noEmit
    ```

11. **Start dev server**
    ```bash
    pnpm dev
    ```

12. **Test each persona + difficulty combination**
    - Start practice session for each archetype
    - Verify AI behavior matches your config
    - Check coaching feedback quality

13. **Test all practice modes**
    - Verify mode-specific instructions work correctly

### Phase 6: Deployment (15 min)

14. **Update environment variables**
    - Set `VITE_APP_TITLE` to your platform name
    - Set `VITE_APP_LOGO` to your logo URL

15. **Save checkpoint**
    ```bash
    # Use webdev_save_checkpoint tool
    ```

16. **Publish**
    - Click Publish button in Manus UI

---

## Config Schema Reference

See `references/vertical-config-schema.ts` for the complete TypeScript interface.

**Key sections:**
- `metadata` - ID, name, industry
- `domain` - Trainee role, AI role, goal, context
- `personas` - 4 personality types with examples
- `difficultyLevels` - 5 levels with behavior patterns
- `practiceModes` - 5-7 focused scenarios
- `coachingPrompt` - Feedback generation template
- `branding` - Colors, logo, terminology
- `features` - Phone support, replay, streaks, leaderboards

---

## Example Configs

### 1. Sales Training (FLEXX FIBER)
**File:** `configs/sales-fiber-door-to-door.json`

- **Domain:** Sales rep → Homeowner
- **Personas:** Lamb, Bull, Tiger, Owl
- **Modes:** Full Pitch, Opener Only, Discovery, Value Prop, Random Objections
- **Features:** Phone support, leaderboards, manager dashboard

### 2. Dating Coach Training
**File:** `configs/dating-coach-training.json`

- **Domain:** Man approaching → Woman being approached
- **Personas:** Social Butterfly, Ice Queen, Intellectual, Busy Professional
- **Modes:** Cold Approach, Conversation Flow, Flirtation, Number Close, Rejection Recovery
- **Features:** Session replay, practice streaks, leaderboards

### 3. Therapy Training
**File:** `configs/therapy-training-relationships.json`

- **Domain:** Therapist → Client
- **Personas:** Anxious Avoider, Angry Blamer, Passive Victim, Logical Rationalizer
- **Modes:** Initial Intake, Active Listening, Probing Questions, Reframing, Crisis Management
- **Features:** Session replay, practice streaks, supervisor dashboard

---

## Architecture Deep Dive

See `references/vertical-roleplay-architecture-analysis.md` for complete analysis.

**Key insights:**
- 10 reusable components identified
- 90% code reuse across verticals
- Config-driven customization reduces dev time by 90%
- Business model: $10k setup + $500/mo per vertical

---

## Best Practices

### Persona Design
- **4 personas is optimal** - Covers personality spectrum without overwhelming users
- **Include concrete examples** - "Show, don't tell" for AI behavior
- **Objection styles matter** - Define how each persona resists

### Difficulty Calibration
- **Use explicit metrics** - Turn counts, pause lengths, response rates
- **Avoid vague descriptions** - "Quite challenging" → "4-5 objections, 3-4 sec pauses"
- **Test across all levels** - Ensure rookie is actually easy, nightmare is actually hard

### Practice Modes
- **5-7 modes is optimal** - Covers key skills without fragmentation
- **Mode-specific instructions** - Tell AI exactly how to behave in each mode
- **Progressive complexity** - Order modes from basic to advanced

### Coaching Prompts
- **Domain-specific feedback** - Reference industry best practices
- **Actionable advice** - "Do X next time" not "You did Y wrong"
- **Encouraging tone** - Balance critique with recognition

---

## Troubleshooting

### AI forgets its role
**Problem:** AI thinks it's the trainee instead of the persona  
**Solution:** Add role reminders throughout prompt (see hume-service.ts line 200-250)

### Difficulty levels feel the same
**Problem:** Vague difficulty descriptions  
**Solution:** Use explicit behavioral metrics (turn counts, pause lengths, objection counts)

### Objections feel random/unnatural
**Problem:** "Unexpected moments" is too vague  
**Solution:** Specify exact turns for objections (turn 3-4, 7-9, 12-15)

### Persona loses personality mid-conversation
**Problem:** Personality described but not demonstrated  
**Solution:** Add 4 concrete response examples per persona

---

## Next Steps

1. **Review the 3 example configs** - Understand the pattern
2. **Choose your vertical** - Or create a new one
3. **Follow the cloning guide** - Step-by-step adaptation
4. **Test thoroughly** - All personas × difficulties × modes
5. **Deploy and iterate** - Gather user feedback and refine

---

## Support

For questions or issues:
- Review `references/vertical-roleplay-architecture-analysis.md` for deep technical details
- Check `references/vertical-roleplay-skill-requirements-analysis.md` for common gaps
- Consult the original FLEXX FIBER dashboard for working examples

---

## Business Model

**Traditional Custom Build:** $50k-100k, 3-6 months  
**Config-Driven Adaptation:** $5k-10k, 2-4 weeks

**Recurring Revenue:** $500/mo per vertical for hosting + support

**Scalability:** 10 verticals = $5k/mo recurring, 100 verticals = $50k/mo recurring

---

## License

This blueprint is based on the FLEXX FIBER sales roleplay dashboard. Adapt freely for your vertical industries.
