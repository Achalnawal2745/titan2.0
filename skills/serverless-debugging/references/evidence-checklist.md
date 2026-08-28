# Evidence Gathering Checklist

Use this comprehensive checklist to gather evidence from all layers before forming hypotheses.

## Database Layer

### Data State
- [ ] Query actual current data (not cached or assumed)
- [ ] Check row counts match expectations
- [ ] Verify timestamps are updating
- [ ] Look for NULL vs 0 vs empty string
- [ ] Check for unexpected default values
- [ ] Verify foreign key relationships
- [ ] Check for orphaned records

### Schema
- [ ] Verify column exists and has correct type
- [ ] Check default values in schema
- [ ] Verify constraints (NOT NULL, UNIQUE, CHECK)
- [ ] Check indexes exist for queried columns
- [ ] Verify triggers are not interfering

### Permissions
- [ ] Check RLS policies for the table
- [ ] Verify user role has required permissions
- [ ] Test with service role to rule out RLS
- [ ] Check column-level permissions

## Code Layer

### Deployment Verification
- [ ] Confirm function version number
- [ ] Verify deployed code matches local code
- [ ] Check deployment timestamp
- [ ] Confirm deployment status is ACTIVE
- [ ] Review deployment logs for errors

### Logic Analysis
- [ ] Identify all conditional branches
- [ ] Check each condition can be true
- [ ] Verify type checks (===, ==, typeof)
- [ ] Look for early returns that skip code
- [ ] Check for try-catch blocks hiding errors
- [ ] Verify async/await usage
- [ ] Check promise chains are complete

### Type Safety
- [ ] Check for type coercion issues (0 vs null)
- [ ] Verify string vs number comparisons
- [ ] Check undefined vs null handling
- [ ] Look for implicit type conversions
- [ ] Verify JSON parsing/stringifying

## Runtime Layer

### Logs
- [ ] Check what logs ARE appearing
- [ ] Note what SHOULD appear but doesn't
- [ ] Look for error patterns
- [ ] Check log timestamps for timing issues
- [ ] Verify log level settings
- [ ] Check if logging works at all (test with simple log)

### Execution
- [ ] Verify function is being called
- [ ] Check execution time (timeout issues?)
- [ ] Look for memory usage issues
- [ ] Check for rate limiting
- [ ] Verify cold start behavior
- [ ] Check concurrent execution limits

### Errors
- [ ] Look for silent failures (no error, no success)
- [ ] Check for caught but unlogged errors
- [ ] Review error response codes
- [ ] Check for timeout errors
- [ ] Look for out-of-memory errors

## Environment Layer

### Configuration
- [ ] Verify all environment variables are set
- [ ] Check environment variable values (not just existence)
- [ ] Verify secrets are accessible
- [ ] Check configuration file is loaded
- [ ] Verify feature flags are enabled

### External Dependencies
- [ ] Check API keys are valid
- [ ] Verify external service is reachable
- [ ] Check rate limits on external APIs
- [ ] Verify webhook URLs are correct
- [ ] Check CORS settings if applicable

### Platform-Specific
- [ ] Check runtime version matches expectations
- [ ] Verify memory/CPU limits
- [ ] Check timeout settings
- [ ] Verify network access is allowed
- [ ] Check for platform-specific limitations

## Comparison Analysis

### Working vs Broken
- [ ] Identify similar features that DO work
- [ ] Compare code differences
- [ ] Compare data differences
- [ ] Compare environment differences
- [ ] Note when it last worked (if ever)

### Expected vs Actual
- [ ] Document expected behavior
- [ ] Document actual behavior
- [ ] Identify specific differences
- [ ] Check edge cases
- [ ] Test with minimal input

## Testing

### Isolation
- [ ] Create minimal reproduction case
- [ ] Test individual components
- [ ] Test with mock data
- [ ] Test in different environments
- [ ] Test with different user roles

### Verification
- [ ] Can you trigger the issue consistently?
- [ ] Can you trigger success in any scenario?
- [ ] What's the simplest case that works?
- [ ] What's the simplest case that fails?

## Documentation

### Record Findings
- [ ] Document all evidence gathered
- [ ] Note what was checked and results
- [ ] Record timestamps of tests
- [ ] Save query results
- [ ] Screenshot relevant logs or UI

### Pattern Recognition
- [ ] Does this match a known bug pattern?
- [ ] Have similar issues occurred before?
- [ ] Are there related open issues?
- [ ] Check documentation for known limitations

## Red Flags

These patterns often indicate specific bug types:

- **No logs at all** → Logging doesn't work in this environment
- **Code exists but never runs** → Conditional always false or early return
- **Works locally, fails in production** → Environment variable or permission issue
- **Intermittent failures** → Race condition or timeout
- **Data exists but not retrieved** → RLS policy or type mismatch in query
- **Function times out** → Infinite loop, missing await, or external service hang
- **Silent failure** → Error caught but not logged, or fire-and-forget operation

## Next Steps

After completing this checklist:

1. Review all evidence gathered
2. Identify patterns and anomalies
3. Form specific, testable hypotheses
4. Proceed to Phase 3 (Hypothesis Formation)
