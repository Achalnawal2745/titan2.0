# Distributed Systems Debugging

Debugging distributed systems (Edge Functions, APIs, databases, microservices) requires systematic investigation across multiple layers. This guide extends the 4-phase systematic debugging process with patterns specific to distributed architectures.

## When to Use This Guide

Use when debugging:
- Edge Functions (Supabase, Vercel, Cloudflare Workers)
- API → Service → Database chains
- Microservices architectures
- Multi-component systems with authentication layers
- Systems with configuration spread across multiple services

## Key Distributed Systems Patterns

### Pattern 1: Configuration vs Code Issues

**Problem:** Not all bugs are in code. Many distributed system issues are configuration mismatches.

**Investigation checklist:**
1. **Environment variables** - Are secrets/keys set in all services?
2. **Authentication settings** - JWT verification, API keys, service roles
3. **Network configuration** - CORS, allowed origins, timeouts
4. **Version mismatches** - Different services running different configs
5. **Deployment state** - Is the latest code actually deployed?

**Example from Wade Memory Fix:**
```
Issue: Memory storage returns 401 errors
Code: ✅ Correct (sending Authorization header)
Config: ❌ Wrong (verify_jwt=true instead of false)
Fix: Configuration change, not code change
```

### Pattern 2: Compare Configurations Across Services

**When:** System has multiple similar services (e.g., 26 Edge Functions)

**Process:**
1. List all similar services and their configurations
2. Look for outliers (1 service configured differently than others)
3. Determine if outlier is intentional or misconfiguration
4. Compare against service purpose (internal vs user-facing)

**Example:**
```
21/26 Edge Functions: verify_jwt=false (internal services)
5/26 Edge Functions: verify_jwt=true (user-facing endpoints)
wade-memory: verify_jwt=true ❌ (should be false - it's internal)
```

**Red flag:** When one service is configured differently without clear reason.

### Pattern 3: Multi-Level Testing

**Problem:** End-to-end tests pass/fail but don't reveal WHERE the issue is.

**Process:** Test each layer independently, from bottom to top:

```
Layer 1: Database
  ✅ Test: Can I query the data directly?
  ✅ Test: Does the data have required fields?

Layer 2: Storage Service (e.g., wade-memory)
  ✅ Test: Can I call it directly with curl?
  ✅ Test: Does it return 200 or error code?

Layer 3: Orchestration Service (e.g., wade-brain)
  ✅ Test: Does it call Layer 2 correctly?
  ✅ Test: Does it handle Layer 2 responses?

Layer 4: User Interface
  ✅ Test: Does it display Layer 3 responses?
```

**Benefit:** Isolates the failing layer instead of guessing.

### Pattern 4: Autonomous Debugging with MCP Connectors

**When:** You have MCP connectors for the services you're debugging.

**Available operations:**
- Deploy functions directly
- Query databases
- Check logs
- Execute SQL
- List configurations

