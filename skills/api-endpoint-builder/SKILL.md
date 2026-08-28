---
name: "api-endpoint-builder"
description: "Specialized skill for api endpoint builder workflows and automation."
---

# API Endpoint Builder

Generate production-ready API endpoints from natural language descriptions using AI.

## Overview

This skill transforms natural language API specifications into complete, type-safe endpoints with:

- **Multiple Frameworks** - Next.js App Router, tRPC, Express
- **Input Validation** - Zod schemas for type-safe validation
- **Authentication** - Built-in auth middleware
- **Error Handling** - Consistent error responses
- **TypeScript** - Full type safety
- **Best Practices** - RESTful design, proper status codes
- **Ready to Deploy** - Production-ready code

## When to Use This Skill

- Building REST APIs for web applications
- Creating tRPC routers for type-safe APIs
- Adding new endpoints to existing APIs
- Learning API design patterns
- Rapid prototyping of backend services

## Quick Start

### Generate Next.js Endpoints

```bash
python3 scripts/generate_endpoints.py "CRUD endpoints for blog posts"
```

### Generate tRPC Router

```bash
python3 scripts/generate_endpoints.py "User management API" --framework trpc
```

### Generate Express Routes

```bash
python3 scripts/generate_endpoints.py "Product catalog endpoints" --framework express
```

## Workflow

### Step 1: Describe Your API

Write a natural language description of the endpoints you need:

**Simple**:
```
"CRUD endpoints for blog posts"
```

**Detailed**:
```
"User management API with:
- List all users (paginated)
- Get user by ID
- Create new user
- Update user profile
- Delete user
- Get user's posts"
```

**Specific Requirements**:
```
"E-commerce product API with:
- List products with filtering (category, price range)
- Search products
- Get product details with reviews
- Add product to cart
- Update cart quantity
- Checkout"
```

### Step 2: Generate Endpoints

Run the generator:

```bash
python3 scripts/generate_endpoints.py "<your description>" [options]
```

**Options**:
- `--framework nextjs` - Next.js App Router (default)
- `--framework trpc` - tRPC router
- `--framework express` - Express.js router
- `--auth` - Include authentication (default: true)
- `--no-auth` - Exclude authentication
- `--validation` - Include Zod validation (default: true)
- `--no-validation` - Exclude validation
- `--output-dir <path>` - Output directory (default: current)

### Step 3: Review Generated Code

The generator creates files with clear structure:

**Next.js**:
```
app/api/posts/route.ts         # List & create
app/api/posts/[id]/route.ts    # Get, update, delete
```

**tRPC**:
```
server/api/routers/posts.ts    # Router with all procedures
```

**Express**:
```
routes/posts.ts                # Router with all routes
```

### Step 4: Integrate into Project

1. Copy generated files to your project
2. Adjust imports and database calls
3. Test endpoints
4. Deploy

## Examples

### Example 1: Blog API (Next.js)

**Description**:
```
"CRUD endpoints for blog posts with title, content, and status"
```

**Command**:
```bash
python3 scripts/generate_endpoints.py "CRUD endpoints for blog posts" --output-dir api/
```

**Generated** (excerpt):
```typescript
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const createPostSchema = z.object({
  title: z.string().min(1).max(255),
  content: z.string().min(1),
  status: z.enum(['draft', 'published']).default('draft'),
});

export async function GET(request: NextRequest) {
  // List posts with pagination
}

export async function POST(request: NextRequest) {
  // Create new post with validation and auth
}
```

### Example 2: User Management (tRPC)

**Description**:
```
"User management API with list, get, create, update, delete"
```

**Command**:
```bash
python3 scripts/generate_endpoints.py "User management API" --framework trpc
```

