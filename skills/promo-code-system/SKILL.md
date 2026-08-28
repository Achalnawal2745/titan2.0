---
name: "promo-code-system"
description: "Specialized skill for promo code system workflows and automation."
---

# Promo Code System

Add promotional and discount code functionality to web applications with tracking, analytics, and flexible discount types.

## Overview

This skill helps implement promo code systems in web apps. Supports:

- **Quick implementation** (hardcoded codes, 5 minutes)
- **Proper implementation** (database-driven, 45 minutes)
- **Multiple discount types** (free access, percentage off, fixed amount)
- **Usage tracking and analytics**
- **Expiration dates and limits**
- **Stripe integration**

## When to Use This Skill

- User wants to add promo codes to their app
- User asks "how do I remember my codes?"
- User needs to track which codes are being used
- User wants to offer free access via codes
- User has existing discount system that needs extension

## Quick Start Workflow

Follow these steps in order:

### Step 1: Discover Existing System

Run the discovery script to find existing promo code implementation:

```bash
python3 scripts/discover_promo_system.py /path/to/project
```

If you don't have the project path, locate it by:
1. Checking Supabase projects (MCP)
2. Checking Vercel deployments (MCP)
3. Checking GitHub repositories (`gh repo list`)
4. Asking user for local path

The script identifies:
- Hardcoded discount codes
- Database tables
- API endpoints
- Payment processor integration

### Step 2: Analyze Current State

Based on discovery results, determine implementation type:

**No System Found**
- No promo code patterns detected
- → Recommend Path A (Quick Start)

**Hardcoded System Found**
- Found `DISCOUNT_CODES` object or similar
- Codes defined in source code
- → Extend existing system or upgrade to database

**Database System Found**
- Found `promo_codes` table
- Has API endpoints
- → Enhance existing system

### Step 3: Choose Implementation Path

**Path A: Quick (Hardcoded) - 5 minutes**
- Best for: MVPs, <20 codes, simple needs
- Use: `templates/hardcoded_codes_template.js`
- Pros: Fast, simple, no database changes
- Cons: No tracking, must redeploy to add codes

**Path B: Proper (Database) - 45 minutes**
- Best for: Production, >20 codes, need tracking
- Use: `templates/promo_schema.sql` + API templates
- Pros: Full tracking, expiration, limits, analytics
- Cons: More complex, requires database

### Step 4: Implement Solution

#### For Path A (Quick/Hardcoded):

1. Copy `templates/hardcoded_codes_template.js` content
2. Add to user's server file (e.g., `server.js`, `index.js`)
3. Customize `DISCOUNT_CODES` object with their codes
4. Update checkout endpoint to use `calculateDiscountedPrice()`
5. Deploy

Example codes to add:
```javascript
const DISCOUNT_CODES = {
  'FREE': { type: 'free', value: 0 },
  'FRIEND': { type: 'free', value: 0 },
  'SAVE10': { type: 'amount', value: 10 },
  'HALF': { type: 'percentage', value: 50 },
};
```

#### For Path B (Database-Driven):

1. Create database tables:
   - Run `templates/promo_schema.sql` in Supabase SQL Editor
   
2. Implement validation functions:
   - Add server-side validation (see `references/implementation_guide.md`)
   
3. Update API endpoints:
   - POST `/api/validate-promo-code` - Validate code
   - POST `/api/create-checkout` - Apply discount
   - POST `/api/verify-payment` - Track usage
   
4. (Optional) Deploy admin panel:
   - Use `templates/admin_panel.html` for visual management
   
5. Test end-to-end

### Step 5: Create Reference Documentation

Always create a quick reference guide for the user:

1. Copy `templates/quick_reference_template.md`
2. Fill in placeholders:
   - Project name
   - File path where codes are stored
   - List of active codes
   - Instructions for adding more codes
   - Instructions for remembering codes
3. Save as `MY_PROMO_CODES.md` in their project

This answers the common question: "How do I remember my codes?"

### Step 6: Test Implementation

Run through testing checklist:

**Basic Tests**:
- Valid code applies discount correctly
- Invalid code returns error
- Free code sets price to $0
- Case insensitivity works (FRIEND = friend)

**Integration Tests** (if using Stripe):
- Checkout with discount code
- Free checkout (skip Stripe for $0)
- Payment verification
- Usage tracking (if database-driven)

Test cards for Stripe:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 9995`

## Tech Stack Specific Instructions

### Node.js + Express

Use `templates/hardcoded_codes_template.js` directly:

```javascript
// Add to server.js
const { validateDiscountCode, calculateDiscountedPrice } = require('./promo-codes');

app.post('/api/validate-promo-code', (req, res) => {
  const { code } = req.body;
  const result = validateDiscountCode(code);
  res.json(result);
});
```

### Next.js (App Router)

Create API routes in `app/api/`:

```typescript
// app/api/validate-promo/route.ts
export async function POST(request: Request) {
  const { code } = await request.json();
  const result = validateDiscountCode(code);
  return Response.json(result);
}
```

### Next.js (Pages Router)

Create API routes in `pages/api/`:

```typescript
// pages/api/validate-promo.ts
export default function handler(req, res) {
  const { code } = req.body;
  const result = validateDiscountCode(code);
  res.json(result);
}
```

### Python + Flask/FastAPI

For Python implementations, adapt the JavaScript logic to Python:

```python
DISCOUNT_CODES = {
    'FREE': {'type': 'free', 'value': 0},
    'SAVE10': {'type': 'amount', 'value': 10},
}

