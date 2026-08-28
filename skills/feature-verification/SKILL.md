---
name: "feature-verification"
description: "Specialized skill for feature verification workflows and automation."
---

# Feature Verification

Systematic 4-phase process for verifying new features work correctly across all layers: database, code deployment, runtime execution, and end-to-end functionality.

## When to Use

- After implementing new features
- When features "should work" but don't behave as expected
- When verifying complex integrations
- After deployments to production
- When debugging deployment-related issues

## Core Methodology

Follow these 4 phases in order. Each phase builds on the previous one.

### Phase 1: Root Cause Investigation

Gather evidence from all layers before forming hypotheses.

**Layer 1: Database Schema**
- Verify tables and columns exist
- Check data types and constraints
- Confirm indexes and relationships
- Test RLS policies

**Layer 2: Code Deployment**
- Verify all files are deployed
- Check deployment version number
- Confirm imports are correct
- Validate environment variables

**Layer 3: Runtime Execution**
- Add logging to track execution paths
- Verify functions are being called
- Check async operations complete
- Review error logs

**Layer 4: End-to-End Testing**
- Test complete user workflows
- Verify data persistence
- Check related features still work
- Validate error handling

**Detailed checklists:** See `references/verification-checklist.md`

### Phase 2: Pattern Analysis

Compare expected vs actual behavior to identify patterns.

**Questions to ask:**
- What should happen vs what actually happens?
- Are there similar working examples to compare against?
- Is this issue consistent or intermittent?
- What changed recently that might affect this?

**Look for patterns:**
- Configuration differences between working/broken features
- Timing issues (async operations)
- Permission/authentication issues
- Deployment-specific problems

### Phase 3: Hypothesis and Testing

Form testable hypotheses based on evidence, then test systematically.

**Hypothesis template:**
```
Hypothesis: [Description of suspected root cause]
Test: [How to verify this hypothesis]
Evidence: [What evidence supports/refutes this]
Conclusion: ✅ CONFIRMED / ❌ RULED OUT / ❓ INCONCLUSIVE
```

**Test each hypothesis:**
- Start with most likely causes
- Rule out possibilities systematically
- Document evidence for each test
- Don't skip to solutions without testing

**Common root causes:** See `references/common-deployment-issues.md`

### Phase 4: Implementation and Verification

Fix identified issues and verify the fixes work.

**For each fix:**
1. Document what you're changing and why
2. Implement the fix
3. Redeploy if necessary
4. Retest the feature
5. Verify related features still work

**Make fixes robust:**
- Add logging for future debugging
- Handle edge cases
- Update documentation
- Consider long-term improvements

## Deliverables

Create a verification report documenting:
1. What was tested
2. Evidence gathered from each layer
3. Patterns identified
4. Hypotheses tested
5. Root causes found
6. Fixes implemented
7. Recommendations

**Use template:** `templates/verification_report_template.md`

## Best Practices

**Evidence Over Assumptions**
- Gather data before forming theories
- Document what works AND what doesn't
- Test hypotheses systematically

**Bottom-Up Verification**
- Start with database (foundation)
- Move to code deployment
- Check runtime execution
- Test end-to-end last

**Work Backwards on Failures**
- If end-to-end fails, check runtime
- If runtime fails, check deployment
- If deployment fails, check code
- If code fails, check schema

**Document Everything**
- Create detailed verification reports
- Record evidence at each layer
- Document solutions for future reference
- Share knowledge with team

## Example: Verifying Conversation Threading

**Phase 1: Investigation**
```
Layer 1 (Database):
✅ wade_conversations table exists
✅ wade_messages table exists
✅ All columns present

Layer 2 (Deployment):
✅ wade-brain v47 deployed
✅ conversation.ts included
⚠️  JWT verification enabled (should be disabled)

Layer 3 (Runtime):
❌ Messages not being stored
❌ last_extraction_at not updating

Layer 4 (End-to-End):
❌ Conversation history not working
```

**Phase 2: Pattern Analysis**
- Expected: Messages stored after each exchange
- Actual: No messages in database
- Pattern: JWT verification blocking requests

**Phase 3: Hypothesis Testing**
```
Hypothesis: JWT verification is rejecting service role key
Test: Disable JWT and retry
Evidence: After disabling, requests succeed
Conclusion: ✅ CONFIRMED
```

**Phase 4: Implementation**
- Disabled JWT verification via dashboard
- Redeployed function
- Retested: ✅ Messages now storing correctly
- Documented: JWT must be disabled for internal services

## Supporting Resources

- `references/verification-checklist.md` - Layer-by-layer verification checklists
- `references/common-deployment-issues.md` - Known issues and solutions
- `templates/verification_report_template.md` - Standard report format

## Related Skills

- **systematic-debugging** - When verification reveals issues or bugs, use this skill to identify root causes and implement fixes

## Tips

**For Supabase Edge Functions:**
- Always verify JWT settings after deployment
- Check environment variables are set
- Include all files in deployment payload
- Test with actual API calls, not just code review

**For Database Changes:**
- Verify migrations applied successfully
- Check RLS policies don't block operations
- Test with service role key
- Query directly to confirm data structure

**For Async Operations:**
- Add logging to track completion
- Update state before async operations
- Use await for critical operations
- Handle errors explicitly

**For Silent Failures:**
- Add descriptive logging with prefixes
- Update status before/after operations
- Re-throw errors when appropriate
- Check logs even when "no errors" reported
