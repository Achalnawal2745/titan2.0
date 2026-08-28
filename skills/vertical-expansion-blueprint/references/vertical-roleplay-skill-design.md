# Vertical Roleplay Platform Builder - Skill Design

## Skill Name: `vertical-roleplay-platform-builder`

## Description
Generate complete AI roleplay training platforms for ANY vertical industry (sales, dating, therapy, etc.) from a single JSON configuration file. Reduces deployment time from weeks to hours.

---

## Skill Structure

```
/home/ubuntu/skills/vertical-roleplay-platform-builder/
├── SKILL.md                          # Main skill documentation
├── references/
│   ├── architecture-pattern.md       # Core architecture explanation
│   ├── config-schema.md              # Detailed schema documentation
│   └── deployment-guide.md           # How to deploy generated platforms
├── templates/
│   ├── config-examples/
│   │   ├── sales.json                # Example: Door-to-door sales
│   │   ├── dating.json               # Example: Pickup artist coaching
│   │   └── therapy.json              # Example: Therapy training
│   ├── database-schema.sql           # Universal 5-table schema
│   ├── hume-service-template.ts      # Prompt generation template
│   ├── practice-page-template.tsx    # Frontend practice page template
│   └── coaching-prompt-template.txt  # AI feedback generation template
├── scripts/
│   ├── validate-config.js            # Validate config JSON against schema
│   ├── generate-platform.js          # Main generator script
│   └── deploy-vertical.sh            # Deployment automation script
└── README.md                         # Quick start guide
```

---

## How It Works

### Step 1: Create Config File
User creates a JSON file matching the `VerticalConfig` schema:

```json
{
  "metadata": {
    "id": "therapy",
    "name": "Therapy Training Platform",
    ...
  },
  "domain": {
    "traineeRole": "Therapist",
    "aiRole": "Client",
    ...
  },
  "personas": [...],
  "difficultyLevels": [...],
  ...
}
```

### Step 2: Validate Config
```bash
node scripts/validate-config.js therapy.json
```

Output:
```
✅ Config valid
✅ 4 personas defined
✅ 5 difficulty levels defined
✅ 6 practice modes defined
✅ Coaching prompt complete
✅ Branding configured
```

### Step 3: Generate Platform
```bash
node scripts/generate-platform.js therapy.json --output /home/ubuntu/therapy-roleplay-platform
```

Output:
```
🚀 Generating platform...
✅ Created database schema
✅ Generated server/hume-service.ts
✅ Generated server/routers.ts
✅ Generated client/src/pages/Practice.tsx
✅ Generated client/src/pages/History.tsx
✅ Generated client/src/pages/Analytics.tsx
✅ Applied branding (colors, logo, terminology)
✅ Platform ready at /home/ubuntu/therapy-roleplay-platform
```

### Step 4: Deploy
```bash
cd /home/ubuntu/therapy-roleplay-platform
pnpm install
pnpm db:push
pnpm dev
```

---

## What Gets Generated

### 1. Database Schema (drizzle/schema.ts)
- `users` table
- `scripts` table (if contentSystem.enabled)
- `practiceSessions` table
- `conversationTurns` table
- `userProgress` table

**No changes needed** - same schema for all verticals

### 2. Server Files
- `server/hume-service.ts` - Prompt generation with config-injected personas/difficulty/modes
- `server/routers.ts` - tRPC procedures (same for all verticals)
- `server/db.ts` - Database queries (same for all verticals)

**Only `hume-service.ts` changes** - prompts are config-driven

### 3. Client Files
- `client/src/pages/Practice.tsx` - Session start page with config personas/modes
- `client/src/pages/History.tsx` - Session history (same for all verticals)
- `client/src/pages/Analytics.tsx` - Progress metrics (same for all verticals)
- `client/src/pages/Scripts.tsx` - Content library (if contentSystem.enabled)
- `client/src/index.css` - Branding colors from config

**Only branding and terminology change** - structure stays the same

### 4. Configuration Files
- `package.json` - Dependencies (same for all verticals)
- `drizzle.config.ts` - Database config (same for all verticals)
- `.env.example` - Environment variables template

