---
name: "voice-ai-integration"
description: "Specialized skill for voice ai integration workflows and automation."
---

# Voice AI Integration Skill

Build production-ready voice AI training platforms with Hume EVI (Empathic Voice Interface), Twilio phone integration, and modern web stack (React + tRPC + Drizzle ORM).

## When to Use This Skill

- Building voice-based roleplay or training systems
- Integrating Hume AI for emotionally intelligent conversations
- Adding phone calling capabilities (inbound/outbound) to web apps
- Creating practice/training platforms with conversation tracking
- Implementing multi-modal voice interfaces (web + phone)

## Core Architecture Pattern

```
Frontend (React + tRPC)
    ↓
Backend (Express + tRPC + Drizzle)
    ↓
Voice AI (Hume EVI) + Phone (Twilio)
    ↓
Database (MySQL/TiDB) - Session & conversation tracking
```

## Implementation Workflow

### Phase 1: Environment Setup

**1. Add Hume AI Credentials**

Use `webdev_request_secrets` to add:
- `HUME_API_KEY` - API key from Hume dashboard
- `HUME_SECRET_KEY` - Secret key for access token generation
- `HUME_FEMALE_CONFIG_ID` - Female voice configuration UUID
- `HUME_MALE_CONFIG_ID` - Male voice configuration UUID
- `HUME_WEBHOOK_URL` - Webhook endpoint for call events (optional)

**2. Add Twilio Credentials** (if phone integration needed)

- `TWILIO_ACCOUNT_SID` - Account SID from Twilio console
- `TWILIO_AUTH_TOKEN` - Auth token from Twilio console
- `TWILIO_PHONE_NUMBER` - Purchased phone number in E.164 format (+15551234567)

**3. Update server environment config**

Add to `server/_core/env.ts`:
```typescript
export const ENV = {
  // ... existing vars
  humeApiKey: process.env.HUME_API_KEY!,
  humeSecretKey: process.env.HUME_SECRET_KEY!,
  humeFemaleConfigId: process.env.HUME_FEMALE_CONFIG_ID!,
  humeMaleConfigId: process.env.HUME_MALE_CONFIG_ID!,
  humeWebhookUrl: process.env.HUME_WEBHOOK_URL,
  twilioAccountSid: process.env.TWILIO_ACCOUNT_SID,
  twilioAuthToken: process.env.TWILIO_AUTH_TOKEN,
  twilioPhoneNumber: process.env.TWILIO_PHONE_NUMBER,
};
```

### Phase 2: Database Schema

**Core tables needed:**

1. **Sessions table** - Practice/training sessions
   - userId, status, archetype/scenario, difficulty, mode
   - voiceGender, roleplayMode (standard/reverse)
   - callType (web/phone_inbound/phone_outbound)
   - userPhoneNumber, twilioCallSid
   - score, feedback, duration
   - userCode (for tracking individual users)

2. **Conversation turns table** - Message-by-message tracking
   - sessionId, speaker (user/ai), message, timestamp
   - emotions (JSON - from Hume), confidence

3. **User progress table** - Aggregate stats
   - userId, totalSessions, avgScore
   - Scenario-specific completion counters

4. **Scripts table** (if using predefined content)
   - userId, name, content, fileUrl

**Example schema** (Drizzle ORM):
```typescript
export const practiceSessions = mysqlTable('practice_sessions', {
  id: int('id').primaryKey().autoincrement(),
  userId: int('user_id').notNull(),
  userCode: varchar('user_code', { length: 50 }),
  archetype: varchar('archetype', { length: 50 }).notNull(),
  difficulty: varchar('difficulty', { length: 50 }).notNull(),
  practiceMode: varchar('practice_mode', { length: 50 }).notNull(),
  voiceGender: varchar('voice_gender', { length: 10 }).notNull(),
  roleplayMode: varchar('roleplay_mode', { length: 20 }).default('standard'),
  callType: varchar('call_type', { length: 20 }).default('web'),
  userPhoneNumber: varchar('user_phone_number', { length: 20 }),
  twilioCallSid: varchar('twilio_call_sid', { length: 100 }),
  status: varchar('status', { length: 20 }).notNull(),
  score: int('score'),
  feedback: text('feedback'),
  duration: int('duration'),
  createdAt: timestamp('created_at').defaultNow(),
});
```

### Phase 3: Hume Service Layer

**Install Hume SDK:**
```bash
pnpm add hume
```

**Create `server/hume-service.ts`:**

Key functions:
1. `getHumeAccessToken()` - Generate access token for client
2. `generateSystemPrompt()` - Dynamic prompt based on scenario/difficulty/mode
3. `prepareHumeSession()` - Return configId + systemPrompt
4. `getConfigId()` - Select male/female voice config

