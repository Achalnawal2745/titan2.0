---
name: "database-schema-generator"
description: "Specialized skill for database schema generator workflows and automation."
---

# Database Schema Generator

Generate production-ready PostgreSQL/Supabase database schemas from natural language descriptions using AI.

## Overview

This skill transforms natural language descriptions into complete, production-ready database schemas with:

- **PostgreSQL/Supabase SQL** - Clean, executable SQL
- **Row Level Security (RLS)** - Security policies by default
- **TypeScript Types** - Auto-generated from schema
- **Migration Files** - Version-controlled schema changes
- **Best Practices** - UUIDs, timestamps, indexes, constraints
- **Validation** - Syntax and structure checking
- **Direct Application** - Apply to Supabase via MCP

## When to Use This Skill

- Creating a new database for a project
- Adding tables to an existing database
- Designing data models from requirements
- Learning database design patterns
- Generating TypeScript types from database schema
- Creating migration files for version control

## Quick Start

### Generate a Schema

```bash
python3 scripts/generate_schema.py "A blog with users, posts, and comments"
```

### Generate with TypeScript Types

```bash
python3 scripts/generate_schema.py "E-commerce with products and orders" --output-format types
```

### Apply to Supabase

```bash
# Generate schema
python3 scripts/generate_schema.py "Task management app" --output-file schema.sql

# Validate
python3 scripts/validate_schema.py schema.sql

# Apply to Supabase
python3 scripts/apply_schema.py schema.sql --project-id YOUR_PROJECT_ID
```

## Workflow

### Step 1: Describe Your Database

Write a natural language description of what you need:

**Simple**:
```
"A blog with users, posts, and comments"
```

**Detailed**:
```
"A task management app with:
- Users with roles (admin, member)
- Projects that users can join
- Tasks within projects with assignees
- Comments on tasks
- File attachments on tasks"
```

**Domain-Specific**:
```
"An e-commerce platform with:
- Products with variants (size, color)
- Shopping cart
- Orders with line items
- Payment tracking
- Inventory management"
```

### Step 2: Generate Schema

Run the generator:

```bash
python3 scripts/generate_schema.py "<your description>" --output-file schema.sql
```

**Options**:
- `--output-format sql` - Raw SQL (default)
- `--output-format supabase` - Supabase SQL Editor format
- `--output-format migration` - Migration file format
- `--output-format types` - TypeScript types only
- `--include-rls` - Include RLS policies (default: true)
- `--no-rls` - Exclude RLS policies
- `--include-seed` - Include seed data
- `--output-file <path>` - Save to file

### Step 3: Validate Schema

Check for errors and best practices:

```bash
python3 scripts/validate_schema.py schema.sql
```

The validator checks:
- ✅ SQL syntax
- ✅ Balanced parentheses
- ✅ Common patterns (timestamps, UUIDs, indexes)
- ✅ Best practices (RLS, foreign keys)
- ✅ Table and index structure

### Step 4: Apply to Supabase

Apply the schema to your Supabase database:

```bash
python3 scripts/apply_schema.py schema.sql --project-id YOUR_PROJECT_ID
```

**Options**:
- `--dry-run` - Show what would be executed without running
- `--confirm` - Skip confirmation prompt

### Step 5: Generate TypeScript Types

Generate TypeScript types for your frontend:

```bash
python3 scripts/generate_schema.py "<description>" --output-format types --output-file types.ts
```

## Examples

### Example 1: Simple Blog

**Description**:
```
"A blog with users, posts, and comments"
```

**Generated Schema** (excerpt):
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);

-- RLS Policies
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view published posts"
  ON posts FOR SELECT
  USING (status = 'published');
```

### Example 2: E-Commerce

**Description**:
```
"E-commerce with products, orders, and customers"
```

**Command**:
```bash
python3 scripts/generate_schema.py "E-commerce with products, orders, and customers" \
  --include-seed \
  --output-file ecommerce_schema.sql
```

### Example 3: SaaS Application

**Description**:
```
"A SaaS app with:
- Organizations (workspaces)
- Users belong to organizations with roles
- Projects within organizations
- Tasks within projects
- Billing and subscriptions per organization"
```

**Command**:
```bash
python3 scripts/generate_schema.py "A SaaS app with organizations, users with roles, projects, tasks, and billing" \
  --output-format migration \
  --output-file migrations/001_initial_schema.sql
```

## Output Formats

### SQL (Default)

Clean, executable PostgreSQL SQL:

```sql
CREATE TABLE users (...);
CREATE INDEX idx_users_email ON users(email);
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
```

### Supabase

Includes Supabase-specific header and extensions:

```sql
-- Supabase SQL Editor
-- Paste this into the Supabase SQL Editor and run

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (...);
```

### Migration

Version-controlled migration file format:

```sql
-- Migration: E-commerce schema
-- Created: 2026-02-08 14:30:00

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (...);
```

### TypeScript Types

Type-safe TypeScript interfaces:

```typescript
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: Date;
  updated_at: Date;
}

