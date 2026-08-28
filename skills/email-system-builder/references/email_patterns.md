# Email System Patterns

## Provider Comparison

### Resend (Recommended)
- **Best for**: Modern apps, React Email
- **Pros**: Developer-friendly, great DX
- **Pricing**: $20/mo for 50k emails
- **Setup**: 5 minutes

### SendGrid
- **Best for**: High volume, templates
- **Pros**: Reliable, feature-rich
- **Pricing**: Free up to 100 emails/day
- **Setup**: 15 minutes

### Mailgun
- **Best for**: Transactional emails
- **Pros**: Good deliverability
- **Pricing**: Pay as you go
- **Setup**: 10 minutes

## Email Types

### Transactional
- Welcome emails
- Password resets
- Order confirmations
- Receipts

### Marketing
- Newsletters
- Product updates
- Drip campaigns
- Announcements

## Best Practices

1. **Use proper from address** - noreply@ is bad
2. **Include unsubscribe link** - Required by law
3. **Test deliverability** - Check spam scores
4. **Track opens/clicks** - Monitor engagement
5. **Handle bounces** - Remove invalid emails
6. **Personalize content** - Use user data
7. **Mobile-responsive** - 50%+ open on mobile
8. **Plain text fallback** - For accessibility

## Database Schema

```sql
CREATE TABLE email_sends (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  email_type TEXT NOT NULL,
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  opened_at TIMESTAMPTZ,
  clicked_at TIMESTAMPTZ,
  bounced BOOLEAN DEFAULT false
);
```

## Testing

```typescript
test('sends welcome email', async () => {
  const user = { email: 'test@example.com', name: 'Test' }
  await sendWelcomeEmail(user)
  
  expect(mockResend.emails.send).toHaveBeenCalledWith({
    to: user.email,
    subject: 'Welcome!'
  })
})
```

## Deliverability Tips

- Warm up new domains gradually
- Maintain good sender reputation
- Use SPF, DKIM, DMARC records
- Monitor bounce rates
- Clean email lists regularly
