# Feature Verification Checklist

This checklist provides a systematic approach to verifying new features across multiple layers.

---

## Layer 1: Database Schema Verification

Use when features involve database changes.

**Checklist:**
- [ ] All required tables exist
- [ ] All required columns exist with correct types
- [ ] Indexes are created for performance
- [ ] Foreign key relationships are correct
- [ ] RLS (Row Level Security) policies are configured
- [ ] Migrations have been applied successfully
- [ ] Sample data can be inserted and queried

**Tools:**
- `manus-mcp-cli tool call execute_sql` - Query database schema
- `\d table_name` in psql - Describe table structure

**Example:**
```sql
-- Check if table exists
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'wade_conversations';

-- Check columns
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'wade_conversations';
```

---

## Layer 2: Code Deployment Verification

Use when features involve new code or file changes.

**Checklist:**
- [ ] All new files are included in deployment
- [ ] Import statements are correct
- [ ] Dependencies are available in runtime
- [ ] Environment variables are set
- [ ] Configuration files are deployed
- [ ] Deployment succeeded without errors
- [ ] Correct version is deployed

**Tools:**
- `manus-mcp-cli tool call get_edge_function` - Check deployed function details
- `manus-mcp-cli tool call deploy_edge_function` - Deploy with all files
- Git logs - Verify commits are pushed

**Common Issues:**
- Missing files in deployment (e.g., new modules not included)
- Import paths incorrect (relative vs absolute)
- Environment variables not set
- Config files not deployed

---

## Layer 3: Runtime Execution Verification

Use when code is deployed but not behaving as expected.

**Checklist:**
- [ ] Functions are being called
- [ ] Parameters are passed correctly
- [ ] Return values are as expected
- [ ] Async operations are completing
- [ ] Database updates are succeeding
- [ ] No runtime errors in logs
- [ ] Performance is acceptable

**Tools:**
- `manus-mcp-cli tool call get_logs` - Check Edge Function logs
- `console.log()` statements - Add logging to track execution
- Database queries - Verify data changes

**Common Issues:**
- Async operations not awaited
- Silent failures (errors caught but not logged)
- Database permission issues
- Incorrect function parameters

---

## Layer 4: End-to-End Testing Verification

Use to verify complete user workflows.

**Checklist:**
- [ ] User can trigger the feature
- [ ] Feature produces expected output
- [ ] Data is persisted correctly
- [ ] Related features still work
- [ ] Error cases are handled
- [ ] Performance is acceptable
- [ ] User experience is smooth

**Tools:**
- `curl` - Test API endpoints
- Browser - Test UI interactions
- Database queries - Verify data persistence

**Test Pattern:**
```bash
# Test 1: Basic functionality
curl -X POST 'https://[project].supabase.co/functions/v1/[function]' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $KEY" \
  -d '{"test": "data"}'

# Test 2: Verify persistence
# Query database to confirm data was stored

# Test 3: Verify retrieval
# Call function again to retrieve stored data
```

---

## Multi-Layer Verification Strategy

**Bottom-Up Approach:**
1. Start with Layer 1 (Database) - Foundation must be solid
2. Move to Layer 2 (Code) - Verify deployment
3. Check Layer 3 (Runtime) - Confirm execution
4. Test Layer 4 (End-to-End) - Validate user experience

**When Issues Arise:**
- If Layer 1 fails → Fix schema before proceeding
- If Layer 2 fails → Redeploy with correct files
- If Layer 3 fails → Add logging and check runtime errors
- If Layer 4 fails → Work backwards through layers

**Evidence-Based Debugging:**
- Gather evidence at each layer BEFORE forming hypotheses
- Document what works AND what doesn't
- Compare expected vs actual behavior
- Test hypotheses systematically

---

## Verification Report Structure

After completing verification, create a report using the template in `templates/verification_report_template.md`.

The report should include:
1. Executive summary (what works, what doesn't)
2. Evidence from all 4 layers
3. Pattern analysis (expected vs actual)
4. Hypothesis testing results
5. Recommendations for fixes

This creates a permanent record for future debugging and knowledge sharing.