**Generated** (excerpt):
```typescript
export const userRouter = createTRPCRouter({
  getAll: publicProcedure
    .input(z.object({ limit: z.number().default(10) }))
    .query(async ({ ctx, input }) => {
      // List users
    }),

  create: protectedProcedure
    .input(z.object({ email: z.string().email(), name: z.string() }))
    .mutation(async ({ ctx, input }) => {
      // Create user
    }),
});
```

### Example 3: E-Commerce (Express)

**Description**:
```
"Product catalog API with search, filtering, and cart management"
```

**Command**:
```bash
python3 scripts/generate_endpoints.py "Product catalog API" --framework express --output-dir routes/
```

## Framework Comparison

### Next.js App Router

**Best for**: Full-stack Next.js applications

**Pros**:
- Integrated with Next.js
- Server components support
- Built-in caching
- Easy deployment (Vercel)

**Cons**:
- Next.js specific
- More boilerplate than tRPC

**Example**:
```typescript
// app/api/posts/route.ts
export async function GET(request: NextRequest) {
  const posts = await db.post.findMany();
  return NextResponse.json(posts);
}
```

### tRPC

**Best for**: Type-safe full-stack TypeScript apps

**Pros**:
- End-to-end type safety
- No code generation
- Excellent DX
- Built-in validation

**Cons**:
- TypeScript only
- Requires tRPC setup

**Example**:
```typescript
export const postRouter = createTRPCRouter({
  getAll: publicProcedure.query(async ({ ctx }) => {
    return await ctx.db.post.findMany();
  }),
});
```

### Express

**Best for**: Standalone Node.js APIs

**Pros**:
- Framework agnostic
- Mature ecosystem
- Flexible
- Works with any frontend

**Cons**:
- More setup required
- Less type safety
- Manual validation

**Example**:
```typescript
router.get('/posts', async (req, res) => {
  const posts = await db.post.findMany();
  res.json(posts);
});
```

## Common Patterns

### CRUD Operations

**Create, Read, Update, Delete** for any resource:

```
"CRUD endpoints for [resource]"
```

Generates:
- `GET /api/[resource]` - List all
- `POST /api/[resource]` - Create
- `GET /api/[resource]/[id]` - Get one
- `PUT /api/[resource]/[id]` - Update
- `DELETE /api/[resource]/[id]` - Delete

### Pagination

Automatically includes pagination for list endpoints:

```typescript
GET /api/posts?limit=10&page=1
```

### Authentication

Protected endpoints check for authenticated user:

```typescript
const session = await getServerSession();
if (!session?.user) {
  return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
}
```

### Authorization (Ownership)

Checks if user owns the resource:

```typescript
if (post.userId !== session.user.id) {
  return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
}
```

### Input Validation

All inputs validated with Zod:

```typescript
const schema = z.object({
  title: z.string().min(1).max(255),
  content: z.string(),
});

const data = schema.parse(body);
```

### Error Handling

Consistent error responses:

```typescript
try {
  // Logic
} catch (error) {
  if (error instanceof z.ZodError) {
    return NextResponse.json(
      { error: 'Validation failed', details: error.errors },
      { status: 400 }
    );
  }
  return NextResponse.json(
    { error: 'Internal server error' },
    { status: 500 }
  );
}
```

## Templates

### tRPC Router Template

Use `templates/trpc_router.ts` for tRPC patterns:
- Public queries
- Protected mutations
- Pagination
- Error handling
- Ownership checks

### Next.js Route Template

Use `templates/nextjs_route.ts` for Next.js patterns:
- GET, POST, PUT, DELETE handlers
- Query parameter parsing
- Authentication checks
- Validation
- Error handling

## Best Practices

The generator follows these best practices automatically:

### 1. Proper HTTP Methods

- `GET` for reading
- `POST` for creating
- `PUT/PATCH` for updating
- `DELETE` for deleting

### 2. Correct Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `500` - Server error

### 3. Input Validation

All inputs validated with Zod schemas before processing.

### 4. Authentication

Protected endpoints check for authenticated users.

### 5. Authorization

