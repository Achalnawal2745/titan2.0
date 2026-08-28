---
name: "feature-flag-system"
description: "Specialized skill for feature flag system workflows and automation."
---

# Feature Flag System Skill

Implement feature flags to toggle features, run A/B tests, and control rollouts without redeployment.

## Purpose

Enable gradual feature rollouts, A/B testing, kill switches, and environment-specific behavior.

## When to Use

- Gradual feature rollouts (10% → 50% → 100%)
- A/B testing different versions
- Beta features for select users
- Kill switches for problematic features
- Environment-specific features

## Quick Start

```bash
python3 /home/ubuntu/skills/feature-flag-system/scripts/setup_flags.py /path/to/project
```

## Usage Example

```typescript
import { useFeatureFlag } from '@/lib/flags'

export function Dashboard() {
  const { enabled } = useFeatureFlag('new_dashboard')
  
  if (enabled) return <NewDashboard />
  return <OldDashboard />
}
```

## Common Patterns

### Percentage Rollout
```typescript
// Roll out to 25% of users
const rollout = 25
const userHash = hashUserId(user.id) % 100
if (userHash < rollout) {
  // Show new feature
}
```

### User-Based Access
```typescript
const betaUsers = ['user1', 'user2']
if (betaUsers.includes(user.id)) {
  // Show beta feature
}
```

## Providers

- **Vercel Flags** - Built-in, free
- **PostHog** - Open source, analytics included
- **LaunchDarkly** - Enterprise-grade
- **Split.io** - A/B testing focused

## Time Savings

**Manual**: 1-2 hours  
**With Skill**: 10-15 minutes  
**Saved**: ~1.5 hours per project

## Files

- `scripts/setup_flags.py` - Automated setup
- `templates/feature-flag.tsx` - React hook
- `references/flags_patterns.md` - Best practices

## Related Skills

- `analytics-dashboard` - Track flag usage
- `deployment-automation` - Deploy with flags
- `testing-framework` - Test flag variations

*Ship features safely with instant rollback capability.*