**No changes needed**

---

## Generator Script Logic

### `generate-platform.js` Pseudocode

```javascript
const config = JSON.parse(fs.readFileSync('therapy.json'));

// 1. Create project directory
fs.mkdirSync(outputPath);

// 2. Copy base template files (90% of codebase)
copyTemplate('base-platform-template/', outputPath);

// 3. Generate config-driven files (10% of codebase)
generateHumeService(config, `${outputPath}/server/hume-service.ts`);
generatePracticePage(config, `${outputPath}/client/src/pages/Practice.tsx`);
generateBranding(config, `${outputPath}/client/src/index.css`);

// 4. Inject terminology replacements
replaceTerminology(config.branding.terminology, outputPath);

// 5. Generate README with vertical-specific instructions
generateREADME(config, `${outputPath}/README.md`);

console.log('✅ Platform generated successfully!');
```

---

## Key Templates

### Template 1: `hume-service-template.ts`

```typescript
// This template uses {{placeholders}} that get replaced with config values

export function generateSystemPrompt(
  archetype: string,
  difficulty: string,
  practiceMode: string
) {
  const archetypeDescriptions = {
    {{#each personas}}
    {{id}}: "{{traits}}",
    {{/each}}
  };

  const archetypeExamples = {
    {{#each personas}}
    {{id}}: {
      responses: [
        {{#each responseExamples}}
        "{{this}}",
        {{/each}}
      ],
      objectionStyle: "{{objectionStyle}}",
    },
    {{/each}}
  };

  const difficultyModifiers = {
    {{#each difficultyLevels}}
    {{id}}: "{{promptModifier}}",
    {{/each}}
  };

  const modeInstructions = {
    {{#each practiceModes}}
    {{id}}: "{{promptInstructions}}",
    {{/each}}
  };

  let prompt = `🏠 YOU ARE THE {{domain.aiRole}}. The user is the {{domain.traineeRole}} at YOUR door.

You are ${archetypeDescriptions[archetype]} ${difficultyModifiers[difficulty]}

HOW YOU RESPOND (${archetype.toUpperCase()} PERSONALITY):
Example responses that match your personality:
${archetypeExamples[archetype].responses.map((ex, i) => `${i + 1}. "${ex}"`).join('\n')}

When raising objections, use this style: ${archetypeExamples[archetype].objectionStyle}

${modeInstructions[practiceMode]}

REMEMBER: You are the {{domain.aiRole}}. The user is the {{domain.traineeRole}}. You are being {{domain.goal}}.

...`;

  return prompt;
}
```

### Template 2: `practice-page-template.tsx`

```tsx
// This template injects config values into the Practice page

export default function Practice() {
  const [archetype, setArchetype] = useState<string>("{{personas.0.id}}");
  const [difficulty, setDifficulty] = useState<string>("rookie");
  const [practiceMode, setPracticeMode] = useState<string>("{{practiceModes.0.id}}");

  return (
    <div>
      <h1>Start {{branding.terminology.session || "Session"}}</h1>

      {/* Archetype Selection */}
      <div>
        <Label>Select {{branding.terminology.aiCharacter || "AI Character"}}</Label>
        <Select value={archetype} onValueChange={setArchetype}>
          {{#each personas}}
          <SelectItem value="{{id}}">{{emoji}} {{name}} - {{description}}</SelectItem>
          {{/each}}
        </Select>
      </div>

      {/* Difficulty Selection */}
      <div>
        <Label>Select Difficulty</Label>
        <Select value={difficulty} onValueChange={setDifficulty}>
          {{#each difficultyLevels}}
          <SelectItem value="{{id}}">{{name}} - {{description}}</SelectItem>
          {{/each}}
        </Select>
      </div>

      {/* Practice Mode Selection */}
      <div>
        <Label>Select Practice Mode</Label>
        <Select value={practiceMode} onValueChange={setPracticeMode}>
          {{#each practiceModes}}
          <SelectItem value="{{id}}">{{name}} - {{description}}</SelectItem>
          {{/each}}
        </Select>
      </div>

      <Button onClick={handleStartSession}>
        Start {{branding.terminology.session || "Session"}}
      </Button>
    </div>
  );
}
```

