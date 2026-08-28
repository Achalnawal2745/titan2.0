# Feature Flags Patterns

## When to Use Feature Flags

- **Gradual Rollouts**: Release to 10%, then 50%, then 100%
- **A/B Testing**: Test two versions simultaneously
- **Kill Switches**: Disable features instantly
- **Beta Features**: Give early access to select users
- **Environment-Specific**: Different behavior per environment

## Implementation Patterns

### Simple Boolean Flag
```typescript
if (flags.newFeature) {
  return <NewFeature />
}
return <OldFeature />
```

### Percentage Rollout
```typescript
const rollout = flags.newFeature // 0-100
const userHash = hashUserId(user.id) % 100
if (userHash < rollout) {
  return <NewFeature />
}
```

### User-Based Flags
```typescript
const hasAccess = flags.betaUsers.includes(user.id)
if (hasAccess) {
  return <BetaFeature />
}
```

## Best Practices

1. **Clean up old flags** - Remove after full rollout
2. **Document flags** - What they control and why
3. **Monitor performance** - Track flag impact
4. **Test both paths** - Ensure on/off both work
5. **Use consistent naming** - feature_name_enabled

## Database Schema

```sql
CREATE TABLE feature_flags (
  id UUID PRIMARY KEY,
  key TEXT UNIQUE NOT NULL,
  enabled BOOLEAN DEFAULT false,
  rollout_percentage INTEGER DEFAULT 0,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Providers

- **Vercel Flags** - Built-in, free
- **LaunchDarkly** - Enterprise, $$$
- **PostHog** - Open source, free tier
- **Split.io** - A/B testing focused

## Testing

```typescript
test('shows new feature when flag enabled', () => {
  mockFlags({ newFeature: true })
  render(<App />)
  expect(screen.getByText('New Feature')).toBeInTheDocument()
})
```
