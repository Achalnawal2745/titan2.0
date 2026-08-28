# API Audit Checklist

Use this checklist to systematically audit API endpoints for validation, error handling, security, and reliability.

## 1. Input Validation

**Purpose:** Prevent invalid data from entering the system

**Check for:**
- [ ] All inputs have Zod schema validation
- [ ] Range validation on numeric inputs (min/max)
- [ ] Format validation on strings (email, phone, URL)
- [ ] Length limits on all string inputs
- [ ] Enum validation for constrained values

**Example Issues:**
```typescript
// ❌ No range validation:
score: z.number(),

// ✅ With range validation:
score: z.number().min(0).max(100),

// ❌ No format validation:
email: z.string(),

// ✅ With format validation:
email: z.string().email(),

// ❌ No length limit:
description: z.string(),

// ✅ With length limit:
description: z.string().max(1000),
```

---

## 2. Error Handling

**Purpose:** Provide clear, actionable error messages

**Check for:**
- [ ] All endpoints use TRPCError (not generic Error)
- [ ] Appropriate error codes (NOT_FOUND, UNAUTHORIZED, BAD_REQUEST, etc.)
- [ ] Descriptive error messages (include context, not just "Error")
- [ ] No sensitive information in error messages

**Standard Pattern:**
```typescript
if (!session) {
  throw new TRPCError({
    code: 'NOT_FOUND',
    message: `Session ${sessionId} not found`,
  });
}

if (session.userId !== ctx.user.id) {
  throw new TRPCError({
    code: 'FORBIDDEN',
    message: 'You do not have permission to access this session',
  });
}
```

**Common Error Codes:**
- `NOT_FOUND` - Resource doesn't exist
- `UNAUTHORIZED` - Not logged in
- `FORBIDDEN` - Logged in but no permission
- `BAD_REQUEST` - Invalid input
- `INTERNAL_SERVER_ERROR` - Unexpected error

---

## 3. Authentication & Authorization

**Purpose:** Ensure only authorized users can access endpoints

**Check for:**
- [ ] All endpoints use appropriate procedure (`publicProcedure` vs `protectedProcedure`)
- [ ] Admin-only endpoints use `adminProcedure`
- [ ] Resource ownership verified before mutations
- [ ] No sensitive data returned to unauthorized users

**Example:**
```typescript
// ❌ No auth check:
deleteSession: publicProcedure
  .input(z.object({ sessionId: z.number() }))
  .mutation(async ({ input }) => {
    await db.delete(practiceSessions).where(eq(practiceSessions.id, input.sessionId));
  }),

// ✅ With auth and ownership check:
deleteSession: protectedProcedure
  .input(z.object({ sessionId: z.number() }))
  .mutation(async ({ input, ctx }) => {
    const session = await db.query.practiceSessions.findFirst({
      where: eq(practiceSessions.id, input.sessionId),
    });
    
    if (!session) {
      throw new TRPCError({ code: 'NOT_FOUND', message: 'Session not found' });
    }
    
    if (session.userId !== ctx.user.id) {
      throw new TRPCError({ code: 'FORBIDDEN', message: 'Not your session' });
    }
    
    await db.delete(practiceSessions).where(eq(practiceSessions.id, input.sessionId));
  }),
```

---

## 4. Rate Limiting

**Purpose:** Prevent abuse and DoS attacks

**Check for:**
- [ ] Rate limiting on expensive operations
- [ ] Rate limiting on authentication endpoints
- [ ] Rate limiting on file uploads
- [ ] Rate limiting on bulk operations

**Expensive Operations to Limit:**
- External API calls (Hume AI, Twilio, etc.)
- File uploads/downloads
- Bulk database operations
- Email sending
- Report generation

**Recommendation:** Implement rate limiting middleware (e.g., 10 requests/minute per user)

---

## 5. Pagination

**Purpose:** Prevent unbounded result sets

**Check for:**
- [ ] All list endpoints support pagination
- [ ] Default page size limits (e.g., 50 items)
- [ ] Maximum page size limits (e.g., 100 items)
- [ ] Cursor-based pagination for large datasets

**Example:**
```typescript
// ❌ No pagination:
getSessions: protectedProcedure
  .query(async ({ ctx }) => {
    return await db.query.practiceSessions.findMany({
      where: eq(practiceSessions.userId, ctx.user.id),
    });
  }),

// ✅ With pagination:
getSessions: protectedProcedure
  .input(z.object({
    limit: z.number().min(1).max(100).default(50),
    offset: z.number().min(0).default(0),
  }))
  .query(async ({ input, ctx }) => {
    return await db.query.practiceSessions.findMany({
      where: eq(practiceSessions.userId, ctx.user.id),
      limit: input.limit,
      offset: input.offset,
    });
  }),
```

---

## 6. Data Sanitization

**Purpose:** Prevent XSS and injection attacks

**Check for:**
- [ ] User-provided content sanitized before storage
- [ ] HTML stripped from text inputs (unless intentional)
- [ ] SQL injection prevented (use parameterized queries)
- [ ] No eval() or similar dangerous functions

**Common Vulnerabilities:**
- Script content not sanitized (potential XSS)
- User names not sanitized
- Search queries not escaped

---

## 7. Transaction Handling

**Purpose:** Ensure data consistency

**Check for:**
- [ ] Multi-step mutations use database transactions
- [ ] Transactions rolled back on error
- [ ] No partial updates on failure

**Example:**
```typescript
// ❌ No transaction (partial update possible):
await db.insert(practiceSessions).values(session);
await db.insert(conversationTurns).values(turns);

// ✅ With transaction:
await db.transaction(async (tx) => {
  await tx.insert(practiceSessions).values(session);
  await tx.insert(conversationTurns).values(turns);
});
```

---

## 8. Response Size Limits

**Purpose:** Prevent memory exhaustion

**Check for:**
- [ ] Large responses paginated or streamed
- [ ] File downloads use streaming (not loading into memory)
- [ ] JSON responses have reasonable size limits

---

## 9. Idempotency

**Purpose:** Safe retries for unreliable networks

**Check for:**
- [ ] POST/PUT endpoints are idempotent where possible
- [ ] Duplicate detection for critical operations
- [ ] Idempotency keys for payment/billing operations

---

## 10. API Documentation

**Purpose:** Clear contract for frontend developers

**Check for:**
- [ ] Input schemas clearly defined
- [ ] Output types exported and used
- [ ] Error cases documented
- [ ] Example requests/responses provided

---

## Output Format

For each issue found, document:

1. **Severity:** Critical / High / Medium / Low
2. **Issue:** Brief description
3. **Impact:** What breaks or degrades
4. **Example:** Code snippet showing the problem
5. **Recommendation:** How to fix it

**Example:**
```
#### 🔴 HIGH: Missing Input Validation on Critical Endpoints
**Issue:** Some endpoints don't validate input ranges or formats
**Impact:** Invalid data can be stored, causing downstream errors
**Example:**
  updateSessionScore doesn't validate score is 0-100
**Recommendation:** Add Zod validation for all input ranges, formats, and business rules
```
