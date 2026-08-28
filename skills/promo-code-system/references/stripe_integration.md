# Stripe Integration for Promo Codes

This guide covers Stripe-specific integration patterns for promo codes.

## Applying Discounts to Checkout Sessions

### Method 1: Adjust Line Item Price (Recommended)

Calculate the final price and create checkout with adjusted amount:

```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

app.post('/api/create-checkout', async (req, res) => {
  const { amount = 27, discountCode } = req.body;
  
  let finalAmount = amount;
  
  // Apply discount
  if (discountCode) {
    const result = calculateDiscountedPrice(amount, discountCode);
    if (result.success) {
      finalAmount = result.finalPrice;
    }
  }
  
  // Handle free checkout
  if (finalAmount === 0) {
    const accessToken = generateAccessToken();
    return res.json({ 
      success: true, 
      accessToken,
      amount: 0 
    });
  }
  
  // Create Stripe checkout
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [{
      price_data: {
        currency: 'usd',
        product_data: {
          name: 'Your Product',
          description: 'Product description'
        },
        unit_amount: Math.round(finalAmount * 100) // Convert to cents
      },
      quantity: 1
    }],
    mode: 'payment',
    success_url: `${YOUR_DOMAIN}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${YOUR_DOMAIN}/cancel`,
    metadata: {
      discount_code: discountCode || '',
      original_amount: amount,
      final_amount: finalAmount
    }
  });
  
  res.json({ 
    success: true, 
    url: session.url,
    sessionId: session.id
  });
});
```

### Method 2: Use Stripe Coupons (Alternative)

Create coupons in Stripe and apply them:

```javascript
// Create coupon (do this once, not per checkout)
const coupon = await stripe.coupons.create({
  percent_off: 50,
  duration: 'once',
  id: 'SAVE50'
});

// Apply coupon to checkout
const session = await stripe.checkout.sessions.create({
  // ... other params
  discounts: [{
    coupon: 'SAVE50'
  }]
});
```

**Note**: This method requires managing coupons in Stripe dashboard or via API.

## Handling $0 Checkouts

Stripe doesn't allow $0 checkout sessions. Handle free codes separately:

```javascript
app.post('/api/create-checkout', async (req, res) => {
  const { amount, discountCode } = req.body;
  
  let finalAmount = amount;
  
  if (discountCode) {
    const result = calculateDiscountedPrice(amount, discountCode);
    if (result.success) {
      finalAmount = result.finalPrice;
    }
  }
  
  // FREE CHECKOUT PATH
  if (finalAmount === 0) {
    // Generate access token
    const accessToken = crypto.randomBytes(32).toString('hex');
    
    // Record in database (if using database-driven system)
    if (discountCode) {
      await recordPromoCodeUsage(discountCode, userEmail, userPhone);
    }
    
    // Return access token directly (no Stripe)
    return res.json({ 
      success: true, 
      accessToken,
      amount: 0,
      message: 'Free access granted'
    });
  }
  
  // PAID CHECKOUT PATH
  // Create Stripe checkout session...
});
```

## Verifying Payment with Metadata

Store promo code info in Stripe metadata for verification:

```javascript
// When creating checkout
metadata: {
  promo_code: discountCode,
  promo_code_id: promoCodeId, // If using database
  original_amount: originalAmount,
  final_amount: finalAmount
}

// When verifying payment
app.post('/api/verify-payment', async (req, res) => {
  const { sessionId } = req.body;
  
  const session = await stripe.checkout.sessions.retrieve(sessionId);
  
  if (session.payment_status !== 'paid') {
    return res.status(400).json({ error: 'Payment not completed' });
  }
  
  // Record promo code usage from metadata
  if (session.metadata.promo_code_id) {
    await recordPromoCodeUsage(
      session.metadata.promo_code_id,
      session.customer_details?.email,
      session.customer_details?.phone,
      sessionId
    );
  }
  
  // Generate access token
  const accessToken = generateAccessToken();
  
  res.json({ 
    success: true, 
    accessToken,
    amount: session.amount_total / 100
  });
});
```

## Webhook Handling

If using webhooks, handle promo code tracking:

```javascript
app.post('/webhook', express.raw({type: 'application/json'}), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  
  let event;
  try {
    event = stripe.webhooks.constructEvent(
      req.body, 
      sig, 
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    
    // Record promo code usage
    if (session.metadata.promo_code_id) {
      await recordPromoCodeUsage(
        session.metadata.promo_code_id,
        session.customer_details?.email,
        session.customer_details?.phone,
        session.id
      );
    }
    
    // ... other fulfillment logic
  }
  
  res.json({received: true});
});
```

## Test Card Numbers

Use these test cards in Stripe test mode:

| Card Number | Description |
|-------------|-------------|
| 4242 4242 4242 4242 | Successful payment |
| 4000 0000 0000 9995 | Declined payment |
| 4000 0025 0000 3155 | Requires authentication (3D Secure) |

**Test Details**:
- Expiry: Any future date (e.g., 12/34)
- CVC: Any 3 digits (e.g., 123)
- ZIP: Any 5 digits (e.g., 12345)

## Common Issues

### Issue: Stripe rejects $0 amount

**Solution**: Skip Stripe for free codes (see "Handling $0 Checkouts")

### Issue: Discount not applied in Stripe dashboard

**Solution**: Stripe only shows the final amount. Store original amount in metadata for tracking.

### Issue: Coupon code not found in Stripe

**Solution**: Either create coupons in Stripe dashboard first, or use Method 1 (adjust line item price) instead.

### Issue: Webhook not receiving promo code data

**Solution**: Ensure metadata is set when creating checkout session. Metadata persists through webhooks.

## Best Practices

1. **Always validate server-side**: Never trust client-provided discount amounts
2. **Store metadata**: Use Stripe metadata to track promo codes
3. **Handle $0 separately**: Don't send $0 amounts to Stripe
4. **Test in test mode**: Use Stripe test keys before going live
5. **Monitor webhooks**: Set up webhook monitoring for failed events

## Switching to Live Mode

When ready for production:

1. Get live keys from Stripe dashboard
2. Update environment variables:
   ```
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   ```
3. Test with real card (small amount)
4. Set up live webhook endpoint
5. Update webhook secret:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

## Revenue Tracking

Calculate revenue impact of promo codes:

```javascript
// Query Stripe for sessions with promo codes
const sessions = await stripe.checkout.sessions.list({
  limit: 100
});

let totalRevenue = 0;
let totalDiscount = 0;

sessions.data.forEach(session => {
  if (session.metadata.original_amount) {
    const original = parseFloat(session.metadata.original_amount);
    const final = session.amount_total / 100;
    totalRevenue += final;
    totalDiscount += (original - final);
  }
});

console.log(`Total Revenue: $${totalRevenue}`);
console.log(`Total Discounts: $${totalDiscount}`);
```