Ownership checks before modifying resources.

### 6. Error Handling

Consistent error format with proper status codes.

### 7. TypeScript

Full type safety throughout.

### 8. Pagination

List endpoints include pagination by default.

## Customization

### Adjust Validation

Modify Zod schemas in generated code:

```typescript
// Generated
title: z.string().min(1).max(255)

// Customize
title: z.string().min(5).max(100)
```

### Add Custom Logic

Insert business logic in generated endpoints:

```typescript
export async function POST(request: NextRequest) {
  // Generated validation
  const data = schema.parse(body);
  
  // Add custom logic
  if (await isDuplicate(data.title)) {
    return NextResponse.json(
      { error: 'Title already exists' },
      { status: 409 }
    );
  }
  
  // Generated creation
  const post = await db.post.create({ data });
}
```

### Change Database Calls

Replace Prisma calls with your ORM:

```typescript
// Generated (Prisma)
const posts = await db.post.findMany();

// Replace with Supabase
const { data: posts } = await supabase.from('posts').select('*');

// Or raw SQL
const posts = await sql`SELECT * FROM posts`;
```

## Integration with Other Skills

### With database-schema-generator

1. Generate database schema
2. Generate TypeScript types
3. Generate API endpoints
4. Endpoints use generated types

### With testing-framework

1. Generate API endpoints
2. Generate tests for endpoints
3. Run tests
4. Deploy with confidence

## Troubleshooting

### Issue: "Generated code doesn't compile"

**Solution**: Check imports and adjust for your project structure:
```typescript
// Generated
import { db } from '~/server/db';

// Adjust to your project
import { db } from '@/lib/db';
```

### Issue: "Authentication not working"

**Solution**: Ensure auth setup matches your project:
```typescript
// For NextAuth
import { getServerSession } from 'next-auth';

// For Supabase
import { createServerClient } from '@supabase/ssr';
```

### Issue: "Validation errors not showing"

**Solution**: Check Zod error handling:
```typescript
if (error instanceof z.ZodError) {
  return NextResponse.json(
    { error: 'Validation failed', details: error.errors },
    { status: 400 }
  );
}
```

## Advanced Usage

### Multiple Resources

Generate endpoints for multiple resources:

```bash
python3 scripts/generate_endpoints.py "CRUD for posts" --output-dir api/posts/
python3 scripts/generate_endpoints.py "CRUD for comments" --output-dir api/comments/
python3 scripts/generate_endpoints.py "CRUD for users" --output-dir api/users/
```

### Complex Relationships

Describe relationships in the specification:

```
"Blog API with:
- Posts with author and comments
- Comments belong to posts and users
- Users can like posts
- Tags for posts (many-to-many)"
```

### Custom Middleware

Add custom middleware to generated endpoints:

```typescript
// Add rate limiting
import { rateLimit } from '@/lib/rate-limit';

export async function POST(request: NextRequest) {
  if (!rateLimit(request.ip)) {
    return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
  }
  
  // Generated code
}
```

## Reference Files

- `references/api_patterns.md` - API design patterns and best practices
- `templates/trpc_router.ts` - tRPC router template
- `templates/nextjs_route.ts` - Next.js route template

## Success Criteria

✅ Endpoints generate without errors  
✅ Code compiles in your project  
✅ Validation works correctly  
✅ Authentication checks pass  
✅ Error handling is consistent  
✅ Endpoints follow REST principles  
✅ TypeScript types are correct  

## Time Savings

- **Manual endpoint creation**: 45-60 minutes
- **With this skill**: 5-10 minutes
- **Savings**: ~45 minutes per API

## Next Steps

After generating your endpoints:

1. ✅ Review generated code
2. ✅ Adjust validation schemas
3. ✅ Integrate with database
4. ✅ Test endpoints
5. ✅ Add custom business logic
6. ✅ Write tests (use testing-framework skill)
7. ✅ Deploy