### Template 3: `coaching-prompt-template.txt`

```
{{coachingPrompt.systemPrompt}}

{{coachingPrompt.analysisTemplate}}

Evaluate based on these criteria:
{{#each coachingPrompt.evaluationCriteria}}
- {{this}}
{{/each}}

Output format:
{
  "strengths": [{{coachingPrompt.outputFormat.strengths}}],
  "weaknesses": [{{coachingPrompt.outputFormat.weaknesses}}],
  "recommendations": [{{coachingPrompt.outputFormat.recommendations}}],
  "score": {{coachingPrompt.outputFormat.score}}
}
```

---

## Validation Script

### `validate-config.js`

```javascript
const Ajv = require('ajv');
const fs = require('fs');

const schema = require('./vertical-config-schema.json');
const config = JSON.parse(fs.readFileSync(process.argv[2]));

const ajv = new Ajv();
const validate = ajv.compile(schema);

if (validate(config)) {
  console.log('✅ Config valid');
  
  // Additional validation checks
  if (config.personas.length !== 4) {
    console.warn('⚠️  Warning: Expected 4 personas, found', config.personas.length);
  }
  
  if (config.difficultyLevels.length !== 5) {
    console.warn('⚠️  Warning: Expected 5 difficulty levels, found', config.difficultyLevels.length);
  }
  
  if (config.practiceModes.length < 5 || config.practiceModes.length > 7) {
    console.warn('⚠️  Warning: Expected 5-7 practice modes, found', config.practiceModes.length);
  }
  
  console.log('✅ All checks passed');
} else {
  console.error('❌ Config invalid:', validate.errors);
  process.exit(1);
}
```

---

## Usage Examples

### Example 1: Generate Sales Platform
```bash
# Use the sales config
node scripts/generate-platform.js templates/config-examples/sales.json --output /home/ubuntu/sales-platform

# Deploy
cd /home/ubuntu/sales-platform
pnpm install && pnpm db:push && pnpm dev
```

### Example 2: Generate Dating Coach Platform
```bash
# Use the dating config
node scripts/generate-platform.js templates/config-examples/dating.json --output /home/ubuntu/dating-platform

# Deploy
cd /home/ubuntu/dating-platform
pnpm install && pnpm db:push && pnpm dev
```

### Example 3: Generate Therapy Training Platform
```bash
# Use the therapy config
node scripts/generate-platform.js templates/config-examples/therapy.json --output /home/ubuntu/therapy-platform

# Deploy
cd /home/ubuntu/therapy-platform
pnpm install && pnpm db:push && pnpm dev
```

---

## Business Model

### Traditional Approach
- Custom build per vertical: $50k-100k
- Development time: 4-8 weeks
- Maintenance: Separate codebases

### With This Skill
- Config-driven deployment: $5k-10k
- Development time: 1-2 days
- Maintenance: Single codebase, config updates only

### Scaling Path
1. Build 3 example configs (sales, dating, therapy)
2. Offer "Vertical Roleplay Platform as a Service"
3. Charge $10k setup + $500/mo per vertical
4. Scale to 10+ verticals in 6 months
5. Target: Sales training, dating coaches, therapy programs, interview prep, customer service, negotiation, public speaking, leadership, conflict resolution, medical communication

---

## Next Steps

1. **Phase 4:** Initialize the skill using skill-development-workflow
2. **Phase 5:** Create 3 example configs (sales, dating, therapy)
3. **Phase 6:** Build and test the generator script
4. **Phase 7:** Validate by generating and deploying all 3 platforms
5. **Phase 8:** Package and document for productization

---

## Success Criteria

✅ Single config file generates full platform  
✅ 90% of code is reusable across verticals  
✅ New vertical can be deployed in 1-2 days  
✅ Same database schema works for all verticals  
✅ Same frontend structure works for all verticals  
✅ Only prompts and branding change per vertical  
✅ Validated with 3 different verticals (sales, dating, therapy)
