---
name: "serverless-debugging"
description: "Specialized skill for serverless debugging workflows and automation."
---

# Serverless Debugging

Systematic debugging methodology for serverless/edge functions where console.log may not appear in logs and traditional debugging tools are unavailable.

## When to Use This Skill

- Feature deployed but not triggering (code exists but never executes)
- Console.log statements don't appear in logs
- No visible errors but behavior doesn't match expectations
- Database state doesn't update as expected
- Type coercion or default value bugs
- Async/timing issues in distributed systems

## Core Methodology: 4-Phase Approach

### Phase 1: Evidence Gathering

Collect evidence from ALL layers before forming hypotheses. Avoid jumping to conclusions.

**Database Layer:**
- Query actual data state (not assumptions)
- Check default values vs. expected values
- Verify row counts, timestamps, update patterns
- Look for NULL vs. 0 vs. empty string differences

**Code Layer:**
- Verify deployed code matches local code
- Check function version numbers
- Review conditional logic and type checks
- Identify all code paths that could prevent execution

**Runtime Layer:**
- Check deployment status (ACTIVE, version number)
- Review available logs (even if incomplete)
- Note what SHOULD appear in logs but doesn't
- Check for silent failures (no error, no success)

**Environment Layer:**
- Verify environment variables are set
- Check permissions and RLS policies
- Confirm API keys and authentication
- Review timeout settings

**Evidence Checklist:** See `references/evidence-checklist.md` for comprehensive list

### Phase 2: Pattern Analysis

Compare working vs. broken behavior to identify differences.

**Key Questions:**
- What works? What doesn't?
- When did it last work? What changed?
- Are there similar features that DO work? How do they differ?
- What's the simplest test case that reproduces the issue?

**Common Patterns:**
- Logging doesn't work in this environment (find alternatives)
- Code path never reached (condition always false)
- Type mismatch (0 vs null, string vs number)
- Async race condition (timing-dependent)
- Environment-specific behavior (works locally, fails in production)

### Phase 3: Hypothesis Formation

Form specific, testable hypotheses based on evidence.

**Good Hypothesis Characteristics:**
- Explains ALL observed symptoms
- Testable with available tools
- Specific about root cause (not vague)
- Based on evidence, not assumptions

**Example Hypotheses:**
- "Database default is 0, but code checks for null"
- "Function never reaches line X because condition Y is always false"
- "Environment variable Z is not set in production"
- "RLS policy blocks access for this user role"

**Testing Without Logs:**
- Use database writes as "print statements"
- Add error responses with diagnostic info
- Create minimal reproduction cases
- Test conditions in isolation

### Phase 4: Implementation & Verification

Fix the root cause and verify across all layers.

**Fix Implementation:**
- Make minimal, targeted changes
- Document the bug and fix
- Update tests to prevent regression
- Deploy new version

**Verification:**
- Database state updates as expected
- Feature triggers in expected scenarios
- No side effects on other features
- End-to-end test passes

## Common Serverless Bugs

See `references/common-serverless-bugs.md` for detailed catalog. Quick reference:

**Type Coercion Issues:**
- `0 === null` → false (check for both)
- `undefined === null` → false
- Empty string vs null vs undefined
- Number strings vs numbers ("0" vs 0)

**Async/Timing Issues:**
- Fire-and-forget operations that fail silently
- Race conditions in parallel operations
- Timeout before completion
- Promise not awaited

**Environment Differences:**
- Console.log works locally but not in production
- Environment variables not set
- Different runtime versions
- Permission differences

**Database Issues:**
- RLS policies blocking access
- Default values vs. expected values
- Transaction isolation issues
- Connection pool exhaustion

## Alternative Debugging Strategies

When console.log doesn't work, use these alternatives:

**Database-Driven Debugging:**
```sql
-- Create debug log table
CREATE TABLE debug_logs (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  function_name TEXT,
  checkpoint TEXT,
  data JSONB
);

-- Write debug info from code
INSERT INTO debug_logs (function_name, checkpoint, data)
VALUES ('my-function', 'before-extraction', jsonb_build_object('count', message_count));
```

**Error Response Debugging:**
```typescript
// Return diagnostic info in error response
return new Response(JSON.stringify({
  debug: {
    messageCount: messageCount,
    lastExtraction: lastExtraction,
    shouldExtract: shouldExtractMemories(messageCount, lastExtraction)
  }
}), { status: 200 });
```

**Code Analysis:**
- Read deployed code directly (if accessible)
- Trace execution paths on paper
- Check type of every variable in conditions
- Verify all branches can be reached

See `references/logging-alternatives.md` for more strategies.

## Practical Tools

**Deployment Verification:**
```bash
# Use scripts/check_deployment.py
python scripts/check_deployment.py <function-name> <local-path>
```

**Database State Analysis:**
```bash
# Use scripts/database_debugger.py
python scripts/database_debugger.py <table-name> <condition>
```

**Type Analysis:**
```bash
# Use scripts/type_analyzer.py
python scripts/type_analyzer.py <file-path> <function-name>
```

## Real-World Example: Wade Memory Extraction Bug

**Symptom:** Proactive memory extraction never triggered despite code being deployed.

**Phase 1 Evidence:**
- ✅ Code deployed (v48)
- ✅ Database schema correct
- ✅ Messages stored (8-10 messages)
- ❌ Console.log never appeared
- ❌ `last_extraction_at` stayed at 0

**Phase 2 Pattern:**
- Console.log doesn't work in Supabase Edge Functions logs API
- Needed alternative debugging approach

**Phase 3 Hypothesis:**
- Database default for `last_extraction_at` is 0, not null
- Code checks `if (lastExtraction === null)` → always false when 0
- Takes wrong branch: `messageCount - 0 >= 10` instead of `messageCount >= 4`