**Process:**
1. Use MCP tools to gather evidence (don't ask user to run commands)
2. Deploy fixes directly through MCP
3. Verify fixes using MCP queries
4. Only involve user when authentication required

**Example:**
```bash
# Instead of asking user to run:
# "Can you run: supabase functions deploy wade-memory"

# Do it yourself:
manus-mcp-cli tool call deploy_edge_function --server supabase --input '{...}'
```

**Benefit:** Faster iteration, less context switching for user.

### Pattern 5: Partial Success Reveals Hidden Issues

**Pattern:** When something "partially works," there are likely multiple issues.

**Example:**
```
✅ Memory storage works
✅ Memory listing works
❌ Memory search fails
```

**This pattern reveals:** Storage and listing don't need X, but search does need X.

**Investigation:**
1. What does search do that storage/listing don't?
2. Answer: Search generates embeddings, storage uses pre-generated embeddings
3. Hypothesis: Embedding generation is failing
4. Root cause: Missing OPENAI_API_KEY environment variable

**Red flag:** Stopping after first success without testing full functionality.

### Pattern 6: Authentication Chain Debugging

**Problem:** Request fails with 401, but multiple auth layers exist.

**Investigation layers:**
```
1. Is auth token/key being SENT?
   → Check request headers in code

2. Is auth token/key VALID?
   → Check if key is expired, correct format

3. Is auth token/key EXPECTED by service?
   → Check service configuration (JWT vs API key)

4. Is auth token/key PROPAGATED through layers?
   → Check if middleware strips/modifies headers
```

**Example from Wade Memory:**
```
Layer 1: Wade-brain sends Authorization header ✅
Layer 2: Wade-memory receives header ✅
Layer 3: Wade-memory expects JWT, receives service key ❌
Layer 4: Wade-memory rejects with 401 ❌
```

**Fix:** Change Layer 3 expectation (verify_jwt=false)

## Case Study: Wade Memory System Debug

This real-world example demonstrates all 4 phases applied to a distributed system.

### Background
- **System:** Wade AI assistant with long-term memory
- **Components:** wade-brain (orchestrator) → wade-memory (storage) → database
- **Issue:** Memory inconsistent - some memories work, others don't
- **Symptom:** Test 3 (old memory) works, Tests 1,2,4 (new memories) fail

### Phase 1: Root Cause Investigation

**Step 1: Gather Evidence**
```bash
# Check database - are memories being stored?
SELECT * FROM wade_memories ORDER BY created_at DESC LIMIT 5;
Result: ✅ Memories exist, including new ones

# Check RLS policies - is access blocked?
SELECT * FROM pg_policies WHERE tablename = 'wade_memories';
Result: ✅ No RLS policies blocking access

# Check logs - what errors are occurring?
manus-mcp-cli tool call get_logs --server supabase
Result: ❌ wade-memory returning 401 errors
```

**Key finding:** 401 errors on wade-memory calls, but database has the data.

**Step 2: Check Recent Changes**
- Wade-memory integration was recently added to wade-brain
- Old memory (Test 3) was stored before integration
- New memories (Tests 1,2,4) go through new integration

**Hypothesis forming:** Integration has authentication issue.

### Phase 2: Pattern Analysis

**Step 1: Compare Configurations**
```bash
# List all Edge Functions and their JWT settings
manus-mcp-cli tool call list_edge_functions --server supabase

Result:
21/26 functions: verify_jwt=false (internal services)
  - wade-brain ✅
  - google-drive ✅
  - content-engine ✅
  - research ✅
  
5/26 functions: verify_jwt=true (user-facing)
  - google-gmail (needs user OAuth)
  - instagram (needs user credentials)
  - wade-memory ❌ (WRONG - this is internal!)
```

**Pattern identified:** Wade-memory is the ONLY internal service with JWT verification enabled.

**Step 2: Understand the Difference**
- Internal services: Accept service role keys (verify_jwt=false)
- User-facing services: Require user JWTs (verify_jwt=true)
- Wade-memory: Internal service misconfigured as user-facing

### Phase 3: Hypothesis and Testing

**Hypothesis:** Wade-memory's `verify_jwt=true` is rejecting service role keys from wade-brain.

**Test 1: Direct call with service role key**
```bash
curl -X POST 'https://.../wade-memory' \
  -H "Authorization: Bearer $SERVICE_ROLE_KEY" \
  -d '{"action": "store", "content": "test"}'

Result: ❌ 401 Unauthorized
```

**Test 2: Check wade-brain code**
```typescript
// Does wade-brain send Authorization header?
headers: {
  'Authorization': `Bearer ${Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}`
}
Result: ✅ Header is sent
```

**Hypothesis confirmed:** Wade-memory expects JWT, receives service key, rejects with 401.

### Phase 4: Implementation

**Step 1: Create Test**
```bash
# Test: Store memory via wade-memory
curl -X POST 'https://.../wade-memory' \
  -H "Authorization: Bearer $SERVICE_ROLE_KEY" \
  -d '{"action": "store", "content": "test memory"}'

Expected: 200 OK
Actual: 401 Unauthorized
```

**Step 2: Implement Fix**
```bash
# Deploy wade-memory with verify_jwt=false
manus-mcp-cli tool call deploy_edge_function --server supabase --input '{
  "name": "wade-memory",
  "verify_jwt": false,
  ...
}'

Result: Deployed as v10
```

**Step 3: Verify Fix**
```bash
# Rerun test
curl -X POST 'https://.../wade-memory' ...

Result: ✅ 200 OK
{"success": true, "memory_id": "..."}
```

**Step 4: Test End-to-End**
```bash
# Test through wade-brain
curl -X POST 'https://.../wade-brain' \
  -d '{"message": "Remember: I like pizza"}'

Result: ✅ Memory stored successfully
```

**Step 5: Check Logs**
```
BEFORE (v9):
wade-memory | POST | 401 ❌
wade-memory | POST | 401 ❌

AFTER (v10):
wade-memory | POST | 200 ✅
wade-memory | POST | 200 ✅
```

### Phase 4 Continued: Second Issue Found

**During verification, discovered partial success:**
- ✅ Memory storage works
- ✅ Memory listing works
- ❌ Memory search returns empty results

**Return to Phase 1 for second issue:**

**Evidence:**
```bash
# Direct search test
curl -X POST 'https://.../wade-memory' \
  -d '{"action": "search", "query": "coffee", "match_threshold": 0.6}'

Result: {"memories": [], "count": 0}

# But memory exists!
SELECT * FROM wade_memories WHERE content LIKE '%coffee%';
Result: ✅ Memory found with embedding
```

**Pattern:** Search needs to generate embedding for query, storage uses pre-generated embedding.

**Hypothesis:** OpenAI API key missing from wade-memory environment.

**Fix:** Add OPENAI_API_KEY to Supabase Edge Functions secrets (requires user authentication).

### Key Learnings from This Case

1. **Two distinct issues** - JWT config + missing API key
2. **Configuration over code** - Both fixes were config, not code changes
3. **Pattern analysis** - Comparing 26 functions revealed outlier
4. **Multi-level testing** - Tested storage, listing, search independently
5. **Partial success** - First fix revealed second issue
6. **Autonomous debugging** - Used MCP to deploy and test without user commands

## Quick Reference: Distributed Systems Checklist

When debugging distributed systems, check:

**Configuration:**
- [ ] Environment variables set in all services?
- [ ] Authentication settings correct for service type?
- [ ] CORS/network settings allow communication?
- [ ] Latest code actually deployed?

**Pattern Analysis:**
- [ ] Compared config against similar working services?
- [ ] Identified outliers or misconfigurations?
- [ ] Checked if service is internal vs user-facing?

**Multi-Level Testing:**
- [ ] Tested database layer directly?
- [ ] Tested each service independently?
- [ ] Tested service-to-service communication?
- [ ] Tested end-to-end flow?

**Authentication Chain:**
- [ ] Is auth token being sent?
- [ ] Is auth token valid?
- [ ] Is auth token expected by service?
- [ ] Is auth token propagated correctly?

**Partial Success:**
- [ ] Tested ALL functionality, not just one path?
- [ ] Identified what works vs what doesn't?
- [ ] Determined what the working path has that failing path doesn't?

## Tools for Distributed Systems Debugging

### MCP Connectors
- **Supabase MCP:** Deploy functions, query database, check logs
- **GitHub MCP:** Check recent commits, compare branches
- **API testing tools:** curl, Postman, direct HTTP calls

### Logging Strategies
```bash
# Check Edge Function logs
manus-mcp-cli tool call get_logs --server supabase

# Check specific function
manus-mcp-cli tool call get_logs --server supabase \
  --input '{"service": "edge-function"}'

# Look for error patterns
grep "401\|500\|error" logs.txt
```

### Configuration Comparison
```bash
# List all functions
manus-mcp-cli tool call list_edge_functions --server supabase

# Get specific function config
manus-mcp-cli tool call get_edge_function --server supabase \
  --input '{"function_slug": "wade-memory"}'

# Compare against working function
manus-mcp-cli tool call get_edge_function --server supabase \
  --input '{"function_slug": "google-drive"}'
```

### Database Verification
```bash
# Check if data exists
manus-mcp-cli tool call execute_sql --server supabase \
  --input '{"query": "SELECT * FROM table LIMIT 5"}'

# Check data structure
manus-mcp-cli tool call execute_sql --server supabase \
  --input '{"query": "SELECT column_name FROM information_schema.columns WHERE table_name = '\''table'\''"}'
```

## Common Distributed Systems Anti-Patterns

### Anti-Pattern 1: Assuming Code When It's Config
**Symptom:** "The code looks right but it doesn't work"  
**Reality:** Code is right, configuration is wrong  
**Fix:** Check environment variables, feature flags, deployment state

### Anti-Pattern 2: Testing Only End-to-End
**Symptom:** "It fails but I don't know where"  
**Reality:** Multiple layers, one is broken  
**Fix:** Test each layer independently

### Anti-Pattern 3: Stopping at First Success
**Symptom:** "Storage works, ship it!"  
**Reality:** Storage works but search doesn't  
**Fix:** Test all functionality, not just one path

### Anti-Pattern 4: Manual Testing Only
**Symptom:** "It works when I test manually"  
**Reality:** Different auth context, different environment  
**Fix:** Test in actual deployment environment

### Anti-Pattern 5: Guessing at Auth Issues
**Symptom:** "Maybe the key is wrong?"  
**Reality:** Key is right, service expects different auth type  
**Fix:** Trace auth chain layer by layer

## Summary

Distributed systems debugging requires:
1. **Configuration awareness** - Not all bugs are code
2. **Pattern comparison** - Compare against working services
3. **Multi-level testing** - Test each layer independently
4. **Autonomous tools** - Use MCP connectors for faster iteration
5. **Partial success analysis** - Test all paths, not just one
6. **Systematic process** - Follow all 4 phases, don't skip

The same 4-phase systematic debugging process applies, but with distributed-systems-specific investigation techniques.
