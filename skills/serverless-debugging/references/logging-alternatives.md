# Logging Alternatives for Serverless Environments

When console.log doesn't work or isn't visible in your serverless platform, use these alternative debugging strategies.

## Database-Driven Debugging

The most reliable debugging method when logs are unavailable. The database is always accessible and writes are permanent.

### Create a Debug Log Table

```sql
CREATE TABLE debug_logs (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  function_name TEXT NOT NULL,
  checkpoint TEXT NOT NULL,
  message TEXT,
  data JSONB,
  user_id TEXT,
  request_id TEXT
);

-- Add index for querying
CREATE INDEX idx_debug_logs_function ON debug_logs(function_name, created_at DESC);
CREATE INDEX idx_debug_logs_checkpoint ON debug_logs(checkpoint);
```

### Log from Your Function

```typescript
async function logDebug(checkpoint: string, data: any) {
  await supabase.from('debug_logs').insert({
    function_name: 'wade-brain',
    checkpoint: checkpoint,
    data: data
  });
}

// Use throughout your code
await logDebug('start', { conversationId, messageCount });
await logDebug('before-extraction', { 
  messageCount, 
  lastExtraction, 
  shouldExtract: shouldExtractMemories(messageCount, lastExtraction) 
});
await logDebug('after-extraction', { success: true });
```

### Query Debug Logs

```sql
-- Recent logs for a function
SELECT * FROM debug_logs 
WHERE function_name = 'wade-brain' 
ORDER BY created_at DESC 
LIMIT 20;

-- Logs for specific checkpoint
SELECT * FROM debug_logs 
WHERE checkpoint = 'before-extraction' 
ORDER BY created_at DESC;

-- Analyze execution flow
SELECT checkpoint, COUNT(*), MAX(created_at) 
FROM debug_logs 
WHERE function_name = 'wade-brain' 
GROUP BY checkpoint;
```

### Cleanup

```sql
-- Delete old debug logs (run periodically)
DELETE FROM debug_logs WHERE created_at < NOW() - INTERVAL '7 days';
```

## Error Response Debugging

Return diagnostic information in the response for testing purposes.

### Add Debug Mode

```typescript
const DEBUG_MODE = Deno.env.get('DEBUG_MODE') === 'true';

// In your function
if (DEBUG_MODE) {
  return new Response(JSON.stringify({
    debug: {
      messageCount: messageCount,
      lastExtraction: conversation.last_extraction_at,
      shouldExtract: shouldExtractMemories(messageCount, conversation.last_extraction_at),
      conversationId: conversation.id,
      userId: user_id
    }
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
}
```

### Conditional Debug Output

```typescript
// Only return debug info if specific header is present
const debugHeader = req.headers.get('X-Debug');
if (debugHeader === 'true') {
  // Return debug info
}
```

**Warning:** Never enable debug mode in production with sensitive data. Use only for testing.

## State Inspection via Database

Use the database itself to inspect state at critical points.

### Update Columns for Debugging

```sql
-- Add temporary debug columns
ALTER TABLE wade_conversations 
ADD COLUMN debug_last_check TIMESTAMPTZ,
ADD COLUMN debug_message_count_at_check INTEGER,
ADD COLUMN debug_should_extract BOOLEAN;
```

```typescript
// Update debug columns
await supabase
  .from('wade_conversations')
  .update({
    debug_last_check: new Date().toISOString(),
    debug_message_count_at_check: messageCount,
    debug_should_extract: shouldExtractMemories(messageCount, lastExtraction)
  })
  .eq('id', conversationId);
```

### Query to Verify Logic

```sql
SELECT 
  id,
  message_count,
  last_extraction_at,
  debug_should_extract,
  debug_message_count_at_check,
  CASE 
    WHEN last_extraction_at IS NULL OR last_extraction_at = 0 
    THEN message_count >= 4
    ELSE message_count - last_extraction_at >= 10
  END as expected_should_extract
FROM wade_conversations
WHERE debug_last_check IS NOT NULL
ORDER BY debug_last_check DESC;
```

## Trace Execution with Timestamps

Create a timeline of execution by recording timestamps.

```typescript
const trace = [];

trace.push({ step: 'start', time: Date.now() });
await someOperation();
trace.push({ step: 'after-operation', time: Date.now() });
await anotherOperation();
trace.push({ step: 'after-another', time: Date.now() });

// Store trace
await supabase.from('debug_logs').insert({
  function_name: 'my-function',
  checkpoint: 'execution-trace',
  data: { 
    trace,
    durations: trace.map((t, i) => ({
      step: t.step,
      duration: i > 0 ? t.time - trace[i-1].time : 0
    }))
  }
});
```