export interface Post {
  id: string;
  user_id: string;
  title: string;
  content: string | null;
  status: 'draft' | 'published';
  created_at: Date;
  updated_at: Date;
}
```

## Templates

### Base Schema Template

Use `templates/base_schema.sql` for common patterns:

- Users table with Supabase Auth integration
- Timestamps with auto-update triggers
- Soft delete support
- RLS policy examples
- Index patterns
- Foreign key patterns

Copy patterns from the template into your own schemas.

## Best Practices

The generator follows these best practices automatically:

### 1. Use UUIDs for Primary Keys

```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

**Why**: Security, no collisions, client-side generation

### 2. Include Timestamps

```sql
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW()
```

**Why**: Audit trail, debugging, sorting

### 3. Add Indexes on Foreign Keys

```sql
CREATE INDEX idx_posts_user_id ON posts(user_id);
```

**Why**: Join performance

### 4. Use Check Constraints for Enums

```sql
status TEXT CHECK (status IN ('draft', 'published', 'archived'))
```

**Why**: Data validation at database level

### 5. Enable Row Level Security

```sql
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
```

**Why**: Security by default (Supabase requirement)

### 6. Use Soft Deletes

```sql
deleted_at TIMESTAMPTZ
```

**Why**: Data recovery, audit trail

### 7. Add Foreign Key Constraints

```sql
user_id UUID REFERENCES users(id) ON DELETE CASCADE
```

**Why**: Data integrity, automatic cleanup

## Common Patterns

### User-Owned Resources

```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  ...
);

-- RLS: Users can only access their own posts
CREATE POLICY "Users can view own posts"
  ON posts FOR SELECT
  USING (auth.uid() = user_id);
```

### Many-to-Many Relationships

```sql
CREATE TABLE post_tags (
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)
);
```

### Hierarchical Data (Nested Comments)

```sql
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
  ...
);
```

### Status Tracking

```sql
status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
```

## Validation

The validator checks for:

### Errors (Must Fix)
- Empty SQL file
- Unbalanced parentheses
- Invalid syntax

### Warnings (Should Fix)
- Missing semicolons
- No CREATE TABLE statements

### Recommendations (Consider)
- Add timestamps (created_at, updated_at)
- Use UUIDs for primary keys
- Add indexes for performance
- Add foreign key constraints
- Enable Row Level Security

## Applying to Supabase

### Via SQL Editor (Manual)

1. Generate schema:
   ```bash
   python3 scripts/generate_schema.py "..." --output-format supabase
   ```

2. Copy output

3. Paste into Supabase SQL Editor

4. Run

### Via MCP (Automated)

1. Generate schema:
   ```bash
   python3 scripts/generate_schema.py "..." --output-file schema.sql
   ```

2. Apply to Supabase:
   ```bash
   python3 scripts/apply_schema.py schema.sql --project-id YOUR_PROJECT_ID
   ```

3. Verify in Supabase dashboard

## Troubleshooting

### Issue: "Invalid SQL syntax"

**Solution**: Run validator to identify specific errors:
```bash
python3 scripts/validate_schema.py schema.sql
```

### Issue: "MCP command failed"

**Solution**: Check Supabase project ID and MCP configuration:
```bash
manus-mcp-cli tool list --server supabase
```

### Issue: "RLS policies not working"

**Solution**: Verify RLS is enabled:
```sql
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;
```

### Issue: "Foreign key constraint violation"

**Solution**: Ensure parent records exist before inserting child records, or use `ON DELETE CASCADE`.

## Advanced Usage

### Custom Prompts

For more control, modify the `SYSTEM_PROMPT` in `scripts/generate_schema.py`:

```python
SYSTEM_PROMPT = """You are an expert database architect...

Additional requirements:
- Use JSONB for flexible data
- Add full-text search indexes
- Include audit triggers
"""
```

### Combining with Existing Schemas

Generate new tables and merge with existing schema:

```bash
# Generate new tables
python3 scripts/generate_schema.py "Add notifications table" --output-file new_tables.sql

# Review and merge manually
cat existing_schema.sql new_tables.sql > combined_schema.sql
```

### Migration Workflow

1. Generate initial schema:
   ```bash
   python3 scripts/generate_schema.py "..." --output-format migration --output-file migrations/001_initial.sql
   ```

2. Apply to database:
   ```bash
   python3 scripts/apply_schema.py migrations/001_initial.sql --project-id YOUR_PROJECT_ID
   ```

3. For changes, generate new migration:
   ```bash
   python3 scripts/generate_schema.py "Add notifications" --output-format migration --output-file migrations/002_add_notifications.sql
   ```

## Reference Files

- `references/schema_patterns.md` - Common database patterns and best practices
- `templates/base_schema.sql` - Reusable schema patterns

## Success Criteria

✅ Schema generates without errors  
✅ Validation passes  
✅ Schema applies to Supabase successfully  
✅ RLS policies work as expected  
✅ TypeScript types match database schema  
✅ Indexes improve query performance  

## Time Savings

- **Manual schema design**: 1-2 hours
- **With this skill**: 5-10 minutes
- **Savings**: ~1.5 hours per database

## Next Steps

After generating your schema:

1. ✅ Apply to Supabase
2. ✅ Generate TypeScript types
3. ✅ Test RLS policies
4. ✅ Add seed data (if needed)
5. ✅ Build API endpoints (use api-endpoint-builder skill)
6. ✅ Write tests (use testing-framework skill)
