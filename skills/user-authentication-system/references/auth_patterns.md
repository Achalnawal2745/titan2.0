# Authentication Patterns Reference

## Provider Comparison

### Clerk (Recommended for Speed)
- **Best for**: Rapid development, startups
- **Pros**: Drop-in components, beautiful UI, easy setup
- **Cons**: Vendor lock-in, pricing scales with users
- **Setup time**: 10 minutes

### Supabase Auth
- **Best for**: Open source, full control
- **Pros**: Free tier, PostgreSQL integration, RLS
- **Cons**: More setup required
- **Setup time**: 20 minutes

### Auth0
- **Best for**: Enterprise, compliance
- **Pros**: Robust, many integrations, SSO
- **Cons**: Complex, expensive
- **Setup time**: 30 minutes

### NextAuth
- **Best for**: Full control, customization
- **Pros**: Free, flexible, many providers
- **Cons**: More code to write
- **Setup time**: 45 minutes

## Common Patterns

### Protected Routes (Next.js)
```typescript
import { auth } from '@clerk/nextjs'
import { redirect } from 'next/navigation'

export default async function ProtectedPage() {
  const { userId } = auth()
  if (!userId) redirect('/sign-in')
  
  return <div>Protected content</div>
}
```

### Session Management
```typescript
import { useUser } from '@clerk/nextjs'

export default function Profile() {
  const { user, isLoaded } = useUser()
  
  if (!isLoaded) return <div>Loading...</div>
  if (!user) return <div>Not signed in</div>
  
  return <div>Hello {user.firstName}</div>
}
```

### Role-Based Access
```typescript
export function requireRole(role: string) {
  const { user } = useUser()
  const hasRole = user?.publicMetadata?.role === role
  
  if (!hasRole) redirect('/unauthorized')
}
```

## Security Best Practices

1. **Always use HTTPS in production**
2. **Store secrets in environment variables**
3. **Implement CSRF protection**
4. **Use secure session cookies**
5. **Enable MFA for sensitive operations**
6. **Implement rate limiting on auth endpoints**
7. **Log authentication events**
8. **Regularly rotate secrets**

## OAuth Providers

### Google
```typescript
providers: [
  GoogleProvider({
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET
  })
]
```

### GitHub
```typescript
providers: [
  GitHubProvider({
    clientId: process.env.GITHUB_ID,
    clientSecret: process.env.GITHUB_SECRET
  })
]
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

### Sessions Table
```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  token TEXT UNIQUE NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
```

## Testing

### Test Sign-in Flow
```typescript
import { test, expect } from '@playwright/test'

test('user can sign in', async ({ page }) => {
  await page.goto('/sign-in')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  
  await expect(page).toHaveURL('/dashboard')
})
```

### Test Protected Route
```typescript
test('redirects to sign-in when not authenticated', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page).toHaveURL('/sign-in')
})
```

## Migration from Other Auth

### From Firebase Auth
1. Export users from Firebase
2. Import to new provider
3. Update client code
4. Test thoroughly
5. Deploy with feature flag

### From Custom Auth
1. Audit current implementation
2. Map to new provider's model
3. Create migration script
4. Run in parallel for testing
5. Gradual rollout

## Performance Optimization

1. **Cache user sessions**
2. **Use JWT for stateless auth**
3. **Implement token refresh**
4. **Lazy load auth components**
5. **Optimize database queries**

## Monitoring

### Key Metrics
- Sign-up conversion rate
- Sign-in success rate
- Session duration
- Failed login attempts
- OAuth provider success rates

### Alerts
- Unusual login patterns
- High failure rates
- Slow auth responses
- Token expiration issues
