# Promo Code System - Implementation Guide

This guide provides detailed workflows for implementing promo code systems.

## Discovery Workflow

### Step 1: Locate the Project

Check these locations in order:

1. **Supabase Projects**
   ```bash
   manus-mcp-cli tool call list_projects --server supabase --input '{}'
   ```

2. **Vercel Deployments**
   ```bash
   manus-mcp-cli tool call list_projects --server vercel --input '{"teamId": "TEAM_ID"}'
   ```

3. **GitHub Repositories**
   ```bash
   gh repo list --limit 100
   ```

4. **Local File System**
   - Ask user for project path
   - Common locations: `~/projects/`, `~/Documents/`, `~/Desktop/`

### Step 2: Scan for Existing Implementation

Use the discovery script:
```bash
python3 /home/ubuntu/skills/promo-code-system/scripts/discover_promo_system.py /path/to/project
```

The script will identify:
- Hardcoded discount codes
- Database tables
- API endpoints
- Stripe integration

### Step 3: Analyze Current State

Determine implementation type:

**Type A: No System**
- No promo code patterns found
- Need to build from scratch
- → Recommend Quick Start (hardcoded)

**Type B: Hardcoded System**
- Found `DISCOUNT_CODES` or similar object
- Codes defined in source code
- → Extend existing or upgrade to database

**Type C: Database System**
- Found `promo_codes` table
- Has API endpoints for validation
- → Enhance or maintain existing system

## Implementation Paths

### Path A: Quick Start (Hardcoded)

**Best for**: MVPs, small projects, <20 codes

**Time**: 5-10 minutes

**Steps**:
1. Copy `templates/hardcoded_codes_template.js`
2. Customize codes in `DISCOUNT_CODES` object
3. Add to user's server file
4. Update checkout endpoint to use `calculateDiscountedPrice()`
5. Deploy

**Pros**:
- Fast implementation
- No database changes
- Easy to understand

**Cons**:
- No usage tracking
- No expiration dates
- Must redeploy to add codes

### Path B: Database-Driven (Proper)

**Best for**: Production apps, >20 codes, need tracking

**Time**: 30-45 minutes

**Steps**:
1. Create database tables using `templates/promo_schema.sql`
2. Implement validation functions (see tech stack guides)
3. Update API endpoints for code validation
4. Add usage tracking on checkout
5. (Optional) Deploy admin panel
6. Test end-to-end

**Pros**:
- Full tracking and analytics
- Expiration dates and limits
- No redeployment needed
- Professional solution

**Cons**:
- More complex setup
- Requires database access
- More code to maintain

## Tech Stack Integration

### Node.js + Express

1. Add validation functions from `templates/hardcoded_codes_template.js`
2. Create endpoints:
   ```javascript
   app.post('/api/validate-promo-code', ...)
   app.post('/api/create-checkout', ...)
   ```
3. Integrate with Stripe checkout

### Next.js (App Router)

1. Create API routes:
   - `app/api/validate-promo/route.ts`
   - `app/api/checkout/route.ts`
2. Use server actions for validation
3. Integrate with Stripe

### Next.js (Pages Router)

1. Create API routes:
   - `pages/api/validate-promo.ts`
   - `pages/api/checkout.ts`
2. Use getServerSideProps if needed
3. Integrate with Stripe

### Python + Flask/FastAPI

See `references/tech_stack_guides.md` for Python implementation.

## Creating Reference Documentation

Always create a quick reference guide for the user:

1. Copy `templates/quick_reference_template.md`
2. Fill in placeholders:
   - `[PROJECT_NAME]`
   - `[FILE_PATH]`
   - `[CODE_EXAMPLE]`
   - etc.
3. List all active codes
4. Provide "how to add more" instructions
5. Include "how to remember" section

## Testing Checklist

### Basic Tests
- [ ] Valid code returns success
- [ ] Invalid code returns error
- [ ] Code applies correct discount
- [ ] Free code sets price to $0
- [ ] Percentage discount calculates correctly
- [ ] Amount discount calculates correctly

### Edge Cases
- [ ] Empty code
- [ ] Null code
- [ ] Case sensitivity (should be insensitive)
- [ ] Whitespace handling
- [ ] Special characters in code

### Database-Specific Tests
- [ ] Expired code rejected
- [ ] Inactive code rejected
- [ ] Max uses limit enforced
- [ ] Usage count increments
- [ ] Usage tracking records created

### Integration Tests
- [ ] Stripe checkout with discount
- [ ] $0 checkout (free code)
- [ ] Payment verification
- [ ] Results delivery after free checkout

## Common Gotchas

### Stripe $0 Checkouts

Some Stripe configurations don't allow $0 checkouts. Solutions:

1. **Skip Stripe for free codes**:
   ```javascript
   if (finalAmount === 0) {
     // Generate access token directly
     return { accessToken: generateToken() };
   }
   ```

2. **Use Stripe with $0.01 minimum**:
   ```javascript
   const stripeAmount = Math.max(1, finalAmount * 100);
   ```

### Case Sensitivity

Always normalize codes to uppercase:
```javascript
const code = userInput.toUpperCase().trim();
```

### Race Conditions (Database)

When tracking usage, use atomic updates:
```sql
UPDATE promo_codes 
SET current_uses = current_uses + 1
WHERE id = $1 AND current_uses < max_uses;
```

### Frontend UI

If discount UI doesn't exist, add:
```html
<button id="discountToggle">Have a discount code?</button>
<div id="discountSection" style="display:none">
  <input id="discountCode" placeholder="Enter code">
  <button id="applyDiscount">Apply</button>
</div>
```

## Security Best Practices

1. **Rate Limiting**: Limit validation attempts to prevent brute force
2. **Code Format**: Use hard-to-guess codes (e.g., `PROMO-2024-XJ9K`)
3. **Server-Side Validation**: Never trust client-side validation
4. **Usage Tracking**: Monitor for abuse patterns
5. **Expiration**: Set reasonable expiration dates

## Analytics Queries

### Most Used Codes
```sql
SELECT code, current_uses 
FROM promo_codes 
ORDER BY current_uses DESC 
LIMIT 10;
```

### Recent Usage
```sql
SELECT pc.code, pcu.user_email, pcu.used_at
FROM promo_code_usage pcu
JOIN promo_codes pc ON pcu.promo_code_id = pc.id
ORDER BY pcu.used_at DESC
LIMIT 50;
```

### Revenue Impact
```sql
SELECT 
  pc.code,
  COUNT(*) as uses,
  SUM(CASE WHEN pc.discount_type = 'amount' 
      THEN pc.discount_value ELSE 0 END) as total_discount
FROM promo_code_usage pcu
JOIN promo_codes pc ON pcu.promo_code_id = pc.id
GROUP BY pc.code;
```

## Deployment Checklist

- [ ] Code changes committed
- [ ] Environment variables set (if needed)
- [ ] Database migrations run (if database-driven)
- [ ] API endpoints tested
- [ ] Frontend UI tested
- [ ] Stripe integration tested
- [ ] Reference documentation created
- [ ] User notified of new codes
