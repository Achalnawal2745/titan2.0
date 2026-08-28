# Integration Audit Checklist

Use this checklist to systematically audit external service integrations for reliability, security, and error handling.

## 1. Error Handling & Retry Logic

**Purpose:** Gracefully handle external service failures

**Check for:**
- [ ] All API calls wrapped in try-catch
- [ ] Retry logic with exponential backoff for transient failures
- [ ] Circuit breaker pattern for repeated failures
- [ ] Fallback behavior when service unavailable

**Example:**
```typescript
// ❌ No retry logic:
const response = await fetch(humeApiUrl);

// ✅ With retry logic:
const response = await retryWithBackoff(
  () => fetch(humeApiUrl),
  { maxRetries: 3, baseDelay: 1000 }
);
```

**Retry Strategy:**
- Transient errors (network, timeout): Retry with backoff
- Client errors (400, 401, 403): Don't retry
- Server errors (500, 503): Retry with backoff
- Rate limit errors (429): Retry after delay specified in headers

---

## 2. Timeout Configuration

**Purpose:** Prevent hanging requests

**Check for:**
- [ ] All external API calls have timeouts
- [ ] Timeout values appropriate for operation (short for health checks, longer for file uploads)
- [ ] Timeout errors handled gracefully

**Recommended Timeouts:**
- Health checks: 5 seconds
- Simple API calls: 10 seconds
- File uploads: 60 seconds
- Long-running operations: 120 seconds

---

## 3. API Key & Credential Management

**Purpose:** Secure access to external services

**Check for:**
- [ ] API keys stored in environment variables (not hardcoded)
- [ ] Credentials never logged or exposed in errors
- [ ] API keys rotated regularly
- [ ] Separate keys for dev/staging/production

**Example:**
```typescript
// ❌ Hardcoded API key:
const apiKey = "sk_live_abc123";

// ✅ From environment:
const apiKey = process.env.HUME_API_KEY;

// ❌ API key in error message:
throw new Error(`Hume API failed with key ${apiKey}`);

// ✅ No sensitive data in error:
throw new Error('Hume API request failed');
```

---

## 4. Webhook Security

**Purpose:** Verify webhook requests are authentic

**Check for:**
- [ ] Webhook signature verification
- [ ] HTTPS-only webhook endpoints
- [ ] Webhook replay attack prevention
- [ ] Rate limiting on webhook endpoints

**Example (Twilio):**
```typescript
import twilio from 'twilio';

app.post('/api/twilio/webhook', (req, res) => {
  const signature = req.headers['x-twilio-signature'];
  const url = `https://${req.headers.host}${req.url}`;
  
  // ✅ Verify signature:
  if (!twilio.validateRequest(TWILIO_AUTH_TOKEN, signature, url, req.body)) {
    return res.status(403).send('Invalid signature');
  }
  
  // Process webhook...
});
```

---

## 5. Resource Cleanup

**Purpose:** Prevent resource accumulation

**Check for:**
- [ ] Temporary resources cleaned up after use
- [ ] Background jobs to clean up old/expired resources
- [ ] No unbounded resource creation

**Common Issues:**
- Hume AI configs created but never deleted
- Temporary files not cleaned up
- Expired session codes not removed
- Old webhooks not deregistered

**Recommendation:** Add cleanup jobs or TTL-based deletion

---

## 6. Rate Limit Handling

**Purpose:** Respect external service limits

**Check for:**
- [ ] Rate limit headers monitored
- [ ] Requests throttled to stay under limits
- [ ] 429 responses handled with retry-after delay
- [ ] Quota tracking for services with daily/monthly limits

---

## 7. Data Validation

**Purpose:** Ensure external data meets expectations

**Check for:**
- [ ] All external API responses validated
- [ ] No assumptions about response structure
- [ ] Graceful handling of missing/null fields
- [ ] Type checking on external data

**Example:**
```typescript
// ❌ No validation:
const configId = response.id;

// ✅ With validation:
if (!response || !response.id) {
  throw new Error('Invalid Hume API response: missing config ID');
}
const configId = response.id;
```

---

## 8. Webhook Reliability

**Purpose:** Ensure webhooks are processed reliably

**Check for:**
- [ ] Webhook endpoints return 200 quickly (process async if needed)
- [ ] Failed webhooks retried by provider (or queued locally)
- [ ] Idempotent webhook processing (handle duplicates)
- [ ] Webhook payload validation

**Pattern:**
```typescript
app.post('/api/webhook', async (req, res) => {
  // ✅ Respond immediately:
  res.status(200).send('OK');
  
  // ✅ Process asynchronously:
  processWebhookAsync(req.body).catch(err => {
    logger.error('Webhook processing failed', err);
  });
});
```

---

## 9. Connection Pooling

**Purpose:** Efficient resource usage

**Check for:**
- [ ] Database connections pooled (not created per request)
- [ ] HTTP clients reused (not created per request)
- [ ] Connection pool size appropriate for load
- [ ] Connection pool monitoring

---

## 10. Service Health Monitoring

**Purpose:** Detect integration failures early

**Check for:**
- [ ] Health check endpoints for all critical integrations
- [ ] Periodic health checks (not just on-demand)
- [ ] Alerts when integrations fail
- [ ] Graceful degradation when service unavailable

**Example Health Check:**
```typescript
app.get('/api/health', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    hume: await checkHumeAPI(),
    twilio: await checkTwilioAPI(),
    s3: await checkS3(),
  };
  
  const allHealthy = Object.values(checks).every(c => c.healthy);
  
  res.status(allHealthy ? 200 : 503).json(checks);
});
```

---

## Integration-Specific Checklists

### Hume AI Integration

- [ ] Dynamic config creation working
- [ ] Config cleanup implemented
- [ ] System prompts fit within character limits
- [ ] Error handling for config creation failures
- [ ] Retry logic for API calls

### Twilio Integration

- [ ] Webhook signature verification
- [ ] Recording callback implemented
- [ ] Call status tracking
- [ ] Error handling for failed calls
- [ ] Phone number format validation

### S3 Storage Integration

- [ ] File size limits enforced
- [ ] Content type validation
- [ ] Upload error handling
- [ ] Presigned URL expiration configured
- [ ] Public/private access configured correctly

### Database Integration (Supabase/MySQL)

- [ ] Connection pooling configured
- [ ] Query timeout configured
- [ ] Transaction handling correct
- [ ] Connection pool monitoring
- [ ] Slow query logging enabled

---

## Output Format

For each issue found, document:

1. **Severity:** Critical / High / Medium / Low
2. **Issue:** Brief description
3. **Impact:** What breaks or degrades
4. **Example:** Code snippet or scenario
5. **Recommendation:** How to fix it

**Example:**
```
#### 🟡 MEDIUM: No Retry Logic for Hume API Calls
**Issue:** If Hume API fails, entire session fails
**Impact:** Poor user experience during Hume API outages
**Recommendation:** Add retry logic with exponential backoff
```
