# Vertical Roleplay Platform Architecture Analysis

## Source: FLEXX FIBER Sales Roleplay Dashboard

### Core Architecture Pattern

This analysis extracts the reusable skeleton architecture from the sales roleplay dashboard to enable rapid vertical expansion into ANY coaching/training industry.

---

## 1. Domain Configuration Layer

**What it is:** The industry-specific parameters that define the training context

**Sales Example:**
- **Domain:** Door-to-door fiber internet sales
- **Trainee Role:** Sales rep
- **AI Role:** Homeowner
- **Goal:** Close the sale / get appointment

**Pickup Artist Example:**
- **Domain:** Social dating scenarios
- **Trainee Role:** Person approaching
- **AI Role:** Potential romantic interest
- **Goal:** Get phone number / plan date

**Therapy Example:**
- **Domain:** Relationship counseling
- **Trainee Role:** Therapist
- **AI Role:** Client with relationship issues
- **Goal:** Build rapport / identify core issues

---

## 2. AI Persona System

**What it is:** Distinct personality archetypes that create varied training scenarios

**Sales (Current):**
- Lamb: Friendly, trusting, eager to listen
- Bull: Skeptical, direct, no-nonsense
- Tiger: Analytical, detail-oriented, cautious
- Owl: Methodical, slow decision maker

**Pickup Artist (Potential):**
- Social Butterfly: Outgoing, flirty, loves attention
- Ice Queen: Guarded, tests confidence, high standards
- Intellectual: Values deep conversation, hates superficiality
- Busy Professional: Time-conscious, direct, no games

**Therapy (Potential):**
- Anxious Avoider: Deflects, changes subject, fears vulnerability
- Angry Blamer: Defensive, projects fault, emotionally reactive
- Passive Victim: Helpless mindset, seeks validation, low agency
- Logical Rationalizer: Intellectualizes emotions, avoids feelings

**Pattern:** 4 archetypes per vertical, each requiring different approach strategies

---

## 3. Difficulty Progression System

**What it is:** Graduated challenge levels that scale with trainee skill

**Current Implementation (5 levels):**
1. **Rookie:** Easy, minimal objections, ready to close quickly
2. **Intermediate:** Moderate challenges, requires persuasion
3. **Advanced:** Challenging objections, requires skill
4. **Expert:** Very difficult, high standards, tests knowledge
5. **Nightmare:** Extremely hostile, masterful handling required

**Key Mechanics:**
- Turn count to close (Rookie: 5-7, Nightmare: 20+)
- Objection count (Rookie: 1-2, Nightmare: 7-10)
- Pause lengths (Rookie: 1-2 sec, Nightmare: 5-8 sec)
- Minimal response rate (Rookie: 20%, Nightmare: 80%)

**Pattern:** Difficulty = explicit behavioral parameters, not vague descriptions

---

## 4. Practice Mode System

**What it is:** Focused training scenarios that isolate specific skills

**Sales (Current):**
- Full Pitch: Complete conversation from greeting to close
- Opener Only: First 30 seconds, door opening
- Discovery: Qualification phase, asking questions
- Value Prop: Evaluating benefits and ROI
- Random Objection: Advanced mode with timed interruptions

**Pickup Artist (Potential):**
- Cold Approach: Initial opener and first impression
- Conversation Flow: Maintaining engaging dialogue
- Flirtation Calibration: Reading interest and escalating
- Number Close: Transitioning to contact exchange
- Rejection Recovery: Handling disinterest gracefully

**Therapy (Potential):**
- Initial Intake: Building rapport and trust
- Active Listening: Reflecting and validating
- Probing Questions: Uncovering root issues
- Reframing: Shifting perspective on problems
- Crisis Management: Handling emotional escalation

**Pattern:** 5-7 practice modes per vertical, each isolating a specific skill

---

## 5. AI Coaching Feedback System

**What it is:** Post-session analysis that provides actionable improvement guidance

**Current Implementation:**
- LLM analyzes full conversation transcript
- Generates structured feedback on strengths/weaknesses
- Provides specific improvement recommendations
- Scores session performance

**Universal Pattern:**
```
Input: Full conversation transcript + domain context
Process: LLM analysis with coaching prompt
Output: {
  strengths: ["What they did well"],
  weaknesses: ["What needs improvement"],
  recommendations: ["Specific next steps"],
  score: 0-100
}
```

**Pattern:** Domain-agnostic feedback engine, just swap coaching prompt

---

## 6. Progress Tracking System

**What it is:** Gamified metrics that motivate consistent practice

**Current Metrics:**
- Total sessions completed
- Average score
- Current difficulty level
- Archetype mastery (sessions per archetype)
- Practice mode completion
- Session history with transcripts

**Universal Metrics:**
- Session count
- Performance scores
- Difficulty progression
- Persona mastery
- Mode completion
- Streak tracking (future)

**Pattern:** Same tracking system works for any vertical

---

## 7. Voice Integration Layer

**What it is:** Real-time voice conversation with AI persona