**System prompt pattern:**
```typescript
function generateSystemPrompt(params: {
  archetype: string;
  difficulty: string;
  practiceMode: string;
  roleplayMode: 'standard' | 'reverse';
  scriptContent?: string;
}): string {
  if (params.roleplayMode === 'reverse') {
    // AI plays expert sales rep, user plays homeowner
    return `You are an expert door-to-door fiber sales representative...`;
  }
  
  // Standard: AI plays homeowner, user plays sales rep
  return `You are a ${params.archetype} homeowner. ${getPersonalityTraits(params.archetype)}...`;
}
```

### Phase 4: Twilio Service Layer (Optional)

**Install Twilio SDK:**
```bash
pnpm add twilio
```

**Create `server/twilio-service.ts`:**

Key functions:
1. `getTwilioPhoneNumber()` - Return configured phone number
2. `initiateOutboundCall()` - Call user's phone number with Hume config

**Outbound call pattern:**
```typescript
export async function initiateOutboundCall(params: {
  toNumber: string;
  configId: string;
  apiKey: string;
}): Promise<{ success: boolean; callSid?: string; error?: string }> {
  const client = twilio(ENV.twilioAccountSid, ENV.twilioAuthToken);
  
  const call = await client.calls.create({
    to: params.toNumber,
    from: ENV.twilioPhoneNumber,
    twiml: `<Response><Connect><Stream url="wss://api.hume.ai/v0/evi/chat?config_id=${params.configId}&api_key=${params.apiKey}" /></Connect></Response>`,
  });
  
  return { success: true, callSid: call.sid };
}
```

### Phase 5: tRPC Router

**Create `server/practice-router.ts` (or similar):**

Essential endpoints:
1. `startSession` - Create session, return sessionId
2. `getHumeToken` - Get access token for web voice calls
3. `prepareHumeSession` - Get configId + systemPrompt
4. `getTwilioPhoneNumber` - Return phone number for call-in
5. `initiatePhoneCall` - Trigger outbound call
6. `updateSession` - Update score/feedback/duration
7. `getMySessions` - List user's sessions
8. `getSession` - Get single session details
9. `getConversation` - Get message-by-message transcript

**Key pattern - session creation:**
```typescript
startSession: protectedProcedure
  .input(z.object({
    scriptId: z.number().optional(),
    userCode: z.string().optional(),
    archetype: z.enum(['type1', 'type2', 'type3']),
    difficulty: z.enum(['easy', 'medium', 'hard']),
    practiceMode: z.enum(['mode1', 'mode2']),
    voiceGender: z.enum(['male', 'female']),
  }))
  .mutation(async ({ ctx, input }) => {
    const result = await createPracticeSession({
      userId: ctx.user.id,
      ...input,
      status: 'in_progress',
    });
    return { sessionId: result.insertId };
  })
```

### Phase 6: Frontend React Hooks

**Create `client/src/hooks/useHumeVoice.ts`:**

Manages WebSocket connection to Hume EVI:
- Connect/disconnect
- Send/receive audio
- Handle messages with emotional data
- Track connection status

**Pattern:**
```typescript
export function useHumeVoice(sessionId: number | null) {
  const [status, setStatus] = useState<'idle' | 'connecting' | 'connected' | 'disconnected'>('idle');
  const [messages, setMessages] = useState<Message[]>([]);
  
  const connect = async () => {
    const token = await trpc.practice.getHumeToken.query();
    const config = await trpc.practice.prepareHumeSession.query({ sessionId });
    
    // WebSocket connection to Hume EVI
    const ws = new WebSocket(`wss://api.hume.ai/v0/evi/chat?access_token=${token}&config_id=${config.configId}`);
    // ... handle audio streaming
  };
  
  return { status, messages, connect, disconnect };
}
```

### Phase 7: Voice Call UI Component

**Create `client/src/components/VoiceCall.tsx`:**

Features:
- Start/end call buttons
- Mute/unmute toggle
- Real-time transcript display
- Call duration timer
- Visual status indicators

**Integration with useHumeVoice hook:**
```typescript
export function VoiceCall({ sessionId }: { sessionId: number }) {
  const { status, messages, connect, disconnect } = useHumeVoice(sessionId);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Practice Session</CardTitle>
        <Badge>{status}</Badge>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={msg.speaker === 'user' ? 'text-right' : 'text-left'}>
              <p>{msg.content}</p>
            </div>
          ))}
        </div>
        <Button onClick={status === 'connected' ? disconnect : connect}>
          {status === 'connected' ? 'End Call' : 'Start Call'}
        </Button>
      </CardContent>
    </Card>
  );
}
```

### Phase 8: Practice Configuration UI

**Create `client/src/pages/Practice.tsx`:**

Configuration sections:
1. Script selection (optional)
2. User code input (for tracking)
3. Scenario/archetype selection
4. Difficulty level
5. Practice mode (full/partial)
6. Roleplay mode (standard/reverse)
7. Call method (web/phone-in/phone-out)
8. Voice gender

**Phone integration UI:**
```typescript
// Call method selection
<RadioGroup value={callMethod} onValueChange={setCallMethod}>
  <RadioGroupItem value="web">Web Browser</RadioGroupItem>
  <RadioGroupItem value="phone_inbound">
    Call In: {twilioPhone?.phoneNumber}
  </RadioGroupItem>
  <RadioGroupItem value="phone_outbound">
    Receive Call
  </RadioGroupItem>
