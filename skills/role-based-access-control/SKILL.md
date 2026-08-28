---
name: "role-based-access-control"
description: "Specialized skill for role based access control workflows and automation."
---

# Role-Based Access Control (RBAC) for tRPC + React Apps

Implement secure role-based access control in full-stack TypeScript applications using tRPC procedures and React components.

## When to Use This Skill

- Adding admin-only or manager-only features to existing applications
- Restricting specific tRPC endpoints to authorized users
- Implementing multi-tier permission systems (admin, manager, user)
- Hiding UI elements based on user roles
- Building dashboards or tools that require different access levels

## Prerequisites

- tRPC backend with `protectedProcedure` already implemented
- User authentication system in place (OAuth, JWT, or similar)
- User table with `role` field in database schema
- React frontend with auth context or hook (e.g., `useAuth()`)

## Implementation Steps

### Step 1: Ensure Database Schema Has Role Field

Verify the `user` table includes a `role` field:

```typescript
// drizzle/schema.ts or similar
export const user = sqliteTable('user', {
  id: integer('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  role: text('role', { enum: ['admin', 'user'] }).notNull().default('user'),
  // ... other fields
});
```

If the role field doesn't exist, add it and run migrations.

### Step 2: Create Role-Specific Procedures

Add custom procedures for each role level in your tRPC router file:

```typescript
// server/routers.ts or similar
import { protectedProcedure, router } from "./_core/trpc";
import { TRPCError } from "@trpc/server";

// Admin-only procedure
const adminProcedure = protectedProcedure.use(({ ctx, next }) => {
  if (ctx.user.role !== 'admin') {
    throw new TRPCError({ 
      code: 'FORBIDDEN',
      message: 'Only administrators can access this resource'
    });
  }
  return next({ ctx });
});

// Manager or admin procedure (if you have multiple admin-like roles)
const managerProcedure = protectedProcedure.use(({ ctx, next }) => {
  if (ctx.user.role !== 'admin' && ctx.user.role !== 'manager') {
    throw new TRPCError({ 
      code: 'FORBIDDEN',
      message: 'Only managers and administrators can access this resource'
    });
  }
  return next({ ctx });
});
```

**Key points:**
- Build on top of `protectedProcedure` (assumes user is already authenticated)
- Use `FORBIDDEN` error code (403) for permission denials
- Provide clear error messages for debugging

### Step 3: Apply Role Procedures to Endpoints

Replace `protectedProcedure` with role-specific procedures for restricted endpoints:

```typescript
export const myRouter = router({
  // Public endpoint - anyone can access
  getPublicData: publicProcedure.query(async () => {
    return await getPublicData();
  }),

  // Protected endpoint - any authenticated user
  getUserData: protectedProcedure.query(async ({ ctx }) => {
    return await getUserData(ctx.user.id);
  }),

  // Admin-only endpoint
  getAllUsers: adminProcedure.query(async () => {
    return await getAllUsers();
  }),

  // Manager or admin endpoint
  getTeamStats: managerProcedure.query(async () => {
    return await getTeamStats();
  }),
});
```

### Step 4: Add Frontend Role Checks

Protect React components and UI elements based on user role:

```typescript
// pages/AdminDashboard.tsx
import { useAuth } from "@/_core/hooks/useAuth";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function AdminDashboard() {
  const { user } = useAuth();

  // Check authentication
  if (!user) {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Authentication Required</AlertTitle>
          <AlertDescription>
            Please log in to access this page.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Check authorization
  if (user.role !== 'admin') {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Access Denied</AlertTitle>
          <AlertDescription>
            You do not have permission to access this page. This area is restricted to administrators only.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Render admin content
  return (
    <div className="container mx-auto py-8">
      <h1>Admin Dashboard</h1>
      {/* Admin-only content */}
    </div>
  );
}
```

### Step 5: Hide Navigation Links for Unauthorized Users

Conditionally render navigation links based on user role:

```typescript
// pages/Home.tsx or Layout.tsx
import { trpc } from "@/lib/trpc";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";

export function Navigation() {
  const { data: user } = trpc.auth.me.useQuery();

  return (
    <nav className="flex items-center gap-4">
      <Link href="/dashboard">
        <Button variant="ghost">Dashboard</Button>
      </Link>
      <Link href="/profile">
        <Button variant="ghost">Profile</Button>
      </Link>
      {user?.role === 'admin' && (
        <Link href="/admin">
          <Button variant="ghost">Admin</Button>
        </Link>
      )}
      {(user?.role === 'admin' || user?.role === 'manager') && (
        <Link href="/manager">
          <Button variant="ghost">Manager</Button>
        </Link>
      )}
    </nav>
  );
}
```

