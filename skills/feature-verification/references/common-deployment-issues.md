# Common Deployment Issues

This reference documents frequently encountered deployment issues and their solutions.

---

## Issue 1: Missing Files in Deployment

**Symptoms:**
- Import errors at runtime
- "Module not found" errors
- Functions reference undefined variables/functions

**Root Cause:**
Deployment tools may not include all files, especially:
- New modules added to existing functions
- Files in subdirectories
- Configuration files

**Solution:**
```bash
# When deploying via MCP, explicitly list ALL files:
{
  "name": "function-name",
  "files": [
    {"name": "index.ts", "content": "..."},
    {"name": "module1.ts", "content": "..."},
    {"name": "module2.ts", "content": "..."}
  ]
}
```

**Prevention:**
- Always verify deployment includes all files
- Check deployed version number increases
- Test imports immediately after deployment

---

## Issue 2: JWT Verification Resets

**Symptoms:**
- 401 Unauthorized errors after deployment
- Functions that worked suddenly require authentication
- Service role keys rejected

**Root Cause:**
Supabase Edge Functions default to `verify_jwt=true`. When deploying via MCP, this setting may not persist from `config.toml`.

**Solution:**
```bash
# Option 1: Disable via dashboard
# Navigate to function settings → Details → Disable JWT verification

# Option 2: Deploy via CLI (respects config.toml)
supabase functions deploy function-name

# Option 3: Set in deployment payload
{
  "verify_jwt": false,
  ...
}
```

**Prevention:**
- Document JWT requirements in deployment guide
- Verify JWT setting after each deployment
- Use CLI deployment when possible

---

## Issue 3: Environment Variables Not Set

**Symptoms:**
- Functions fail with "undefined" errors
- API calls fail with authentication errors
- Database connections fail

**Root Cause:**
Edge Functions need environment variables set at project level, not in code.

**Solution:**
```bash
# Check if variable exists
echo $VARIABLE_NAME

# Set via Supabase dashboard:
# Project Settings → Edge Functions → Secrets → Add secret

# Or via CLI:
supabase secrets set VARIABLE_NAME=value
```

**Common Variables:**
- `OPENAI_API_KEY` - For AI/LLM features
- `SUPABASE_SERVICE_ROLE_KEY` - For internal function calls
- `SUPABASE_URL` - Project URL

**Prevention:**
- Document required environment variables
- Verify variables are set before deployment
- Test with actual API calls after deployment

---

## Issue 4: Async Operations Not Completing

**Symptoms:**
- Database updates don't persist
- Functions return before operations complete
- Intermittent failures

**Root Cause:**
Async operations started but not awaited, causing race conditions.

**Solution:**
```typescript
// ❌ Wrong - doesn't wait
extractMemories(data)
  .then(() => updateDatabase())
  .catch(err => console.error(err));

// ✅ Better - waits for completion
await extractMemories(data);
await updateDatabase();

// ✅ Best - fire and forget with guaranteed update
await updateDatabase(); // Update first
extractMemories(data).catch(err => console.error(err)); // Then extract
```

**Prevention:**
- Use `await` for critical operations
- Update state BEFORE async operations
- Add logging to track completion

---

## Issue 5: Silent Failures

**Symptoms:**
- Code appears to run but nothing happens
- No errors in logs
- Database not updated

**Root Cause:**
Errors caught and logged but not propagated, making debugging difficult.

**Solution:**
```typescript
// ❌ Wrong - error hidden
try {
  await operation();
} catch (err) {
  console.error(err); // Logged but not visible
}

// ✅ Better - error visible
try {
  await operation();
} catch (err) {
  console.error('[OPERATION] Failed:', err);
  throw err; // Re-throw for visibility
}

// ✅ Best - defensive updates
await updateStatus('pending');
try {
  await operation();
  await updateStatus('success');
} catch (err) {
  await updateStatus('failed');
  console.error('[OPERATION] Failed:', err);
}
```

**Prevention:**
- Add descriptive logging with prefixes
- Update status before/after operations
- Re-throw errors when appropriate

---

## Issue 6: Database Permission Issues

**Symptoms:**
- SELECT works but INSERT/UPDATE fails
- Service role key rejected
- RLS policy blocks operations

**Root Cause:**
Row Level Security (RLS) policies may block operations even with service role key.

**Solution:**
```sql
-- Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'your_table';

-- Disable RLS for service role (if appropriate)
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;
ALTER TABLE your_table FORCE ROW LEVEL SECURITY;

CREATE POLICY "Service role bypass" ON your_table
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
```

**Prevention:**
- Document RLS requirements
- Test with service role key
- Verify policies allow intended operations

---

## Issue 7: Import Path Errors

**Symptoms:**
- "Module not found" errors
- Functions work locally but fail in deployment
- Relative imports fail

**Root Cause:**
Deno runtime in Supabase requires specific import patterns.

**Solution:**
```typescript
// ❌ Wrong - may fail in deployment
import { func } from './module';

// ✅ Better - explicit extension
import { func } from './module.ts';

// ✅ Best - absolute from entrypoint
import { func } from './module.ts'; // From index.ts
```

**Prevention:**
- Always use `.ts` extension
- Test deployment immediately
- Use relative paths from entrypoint

---

## Debugging Workflow

When encountering deployment issues:

1. **Verify Deployment**
   - Check version number increased
   - Confirm all files included
   - Verify JWT settings

2. **Check Environment**
   - Verify environment variables set
   - Test API keys work
   - Confirm database access

3. **Test Runtime**
   - Add logging statements
   - Test with simple inputs
   - Check error logs

4. **Verify Persistence**
   - Query database directly
   - Check data format
   - Verify RLS policies

5. **Document Findings**
   - Record issue and solution
   - Update this reference
   - Share with team

---

## Quick Reference

| Issue | Symptom | Solution |
|-------|---------|----------|
| Missing files | Import errors | Deploy with all files explicitly listed |
| JWT resets | 401 errors | Disable JWT via dashboard or CLI |
| Missing env vars | Undefined errors | Set secrets in project settings |
| Async not completing | Intermittent failures | Use await or update state first |
| Silent failures | No errors, no results | Add logging, re-throw errors |
| Permission issues | RLS blocks operations | Check policies, add service role bypass |
| Import errors | Module not found | Use .ts extension, relative paths |