**Current Stack:**
- Hume AI for emotional voice synthesis
- Twilio for phone call routing
- WebRTC for browser-based voice
- Real-time transcript capture

**Pattern:** Voice provider agnostic - swap Hume for ElevenLabs, Twilio for Vapi, etc.

---

## 8. Database Schema Pattern

**Core Tables (Universal):**

1. **users** - Trainees using the platform
2. **scripts** - Training content/methodology (optional per vertical)
3. **practiceSessions** - Individual training sessions
   - userId, archetype, difficulty, practiceMode, duration, score
4. **conversationTurns** - Full transcript of each session
   - sessionId, turnNumber, speaker, message, timestamp
5. **userProgress** - Aggregate metrics
   - totalSessions, averageScore, currentLevel, archetypeStats

**Pattern:** Same 5-table structure works for any vertical

---

## 9. Prompt Engineering Architecture

**What it is:** Structured system prompts that maintain AI persona consistency

**Key Components:**
1. **Role Definition:** "You are [AI role]. The user is [trainee role]."
2. **Personality Description:** Archetype traits
3. **Behavioral Examples:** 4 concrete response examples per archetype
4. **Difficulty Parameters:** Explicit turn counts, objection counts, pause lengths
5. **Practice Mode Instructions:** Specific focus for this session
6. **Resistance Dynamics:** When to soften/harden based on trainee behavior
7. **Role Reinforcement:** Multiple reminders throughout prompt

**Pattern:** Template-based prompt generation with domain-specific variables

---

## 10. Frontend UX Pattern

**Core Pages (Universal):**
1. **Practice** - Start new session (archetype + difficulty + mode selection)
2. **History** - View past sessions with transcripts
3. **Analytics** - Progress metrics and charts
4. **Scripts** - Training content library (if applicable)
5. **Profile** - User settings and progress

**Pattern:** Same 5-page structure for any vertical

---

## Reusable Skeleton Architecture

### What Stays the Same (90%):
- Database schema (5 core tables)
- Frontend pages (Practice, History, Analytics, Scripts, Profile)
- Voice integration layer
- AI coaching feedback engine
- Progress tracking system
- Prompt engineering structure

### What Changes Per Vertical (10%):
- Domain configuration (trainee role, AI role, goal)
- AI persona definitions (4 archetype descriptions)
- Practice mode definitions (5-7 mode descriptions)
- Coaching prompt template (domain-specific feedback criteria)
- Branding (colors, logo, terminology)

---

## Implementation Strategy

### Step 1: Extract Configuration Schema
```typescript
interface VerticalConfig {
  domain: {
    name: string; // "Door-to-door sales"
    traineeRole: string; // "Sales rep"
    aiRole: string; // "Homeowner"
    goal: string; // "Close the sale"
  };
  personas: Array<{
    id: string; // "lamb"
    name: string; // "Lamb"
    description: string;
    responseExamples: string[];
    objectionStyle: string;
  }>;
  practiceModes: Array<{
    id: string; // "full_pitch"
    name: string; // "Full Pitch"
    description: string;
    focusArea: string;
  }>;
  coachingPrompt: string; // LLM prompt for feedback generation
  branding: {
    primaryColor: string;
    logo: string;
    terminology: Record<string, string>; // "session" → "conversation"
  };
}
```

### Step 2: Create Vertical Template Generator
- Input: VerticalConfig JSON
- Output: Full codebase with domain-specific values injected

### Step 3: Build 3 Example Configs
1. Sales (existing)
2. Pickup Artist
3. Therapy

---

## Business Model Implications

**Current:** One-off custom build per vertical ($50k-100k dev cost)

**With Skeleton:** Config-driven platform ($5k-10k per vertical)

**Scaling Path:**
1. Build skeleton architecture tool (1 week)
2. Create 3 example configs to validate (2 days)
3. Offer "Vertical Roleplay Platform as a Service" to coaches
4. Charge $10k setup + $500/mo per vertical
5. Scale to 10+ verticals in 6 months

**Target Customers:**
- Sales training companies
- Dating/pickup coaches
- Therapy training programs
- Interview prep services
- Customer service training
- Negotiation training
- Public speaking coaches
- Leadership development
- Conflict resolution training
- Medical patient communication training

---

## Next Steps

1. **Build the skill:** `vertical-roleplay-platform-builder`
2. **Create config templates:** Sales, Dating, Therapy
3. **Build generator script:** Config JSON → Full codebase
4. **Validate:** Deploy 3 verticals to test pattern
5. **Package:** Turn into productized service

---

## Success Criteria

✅ Same 5-table database schema works for all verticals  
✅ Same 5-page frontend works for all verticals  
✅ Same voice integration works for all verticals  
✅ Same feedback engine works for all verticals  
✅ Only 10% of code changes per vertical (config-driven)  
✅ New vertical can be deployed in 1-2 days (not weeks)

---

**Conclusion:** This is a **highly reusable architecture pattern** that can scale horizontally across ANY coaching/training vertical with minimal customization.