**Key points:**
- Use optional chaining (`user?.role`) to handle loading states
- Hide links entirely rather than showing disabled buttons
- Keep role checks consistent between frontend and backend

## Testing Checklist

- [ ] Verify admin users can access admin-only endpoints
- [ ] Verify regular users receive 403 FORBIDDEN errors when accessing admin endpoints
- [ ] Verify navigation links are hidden for unauthorized users
- [ ] Verify protected pages show access denied messages for non-admin users
- [ ] Test with unauthenticated users (should see login prompts)
- [ ] Test role promotion (change user role in database, verify new permissions)

## Common Patterns

### Multiple Role Levels

For applications with more than two roles (e.g., admin, manager, moderator, user):

```typescript
const roleHierarchy = {
  admin: 4,
  manager: 3,
  moderator: 2,
  user: 1,
};

const requireRole = (minRole: keyof typeof roleHierarchy) => {
  return protectedProcedure.use(({ ctx, next }) => {
    const userRoleLevel = roleHierarchy[ctx.user.role];
    const requiredLevel = roleHierarchy[minRole];
    
    if (userRoleLevel < requiredLevel) {
      throw new TRPCError({ 
        code: 'FORBIDDEN',
        message: `This resource requires ${minRole} role or higher`
      });
    }
    return next({ ctx });
  });
};

// Usage
const managerProcedure = requireRole('manager'); // allows manager, admin
const moderatorProcedure = requireRole('moderator'); // allows moderator, manager, admin
```

### Resource-Level Permissions

For fine-grained permissions (e.g., "user can only edit their own posts"):

```typescript
const canEditPost = protectedProcedure.use(async ({ ctx, next, input }) => {
  const post = await getPostById(input.postId);
  
  if (post.authorId !== ctx.user.id && ctx.user.role !== 'admin') {
    throw new TRPCError({ 
      code: 'FORBIDDEN',
      message: 'You can only edit your own posts'
    });
  }
  
  return next({ ctx: { ...ctx, post } });
});
```

### Reusable Role Check Hook

Create a custom hook for consistent role checks across components:

```typescript
// hooks/useRequireRole.ts
import { useAuth } from "@/_core/hooks/useAuth";
import { useEffect } from "react";
import { useLocation } from "wouter";

export function useRequireRole(requiredRole: 'admin' | 'manager') {
  const { user } = useAuth();
  const [, setLocation] = useLocation();

  useEffect(() => {
    if (!user) {
      setLocation('/login');
    } else if (user.role !== requiredRole && user.role !== 'admin') {
      setLocation('/access-denied');
    }
  }, [user, requiredRole, setLocation]);

  return { user, isAuthorized: user?.role === requiredRole || user?.role === 'admin' };
}

// Usage in component
export function AdminDashboard() {
  const { user, isAuthorized } = useRequireRole('admin');
  
  if (!isAuthorized) return null; // Will redirect
  
  return <div>Admin content</div>;
}
```

## Security Best Practices

1. **Always validate on the backend** - Frontend checks are for UX only; backend procedures enforce security
2. **Use specific error codes** - `FORBIDDEN` (403) for permission issues, `UNAUTHORIZED` (401) for authentication issues
3. **Fail closed** - Default to denying access unless explicitly granted
4. **Log permission denials** - Track unauthorized access attempts for security monitoring
5. **Avoid role checks in database queries** - Use procedures to centralize authorization logic
6. **Test with different roles** - Verify each role level has correct access

## Troubleshooting

**Error: "Cannot read property 'role' of undefined"**
- User object is not available in context
- Check that `protectedProcedure` is properly configured
- Verify authentication middleware is running before role checks

**Frontend shows admin links but backend denies access**
- Role check logic differs between frontend and backend
- Ensure consistent role field names and values
- Check for typos in role strings ('admin' vs 'Admin')

**User role not updating after database change**
- Session/JWT token still contains old role
- Implement token refresh or require re-login after role changes
- Consider adding role version field to detect stale tokens
