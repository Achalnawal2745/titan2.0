# Stripe Payment Integration Patterns

## One-Time Payments

**Use Case**: Single product purchase, course enrollment, quiz access

**Implementation**:
- Create Checkout Session
- Redirect to Stripe-hosted page
- Handle webhook for fulfillment

**Time to implement**: 30 minutes

## Subscriptions

**Use Case**: SaaS, memberships, recurring services

**Implementation**:
- Create subscription with price ID
- Handle trial periods
- Manage upgrades/downgrades
- Cancel/pause subscriptions

**Time to implement**: 1 hour

## Webhooks

**Critical Events**:
- `checkout.session.completed` - Payment successful
- `customer.subscription.updated` - Subscription changed
- `customer.subscription.deleted` - Subscription cancelled
- `invoice.payment_failed` - Payment failed

**Security**: Always verify webhook signatures

## Testing

**Test Cards**:
- Success: 4242 4242 4242 4242
- Decline: 4000 0000 0000 0002
- 3D Secure: 4000 0027 6000 3184

## Best Practices

1. **Never store card details** - Use Stripe tokens
2. **Handle errors gracefully** - Network issues, declined cards
3. **Verify webhooks** - Prevent replay attacks
4. **Test thoroughly** - Use test mode extensively
5. **Monitor failed payments** - Set up alerts
