---
name: "email-system-builder"
description: "Specialized skill for email system builder workflows and automation."
---

# Email System Builder Skill

Set up complete email systems with beautiful templates, tracking, and deliverability best practices.

## Purpose

Send transactional emails (welcome, password reset, receipts) and marketing emails (newsletters, campaigns) with professional templates.

## When to Use

- Adding email to a new application
- Sending welcome/onboarding emails
- Password reset functionality
- Order confirmations and receipts
- Marketing campaigns and newsletters

## Quick Start

```bash
python3 /home/ubuntu/skills/email-system-builder/scripts/setup_email.py \
  /path/to/project \
  resend
```

## Usage Example

```typescript
import { Resend } from 'resend'
import WelcomeEmail from '@/emails/welcome'

const resend = new Resend(process.env.RESEND_API_KEY)

await resend.emails.send({
  from: 'hello@example.com',
  to: user.email,
  subject: 'Welcome!',
  react: WelcomeEmail({ name: user.name })
})
```

## Providers

- **Resend** - Modern, React Email (Recommended)
- **SendGrid** - Reliable, high volume
- **Mailgun** - Transactional focused
- **AWS SES** - Cost-effective at scale

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

## Best Practices

1. Use proper from address (not noreply@)
2. Include unsubscribe link (required by law)
3. Mobile-responsive design
4. Track opens and clicks
5. Handle bounces properly
6. Test deliverability

## Time Savings

**Manual**: 2-3 hours  
**With Skill**: 15-20 minutes  
**Saved**: ~2 hours per project

## Files

- `scripts/setup_email.py` - Automated setup
- `templates/welcome-email.tsx` - React Email template
- `references/email_patterns.md` - Best practices

## Related Skills

- `user-authentication-system` - Send password reset emails
- `analytics-dashboard` - Track email engagement
- `database-schema-generator` - Create email tracking tables

*Professional emails in minutes, not hours.*
