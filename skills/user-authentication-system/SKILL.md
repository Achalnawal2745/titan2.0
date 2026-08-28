---
name: "user-authentication-system"
description: "Specialized skill for user authentication system workflows and automation."
---

# User Authentication System Skill

Automate setup of complete authentication systems with OAuth, session management, and security best practices.

## Purpose

Quickly add production-ready authentication to web applications with support for multiple providers (Clerk, Supabase, Auth0, NextAuth).

## When to Use

- Adding auth to a new application
- Switching auth providers
- Implementing OAuth (Google, GitHub, etc.)
- Setting up role-based access control
- Migrating from custom auth

## Quick Start

```bash
python3 /home/ubuntu/skills/user-authentication-system/scripts/setup_auth.py \
  /path/to/project \
  clerk \
  pk_test_your_key
```

## Supported Providers

- **Clerk** - Fastest setup (10 min)
- **Supabase** - Open source, free tier
- **Auth0** - Enterprise-grade
- **NextAuth** - Full control, customizable

## What It Does

1. Detects framework (Next.js, React, Express, Flask)
2. Installs auth dependencies
3. Creates configuration files
4. Generates auth provider components
5. Provides sign-in/sign-up templates

## Protected Routes Example

```typescript
import { auth } from '@clerk/nextjs'

export default async function Dashboard() {
  const { userId } = auth()
  if (!userId) redirect('/sign-in')
  return <div>Protected content</div>
}
```

## Time Savings

**Manual**: 2-3 hours  
**With Skill**: 15-20 minutes  
**Saved**: ~2 hours per project

## Files

- `scripts/setup_auth.py` - Automated setup (200 lines)
- `templates/signin.tsx` - Sign-in component
- `references/auth_patterns.md` - Comprehensive guide (200+ lines)

## Related Skills

- `deployment-automation` - Deploy with auth configured
- `database-schema-generator` - Create users/sessions tables
- `analytics-dashboard` - Track auth events

*Production-ready authentication in minutes.*
