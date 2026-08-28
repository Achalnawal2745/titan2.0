# Common Serverless Bugs Catalog

This catalog documents frequently encountered bugs in serverless environments, organized by category with real-world examples and solutions.

## Type Coercion Bugs

### NULL vs 0 vs Undefined

**Pattern:** Database defaults to 0, but code checks for null.

**Example:**
```typescript
// Database: last_extraction_at INTEGER DEFAULT 0
// Code:
if (lastExtractionAt === null) {
  return messageCount >= 4;  // Never executes!
}
return messageCount - lastExtractionAt >= 10;  // Always executes
```

**Why it fails:** In JavaScript, `0 === null` is false. The condition never matches, taking the wrong branch.

**Solution:** Check for both null AND the default value.
```typescript
if (lastExtractionAt === null || lastExtractionAt === 0) {
  return messageCount >= 4;
}
```

**Prevention:** Always verify database defaults match code assumptions.

### String vs Number Comparison

**Pattern:** Database returns string, code expects number.

**Example:**
```typescript
const count = await db.query('SELECT COUNT(*) as count FROM messages');
if (count.count > 10) {  // count.count is "15" (string)
  // This comparison may fail unexpectedly
}
```

**Why it fails:** String "15" > 10 works due to coercion, but "5" > 10 is true (lexicographic).

**Solution:** Explicitly convert types.
```typescript
if (parseInt(count.count) > 10) {
  // Reliable numeric comparison
}
```

### Empty String vs NULL

**Pattern:** Form field or API parameter is empty string, code checks for null.

**Example:**
```typescript
if (userInput === null) {
  useDefault();  // Never executes for empty string
}
```

**Solution:** Check for both null and empty string.
```typescript
if (!userInput || userInput === null) {
  useDefault();
}
```

## Async/Timing Bugs

### Fire-and-Forget Failures

**Pattern:** Background operation fails silently because promise is not awaited.

**Example:**
```typescript
// Wrong: Fire and forget
extractMemories(conversationId, userId)
  .then(() => console.log('Success'))
  .catch(err => console.error('Failed:', err));

return new Response('OK');  // Returns before extraction completes
```

**Why it fails:** If extraction fails, the error is logged but not handled. The function returns success regardless.

**Solution:** Either await the operation or use proper error handling.
```typescript
// Option 1: Await
await extractMemories(conversationId, userId);

// Option 2: Fire-and-forget with database logging
extractMemories(conversationId, userId)
  .catch(err => db.logError('extraction-failed', err));
```

### Race Conditions

**Pattern:** Multiple concurrent operations modify the same resource.

**Example:**
```typescript
// Two requests arrive simultaneously
const count = await getMessageCount(conversationId);  // Both read 3
await incrementMessageCount(conversationId);  // Both write 4
// Expected: 5, Actual: 4
```

**Solution:** Use atomic operations or database transactions.
```typescript
// Atomic increment
await db.query('UPDATE conversations SET message_count = message_count + 1');
```

### Missing Await

**Pattern:** Async function called without await, code continues before completion.

**Example:**
```typescript
async function processData() {
  const data = fetchData();  // Missing await!
  console.log(data);  // Logs Promise object, not data
}
```

**Solution:** Always await async functions.
```typescript
const data = await fetchData();
```

## Environment Bugs

### Console.log Not Visible

**Pattern:** Console.log works locally but doesn't appear in production logs.

**Platforms affected:** Supabase Edge Functions, some AWS Lambda configurations, Cloudflare Workers (limited logging).

**Why it fails:** Some serverless platforms don't expose stdout/stderr in standard logs API.

**Solution:** Use alternative logging methods.
```typescript
// Database logging
await db.insert('debug_logs', {
  function: 'my-function',
  message: 'Debug info',
  data: { count: messageCount }
});

// Error response debugging (for testing)
return new Response(JSON.stringify({ debug: { count: messageCount } }));
```

### Environment Variables Not Set

**Pattern:** Environment variable works locally but is undefined in production.

**Example:**
```typescript
const apiKey = process.env.API_KEY;
fetch(url, { headers: { 'Authorization': apiKey } });  // Fails if undefined
```

**Why it fails:** Environment variables must be explicitly set in serverless platform, not inherited from .env files.

**Solution:** Verify environment variables are set in platform settings and handle missing values.
```typescript
const apiKey = process.env.API_KEY;
if (!apiKey) {
  throw new Error('API_KEY environment variable not set');
}
```

### Runtime Version Differences

**Pattern:** Code works with Node 18 locally but production uses Node 16.