## Exception Tracking

Catch and log all exceptions to database.

```typescript
async function executeWithTracking(fn: () => Promise<any>, operation: string) {
  try {
    const result = await fn();
    await logDebug(`${operation}-success`, { result });
    return result;
  } catch (error) {
    await logDebug(`${operation}-error`, { 
      error: String(error),
      stack: error.stack 
    });
    throw error;
  }
}

// Usage
await executeWithTracking(
  () => extractMemories(conversationId, userId),
  'memory-extraction'
);
```

## Conditional Logging

Only log when specific conditions are met to reduce noise.

```typescript
async function conditionalLog(condition: boolean, checkpoint: string, data: any) {
  if (condition) {
    await logDebug(checkpoint, data);
  }
}

// Log only when extraction should happen
await conditionalLog(
  shouldExtractMemories(messageCount, lastExtraction),
  'extraction-triggered',
  { messageCount, lastExtraction }
);
```

## Assertion Logging

Log when assumptions are violated.

```typescript
async function assertEqual(actual: any, expected: any, message: string) {
  if (actual !== expected) {
    await logDebug('assertion-failed', {
      message,
      expected,
      actual,
      stack: new Error().stack
    });
  }
}

// Usage
await assertEqual(
  typeof conversation.last_extraction_at,
  'number',
  'last_extraction_at should be a number'
);
```

## Performance Tracking

Track execution time of operations.

```typescript
async function withTiming<T>(
  fn: () => Promise<T>,
  operation: string
): Promise<T> {
  const start = Date.now();
  try {
    const result = await fn();
    const duration = Date.now() - start;
    await logDebug('timing', { operation, duration, success: true });
    return result;
  } catch (error) {
    const duration = Date.now() - start;
    await logDebug('timing', { operation, duration, success: false, error: String(error) });
    throw error;
  }
}

// Usage
const memories = await withTiming(
  () => extractMemories(conversationId, userId),
  'extract-memories'
);
```

## Code Path Tracking

Verify which code paths are executed.

```typescript
const executionPath = [];

async function trackPath(checkpoint: string) {
  executionPath.push(checkpoint);
}

// In your code
await trackPath('start');
if (condition1) {
  await trackPath('branch-a');
} else {
  await trackPath('branch-b');
}
await trackPath('end');

// Log the path
await logDebug('execution-path', { path: executionPath });
```

## Variable State Snapshots

Capture variable state at critical points.

```typescript
async function snapshot(label: string, variables: Record<string, any>) {
  await logDebug('snapshot', {
    label,
    variables,
    timestamp: Date.now()
  });
}

// Usage
await snapshot('before-extraction-check', {
  messageCount,
  lastExtraction: conversation.last_extraction_at,
  conversationId: conversation.id,
  shouldExtract: shouldExtractMemories(messageCount, conversation.last_extraction_at)
});
```

## Best Practices

**Do:**
- Use database logging for persistent debugging
- Add timestamps to all debug logs
- Include context (user_id, request_id) in logs
- Clean up debug logs periodically
- Use structured data (JSONB) for complex information

**Don't:**
- Leave debug logging enabled in production
- Log sensitive information (passwords, tokens)
- Create infinite loops with logging
- Forget to handle logging errors (use try-catch)
- Overwhelm the database with excessive logging

## Cleanup After Debugging

Once the bug is fixed, clean up debug code:

```typescript
// Remove debug logging
// await logDebug('checkpoint', data);  // DELETE

// Remove debug columns
// ALTER TABLE conversations DROP COLUMN debug_last_check;

// Remove debug mode checks
// if (DEBUG_MODE) { ... }  // DELETE

// Keep only essential error logging
try {
  await criticalOperation();
} catch (error) {
  // Keep this - production error logging
  await logError('critical-operation-failed', error);
  throw error;
}
```

## Platform-Specific Considerations

### Supabase Edge Functions
- Console.log doesn't appear in logs API
- Database logging is most reliable
- Use service role key for debug writes

### AWS Lambda
- CloudWatch Logs available but may have delay
- Use structured logging (JSON)
- Consider AWS X-Ray for tracing

### Cloudflare Workers
- Limited logging to console
- Use Durable Objects for persistent debug state
- Consider external logging service

### Vercel Edge Functions
- Console.log works but may be delayed
- Use Vercel Analytics for monitoring
- Database logging recommended for debugging