</RadioGroup>

// Phone number input (for outbound)
{callMethod === 'phone_outbound' && (
  <Input
    placeholder="+15551234567"
    value={userPhoneNumber}
    onChange={(e) => setUserPhoneNumber(e.target.value)}
  />
)}
```

### Phase 9: History & Analytics

**Create `client/src/pages/History.tsx`:**

Display:
- Session list with filters
- Session details dialog
- Full conversation transcript
- Performance metrics
- Progress by scenario/difficulty

**Create `client/src/pages/Analytics.tsx`:**

Aggregate stats:
- Total sessions
- Average score
- Completion rates by scenario
- Difficulty progression
- Time-series charts

## Testing Strategy

**1. Credential validation tests:**
```typescript
// server/hume.credentials.test.ts
test('Hume credentials are valid', async () => {
  const token = await getHumeAccessToken();
  expect(token).toBeTruthy();
});
```

**2. Integration tests:**
```typescript
// server/phone-integration.test.ts
test('System prompt includes roleplay mode', () => {
  const prompt = generateSystemPrompt({ roleplayMode: 'reverse', ... });
  expect(prompt).toContain('expert sales representative');
});
```

**3. End-to-end flow:**
- Start session → Connect to Hume → Have conversation → End session → View history

## Common Patterns

### Reverse Roleplay Mode

Allow users to practice by playing the "customer" role while AI demonstrates expert responses:

```typescript
if (roleplayMode === 'reverse') {
  systemPrompt = `You are an expert ${profession}. The user will play the role of ${customerType} and present objections or scenarios. Demonstrate how to handle them professionally...`;
} else {
  systemPrompt = `You are a ${customerType}. The user is a ${profession} trying to ${goal}...`;
}
```

### User Code Tracking

Enable managers to track individual users without requiring login:

```typescript
// Auto-fill from profile or manual entry
const repCode = user?.repCode || manualRepCode || undefined;

// Store with session
await createPracticeSession({
  userId: ctx.user.id,
  userCode: repCode,
  ...otherParams
});

// Filter in manager dashboard
const sessions = await getUserSessions({ userCode: 'REP-1234' });
```

### Dynamic System Prompts

Adjust AI behavior based on difficulty:

```typescript
const difficultyModifiers = {
  rookie: 'Be friendly and receptive. Show clear buying signals.',
  intermediate: 'Be neutral. Require some persuasion.',
  expert: 'Be skeptical. Present common objections.',
  nightmare: 'Be hostile and dismissive. Maximum difficulty.',
};

systemPrompt += ` ${difficultyModifiers[difficulty]}`;
```

## Deployment Checklist

- [ ] All credentials added via `webdev_request_secrets`
- [ ] Database migrations applied (`pnpm db:push`)
- [ ] Hume credentials validated (run credential tests)
- [ ] Twilio phone number configured (if using phone)
- [ ] Webhook endpoints secured (if using webhooks)
- [ ] Test web voice calls end-to-end
- [ ] Test phone calls (inbound + outbound)
- [ ] Verify conversation tracking in database
- [ ] Check analytics/history pages display correctly

## Troubleshooting

**Hume 401 errors:**
- Regenerate API keys from Hume dashboard
- Verify `HUME_API_KEY` and `HUME_SECRET_KEY` are correct
- Check access token generation function

**Twilio call failures:**
- Verify phone number is in E.164 format (+15551234567)
- Check `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`
- Ensure Twilio account has sufficient balance
- Test with Twilio console first

**WebSocket connection issues:**
- Check CORS settings for Hume WebSocket
- Verify access token is valid and not expired
- Ensure browser supports WebRTC/MediaRecorder

**No audio in calls:**
- Check microphone permissions in browser
- Verify audio devices are working
- Test with simple WebRTC example first

## References

- Hume EVI Documentation: https://dev.hume.ai/docs/empathic-voice-interface-evi/overview
- Twilio Voice API: https://www.twilio.com/docs/voice
- tRPC Documentation: https://trpc.io/docs
- Drizzle ORM: https://orm.drizzle.team/docs/overview
