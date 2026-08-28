# API Endpoint Patterns

Best practices and common patterns for building REST and tRPC APIs.

## Table of Contents

1. [RESTful Design](#restful-design)
2. [HTTP Methods](#http-methods)
3. [Status Codes](#status-codes)
4. [Input Validation](#input-validation)
5. [Error Handling](#error-handling)
6. [Authentication](#authentication)
7. [Pagination](#pagination)
8. [Filtering & Sorting](#filtering--sorting)
9. [Rate Limiting](#rate-limiting)
10. [tRPC Patterns](#trpc-patterns)

---

## RESTful Design

### Resource Naming

Use **plural nouns** for resources:

```
✅ Good:
/api/users
/api/posts
/api/comments

❌ Bad:
/api/getUsers
/api/user
/api/post-list
```

### Nested Resources

Use nesting for relationships:

```
✅ Good:
/api/posts/123/comments
/api/users/456/posts

⚠️  Avoid deep nesting (max 2 levels):
❌ /api/users/123/posts/456/comments/789/likes
✅ /api/comments/789/likes
```

### URL Structure

```
GET    /api/posts           # List all posts
POST   /api/posts           # Create new post
GET    /api/posts/123       # Get single post
PUT    /api/posts/123       # Update entire post
PATCH  /api/posts/123       # Update partial post
DELETE /api/posts/123       # Delete post
```

---

## HTTP Methods

### GET - Read

**Use for**: Retrieving data  
**Idempotent**: Yes  
**Safe**: Yes (no side effects)

```typescript
GET /api/posts?limit=10&page=1
```

### POST - Create

**Use for**: Creating new resources  
**Idempotent**: No  
**Safe**: No

```typescript
POST /api/posts
Body: { title: "...", content: "..." }
Response: 201 Created
```

### PUT - Replace

**Use for**: Replacing entire resource  
**Idempotent**: Yes  
**Safe**: No

```typescript
PUT /api/posts/123
Body: { title: "...", content: "...", status: "..." }
Response: 200 OK
```

### PATCH - Update

**Use for**: Updating part of resource  
**Idempotent**: Yes  
**Safe**: No

```typescript
PATCH /api/posts/123
Body: { status: "published" }
Response: 200 OK
```

### DELETE - Remove

**Use for**: Deleting resources  
**Idempotent**: Yes  
**Safe**: No

```typescript
DELETE /api/posts/123
Response: 204 No Content
```

---

## Status Codes

### Success (2xx)

- **200 OK** - Successful GET, PUT, PATCH, or DELETE
- **201 Created** - Successful POST with new resource
- **204 No Content** - Successful DELETE with no response body

### Client Errors (4xx)

- **400 Bad Request** - Invalid input/validation error
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Authenticated but not authorized
- **404 Not Found** - Resource doesn't exist
- **409 Conflict** - Duplicate resource or conflict
- **422 Unprocessable Entity** - Validation error (alternative to 400)
- **429 Too Many Requests** - Rate limit exceeded

### Server Errors (5xx)

- **500 Internal Server Error** - Unexpected server error
- **503 Service Unavailable** - Server temporarily down

### Example Usage

```typescript
// Success
return NextResponse.json(data, { status: 200 });

// Created
return NextResponse.json(newItem, { status: 201 });

// Bad request
return NextResponse.json(
  { error: 'Invalid input', details: errors },
  { status: 400 }
);

// Unauthorized
return NextResponse.json(
  { error: 'Unauthorized' },
  { status: 401 }
);

// Not found
return NextResponse.json(
  { error: 'Post not found' },
  { status: 404 }
);
```

---

## Input Validation

### Use Zod for Validation

```typescript
import { z } from 'zod';

const createPostSchema = z.object({
  title: z.string().min(1).max(255),
  content: z.string().min(1),
  status: z.enum(['draft', 'published']).default('draft'),
  tags: z.array(z.string()).optional(),
});

// In endpoint
try {
  const data = createPostSchema.parse(body);
  // Use validated data
} catch (error) {
  if (error instanceof z.ZodError) {
    return NextResponse.json(
      { error: 'Validation failed', details: error.errors },
      { status: 400 }
    );
  }
}
```

### Common Validation Patterns

```typescript
// Email
email: z.string().email()

// URL
url: z.string().url()

// UUID
id: z.string().uuid()

// Enum
status: z.enum(['draft', 'published', 'archived'])

// Number range
age: z.number().min(0).max(120)

// String length
username: z.string().min(3).max(20)

// Optional with default
role: z.string().default('user')

// Array
tags: z.array(z.string()).min(1).max(10)

// Nested object
address: z.object({
  street: z.string(),
  city: z.string(),
  zip: z.string(),
})

// Transform
limit: z.string().transform(Number).pipe(z.number().min(1).max(100))
```

---

## Error Handling

### Consistent Error Format

```typescript
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": { /* Additional context */ }
}
```

### Example Implementation

```typescript
export async function POST(request: NextRequest) {
  try {
    // Your logic here
  } catch (error) {
    // Validation error
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation failed',
          code: 'VALIDATION_ERROR',
          details: error.errors,
        },
        { status: 400 }
      );
    }

    // Database error
    if (error.code === 'P2002') {
      return NextResponse.json(
        {
          error: 'Resource already exists',
          code: 'DUPLICATE_ERROR',
        },
        { status: 409 }
      );
    }

    // Generic error
    console.error('API error:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        code: 'INTERNAL_ERROR',
      },
      { status: 500 }
    );
  }
}
```

---

## Authentication

### Check Authentication

```typescript
import { getServerSession } from 'next-auth';

export async function POST(request: NextRequest) {
  const session = await getServerSession();
  
  if (!session?.user) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }

  // User is authenticated
  const userId = session.user.id;
}
```

### Check Authorization (Ownership)

```typescript
// Check if user owns the resource
const post = await db.post.findUnique({
  where: { id: params.id },
});

if (!post) {
  return NextResponse.json(
    { error: 'Post not found' },
    { status: 404 }
  );
}

if (post.userId !== session.user.id) {
  return NextResponse.json(
    { error: 'Forbidden' },
    { status: 403 }
  );
}
```

### Role-Based Access

```typescript
// Check user role
if (session.user.role !== 'admin') {
  return NextResponse.json(
    { error: 'Admin access required' },
    { status: 403 }
  );
}
```

---

## Pagination

### Offset-Based Pagination

**Simple, but slower for large datasets**

```typescript
const querySchema = z.object({
  limit: z.number().min(1).max(100).default(10),
  page: z.number().min(1).default(1),
});

const { limit, page } = querySchema.parse(query);

const items = await db.item.findMany({
  take: limit,
  skip: (page - 1) * limit,
  orderBy: { createdAt: 'desc' },
});

const total = await db.item.count();

return {
  items,
  pagination: {
    page,
    limit,
    total,
    pages: Math.ceil(total / limit),
  },
};
```

### Cursor-Based Pagination

**Better performance for large datasets**

```typescript
const querySchema = z.object({
  limit: z.number().min(1).max(100).default(10),
  cursor: z.string().optional(),
});

const { limit, cursor } = querySchema.parse(query);

const items = await db.item.findMany({
  take: limit + 1, // Fetch one extra to check if there's more
  cursor: cursor ? { id: cursor } : undefined,
  orderBy: { createdAt: 'desc' },
});

let nextCursor: string | undefined = undefined;
if (items.length > limit) {
  const nextItem = items.pop();
  nextCursor = nextItem!.id;
}

return {
  items,
  nextCursor,
};
```

---

## Filtering & Sorting

### Query Parameters

```
GET /api/posts?status=published&sort=createdAt&order=desc&search=hello
```

### Implementation

```typescript
const querySchema = z.object({
  status: z.enum(['draft', 'published', 'archived']).optional(),
  sort: z.enum(['createdAt', 'updatedAt', 'title']).default('createdAt'),
  order: z.enum(['asc', 'desc']).default('desc'),
  search: z.string().optional(),
});

const query = querySchema.parse(searchParams);

const items = await db.item.findMany({
  where: {
    ...(query.status && { status: query.status }),
    ...(query.search && {
      OR: [
        { title: { contains: query.search, mode: 'insensitive' } },
        { content: { contains: query.search, mode: 'insensitive' } },
      ],
    }),
  },
  orderBy: { [query.sort]: query.order },
});
```

---

## Rate Limiting

### Simple In-Memory Rate Limiter

```typescript
const rateLimitMap = new Map<string, { count: number; resetTime: number }>();

function rateLimit(identifier: string, limit: number, windowMs: number): boolean {
  const now = Date.now();
  const record = rateLimitMap.get(identifier);

  if (!record || now > record.resetTime) {
    rateLimitMap.set(identifier, {
      count: 1,
      resetTime: now + windowMs,
    });
    return true;
  }

  if (record.count >= limit) {
    return false;
  }

  record.count++;
  return true;
}

// In endpoint
const identifier = session?.user?.id || request.ip;
if (!rateLimit(identifier, 10, 60000)) { // 10 requests per minute
  return NextResponse.json(
    { error: 'Too many requests' },
    { status: 429 }
  );
}
```

---

## tRPC Patterns

### Router Structure

```typescript
import { createTRPCRouter, publicProcedure, protectedProcedure } from '~/server/api/trpc';

export const postRouter = createTRPCRouter({
  // Public query
  getAll: publicProcedure
    .input(z.object({ limit: z.number().default(10) }))
    .query(async ({ ctx, input }) => {
      return await ctx.db.post.findMany({
        take: input.limit,
      });
    }),

  // Protected mutation
  create: protectedProcedure
    .input(z.object({ title: z.string(), content: z.string() }))
    .mutation(async ({ ctx, input }) => {
      return await ctx.db.post.create({
        data: {
          ...input,
          userId: ctx.session.user.id,
        },
      });
    }),
});
```

### Error Handling

```typescript
import { TRPCError } from '@trpc/server';

// Throw errors
throw new TRPCError({
  code: 'NOT_FOUND',
  message: 'Post not found',
});

// Error codes:
// - BAD_REQUEST
// - UNAUTHORIZED
// - FORBIDDEN
// - NOT_FOUND
// - INTERNAL_SERVER_ERROR
// - CONFLICT
```

### Middleware

```typescript
const isAuthed = t.middleware(({ ctx, next }) => {
  if (!ctx.session?.user) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }
  return next({
    ctx: {
      session: ctx.session,
    },
  });
});

export const protectedProcedure = t.procedure.use(isAuthed);
```

---

## Best Practices Summary

1. ✅ Use proper HTTP methods and status codes
2. ✅ Validate all inputs with Zod
3. ✅ Handle errors consistently
4. ✅ Check authentication and authorization
5. ✅ Implement pagination for lists
6. ✅ Add rate limiting
7. ✅ Use TypeScript for type safety
8. ✅ Log errors for debugging
9. ✅ Return meaningful error messages
10. ✅ Document your API

---

## Further Reading

- [REST API Design Best Practices](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [tRPC Documentation](https://trpc.io/)
- [Zod Documentation](https://zod.dev/)