**Phase 4 Fix:**
```typescript
// Before: Only checked null
if (lastExtractionAt === null) {
  return messageCount >= 4;
}

// After: Check both null AND 0
if (lastExtractionAt === null || lastExtractionAt === 0) {
  return messageCount >= 4;
}
```

**Result:** Feature now works correctly, triggers after 4 messages.

## Best Practices

1. **Gather evidence before hypothesizing** - Resist the urge to guess
2. **Use database as debugging tool** - When logs fail, database writes work
3. **Check type coercion carefully** - 0, null, undefined are all different
4. **Verify deployed code** - Don't assume local matches production
5. **Test in isolation** - Minimal reproduction cases reveal root cause
6. **Document the process** - Future debugging benefits from past patterns

## Quick Start

1. Read `references/evidence-checklist.md` and gather evidence from all layers
2. Identify patterns using Phase 2 questions
3. Form testable hypothesis
4. Use `scripts/` tools to verify hypothesis
5. Implement fix and verify across all layers
6. Document bug and fix for future reference


## When 3+ Fixes Fail: Question the Architecture

**Red flag pattern:** Multiple fix attempts, each revealing new problems in different layers.

### Symptoms

- ✅ Fix #1: Added environment variables → Still failing
- ✅ Fix #2: Force redeployed → Still failing
- ✅ Fix #3: Added to all environments → Still failing
- ✅ Fix #4: Created lazy initialization → Deployment failed
- ✅ Fix #5: Tried different deployment method → New error

**Pattern:** Not converging on a solution. Each fix reveals a NEW problem.

### What This Means

**Per systematic-debugging Phase 4.5:**

> If 3+ fixes failed: STOP and question the architecture

This is NOT a bug. This is an **ARCHITECTURAL PROBLEM**.

### Root Cause Analysis

**The real issues:**
1. **Generic error messages** - Can't see actual problem
2. **No direct code access** - Can't iterate quickly
3. **Complex deployment pipeline** - Adds failure points
4. **No local testing** - Can't reproduce issue
5. **Limited observability** - Can't see runtime state

### What to Do

**STOP attempting more fixes. Instead:**

1. **Get better error visibility**
   - Add comprehensive error logging (see `references/enhanced-error-logging.md`)
   - Access full logs (not truncated)
   - Add diagnostic endpoints

2. **Simplify the workflow**
   - Test locally first
   - Use proper version control (GitHub)
   - Set up CI/CD pipeline
   - Remove manual deployment steps

3. **Question the fundamentals**
   - Is this deployment method sound?
   - Are we fighting the platform?
   - Should we refactor the approach?

### Real-World Example: Stripe Integration

**Attempts:**
1. Added Stripe keys to Vercel → Still failing
2. Force redeployed → Still failing
3. Added keys to all environments → Still failing
4. Created lazy initialization fix → Deployment failed
5. Tried Google Drive transfer → Downloaded 0 bytes

**Root cause:** Generic error message hid the actual Stripe error

**Solution:** Add comprehensive error logging to see real error, then fix that

**Lesson:** After 3 failed fixes, we should have stopped and added better logging FIRST

### Key Takeaways

- **3+ failed fixes = architectural problem**
- **Stop fixing, start observing**
- **Add logging before adding fixes**
- **Question the deployment workflow**
- **Test locally before deploying**

See also: `systematic-debugging` skill Phase 4.5

## Lazy Initialization for External Services

**Problem:** Module-level initialization fails in serverless environments.

```javascript
// ❌ DON'T: Initialize at module load
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
```

**Why it fails:**
- Environment variables may not be ready at cold start
- No validation that keys exist
- Initialization errors hidden
- Cached instances retain old values

**Solution:** Lazy initialization pattern

```javascript
// ✅ DO: Initialize on first use
let stripeInstance = null;

function getStripe() {
  if (!stripeInstance) {
    const key = process.env.STRIPE_SECRET_KEY;
    if (!key) throw new Error('STRIPE_SECRET_KEY not set');
    stripeInstance = require('stripe')(key);
  }
  return stripeInstance;
}
```

**Benefits:**
- ✅ Environment variables validated
- ✅ Clear error if missing
- ✅ Initialization after env vars loaded
- ✅ Proper error logging

See `references/lazy-initialization-patterns.md` for complete examples.

## Enhanced Error Logging

**Problem:** Generic error messages hide root cause.

```javascript
// ❌ DON'T: Hide error details
catch (error) {
  res.status(500).json({ error: 'An error occurred' });
}
```

**Solution:** Log full error details

```javascript
// ✅ DO: Log comprehensive error info
catch (error) {
  console.error('Operation failed:', {
    message: error.message,
    type: error.type,
    code: error.code,
    stack: error.stack,
    context: { priceId, userId }
  });
  res.status(500).json({ 
    error: error.message,
    type: error.type,
    code: error.code
  });
}
```

See `references/enhanced-error-logging.md` for patterns.

## Diagnostic Health Endpoints

Add health check endpoints to verify configuration:

```javascript
app.get('/api/health', (req, res) => {
  const config = {
    stripe: !!process.env.STRIPE_SECRET_KEY,
    supabase: !!process.env.SUPABASE_URL
  };
  
  const keyPrefixes = {
    stripe: config.stripe ? process.env.STRIPE_SECRET_KEY.substring(0, 7) : 'none'
  };
  
  res.json({ 
    status: 'ok',
    configured: config,
    keyPrefixes: keyPrefixes
  });
});
```

**Usage:**
```bash
curl https://your-api.vercel.app/api/health
```

This immediately shows:
- Which services are configured
- Key prefixes (safe to log)
- Whether environment variables are set