def validate_discount_code(code):
    code = code.upper().strip()
    if code not in DISCOUNT_CODES:
        return {'valid': False, 'error': 'Invalid code'}
    return {'valid': True, **DISCOUNT_CODES[code]}
```

## Stripe Integration

Read `references/stripe_integration.md` for detailed Stripe patterns.

### Key Points:

1. **Apply discount by adjusting line item price** (recommended):
   ```javascript
   unit_amount: Math.round(finalAmount * 100)
   ```

2. **Handle $0 checkouts separately** (Stripe doesn't allow $0):
   ```javascript
   if (finalAmount === 0) {
     return { accessToken: generateToken() };
   }
   ```

3. **Store promo code in metadata**:
   ```javascript
   metadata: {
     promo_code: discountCode,
     original_amount: originalAmount,
     final_amount: finalAmount
   }
   ```

## Generating Promo Codes

Use the code generator script to create secure codes:

```bash
python3 scripts/generate_codes.py --count 10 --prefix FRIEND
```

Options:
- `--count N` - Number of codes to generate
- `--prefix PREFIX` - Code prefix (e.g., SAVE, FRIEND)
- `--length N` - Random part length (default: 8)
- `--format` - alphanumeric, alpha, or numeric
- `--separator` - Separator character (default: -)

Output includes ready-to-paste formats:
- JavaScript object
- SQL INSERT statements
- Markdown list
- Plain text

## Common Patterns

### Free Access Codes
```javascript
'FREE': { type: 'free', value: 0 }
'FRIEND': { type: 'free', value: 0 }
'BETA': { type: 'free', value: 0 }
```

### Fixed Amount Discounts
```javascript
'SAVE10': { type: 'amount', value: 10 }  // $10 off
'SAVE20': { type: 'amount', value: 20 }  // $20 off
```

### Percentage Discounts
```javascript
'HALF': { type: 'percentage', value: 50 }     // 50% off
'QUARTER': { type: 'percentage', value: 25 }  // 25% off
```

## Database Schema (Path B)

For database-driven systems, use `templates/promo_schema.sql`:

**Main table**: `promo_codes`
- `code` - The promo code (unique)
- `discount_type` - 'free', 'amount', or 'percentage'
- `discount_value` - Discount amount
- `is_active` - Enable/disable code
- `max_uses` - Usage limit (NULL = unlimited)
- `current_uses` - Usage counter
- `expires_at` - Expiration date (NULL = never)

**Tracking table**: `promo_code_usage`
- `promo_code_id` - Link to promo code
- `user_email` - Who used it
- `used_at` - When used
- `stripe_session_id` - Payment session

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

## Security Best Practices

1. **Always validate server-side** - Never trust client input
2. **Rate limit validation** - Prevent brute force guessing
3. **Use secure code format** - Hard-to-guess codes (e.g., `PROMO-2024-XJ9K`)
4. **Normalize codes** - Convert to uppercase, trim whitespace
5. **Track usage patterns** - Monitor for abuse

## Troubleshooting

### Code not working
- Check code is active (`is_active = true`)
- Check not expired (`expires_at > NOW()`)
- Check usage limit not reached (`current_uses < max_uses`)
- Verify case-insensitive comparison

### $0 checkout fails
- Stripe doesn't allow $0 checkouts
- Skip Stripe for free codes
- Generate access token directly

### Usage not tracked
- Verify `recordPromoCodeUsage()` is called after payment
- Check database connection
- Verify promo_code_id is passed correctly

### Discount not applied in Stripe
- Stripe shows final amount only
- Store original amount in metadata for tracking
- Verify calculation logic is correct

## Reference Files

- `references/implementation_guide.md` - Detailed implementation workflows
- `references/stripe_integration.md` - Stripe-specific patterns
- `templates/promo_schema.sql` - Database schema
- `templates/hardcoded_codes_template.js` - Quick implementation template
- `templates/quick_reference_template.md` - User reference doc template

## Deliverables

Always provide user with:

1. **Implementation code** - Ready to paste into their project
2. **Quick reference guide** - `MY_PROMO_CODES.md` with their codes
3. **Testing instructions** - How to verify it works
4. **Deployment steps** - How to deploy changes

## Example Complete Workflow

User says: "I need to add promo codes to my poker quiz app"

1. **Discover**: Run discovery script, find existing hardcoded system
2. **Analyze**: They have `DISCOUNT_CODES` object with 2 codes
3. **Choose**: Recommend extending existing system (Path A)
4. **Implement**: Add 10 new codes to their `DISCOUNT_CODES` object
5. **Document**: Create `MY_PROMO_CODES.md` with all codes
6. **Test**: Verify codes work on live site
7. **Deliver**: Send updated code + reference doc

User asks: "How do I remember my codes?"

Answer: "Your codes are in `MY_PROMO_CODES.md` (attached). They're also in your `server.js` file at line 159."

## Success Criteria

✅ User can add promo codes in < 5 minutes (Path A)  
✅ User has reference doc to remember codes  
✅ Codes work on live site  
✅ User understands how to add more codes  
✅ (Optional) User has path to upgrade to database system