**Example:**
```typescript
// Node 18 feature
const result = array.findLast(item => item.id === targetId);
// Fails on Node 16: findLast is not a function
```

**Solution:** Check platform runtime version and use compatible features.

## Database Bugs

### RLS Policy Blocking Access

**Pattern:** Query returns empty results despite data existing.

**Example:**
```typescript
const { data } = await supabase
  .from('messages')
  .select('*')
  .eq('conversation_id', conversationId);
// Returns [] even though messages exist
```

**Why it fails:** Row Level Security policy prevents access for the current user role.

**Solution:** Test with service role to rule out RLS, then fix policy.
```typescript
// Test with service role
const { data } = await supabaseAdmin  // Uses service_role key
  .from('messages')
  .select('*')
  .eq('conversation_id', conversationId);
```

### Default Value Mismatch

**Pattern:** Database default doesn't match code expectations.

**Example:**
```sql
-- Schema
CREATE TABLE conversations (
  last_extraction_at INTEGER DEFAULT 0  -- Default is 0
);

-- Code expects NULL
if (conversation.last_extraction_at === null) {
  // Never executes because default is 0, not NULL
}
```

**Solution:** Align database defaults with code logic or handle all possible default values.

### Transaction Isolation Issues

**Pattern:** Read-modify-write operations see stale data.

**Example:**
```typescript
const count = await getCount();  // Reads 5
// Another request increments to 6
await setCount(count + 1);  // Sets to 6, not 7
```

**Solution:** Use transactions or atomic operations.
```typescript
await db.transaction(async (trx) => {
  const count = await trx.getCount();
  await trx.setCount(count + 1);
});
```

## Logic Bugs

### Unreachable Code Path

**Pattern:** Condition is always false, code never executes.

**Example:**
```typescript
if (messageCount >= 4 && lastExtraction === null) {
  extract();  // Never runs if lastExtraction defaults to 0
}
```

**Solution:** Trace all possible values through the condition.
```typescript
// Check all "empty" values
if (messageCount >= 4 && (lastExtraction === null || lastExtraction === 0)) {
  extract();
}
```

### Early Return Skipping Code

**Pattern:** Early return prevents important code from executing.

**Example:**
```typescript
async function processMessage(message) {
  if (!message.content) return;  // Early return
  
  await storeMessage(message);
  await extractMemories();  // Never runs for empty content
}
```

**Solution:** Ensure early returns don't skip critical operations.

### Off-by-One Errors

**Pattern:** Boundary conditions are incorrect.

**Example:**
```typescript
// Extract every 10 messages starting from message 10
if (messageCount % 10 === 0) {
  extract();  // Runs at 10, 20, 30... but not at 4 for first extraction
}
```

**Solution:** Handle initial case separately.
```typescript
if (lastExtraction === 0 && messageCount >= 4) {
  extract();  // First extraction
} else if (messageCount - lastExtraction >= 10) {
  extract();  // Subsequent extractions
}
```

## Platform-Specific Bugs

### Supabase Edge Functions

**Issue:** Console.log doesn't appear in logs API.
**Solution:** Use database logging or error responses.

**Issue:** JWT verification fails with anon key.
**Solution:** Verify JWT settings in function deployment configuration.

### AWS Lambda

**Issue:** Cold start timeout.
**Solution:** Optimize initialization code, use provisioned concurrency.

**Issue:** /tmp directory cleared between invocations.
**Solution:** Don't rely on /tmp for persistent storage.

### Cloudflare Workers

**Issue:** No access to Node.js APIs.
**Solution:** Use Web APIs or Cloudflare-specific alternatives.

**Issue:** 50ms CPU time limit.
**Solution:** Offload heavy computation to Durable Objects or external services.

## Debugging Strategies by Symptom

**Symptom:** Feature never triggers
- Check conditional logic (always false?)
- Verify function is being called
- Look for early returns

**Symptom:** No logs appear
- Console.log may not work in this platform
- Use database logging instead
- Check log level settings

**Symptom:** Works locally, fails in production
- Environment variables not set
- Runtime version differences
- RLS policies in production only

**Symptom:** Intermittent failures
- Race condition
- Timeout under load
- External service unreliable

**Symptom:** Data not updating
- RLS policy blocking write
- Transaction not committed
- Type mismatch in WHERE clause

## Prevention Checklist

- Always verify database defaults match code assumptions
- Use strict equality (===) and explicit type checking
- Await all async operations or handle errors explicitly
- Test with actual production environment variables
- Verify RLS policies allow expected operations
- Use atomic database operations for counters
- Document platform-specific limitations
- Add comprehensive error logging
