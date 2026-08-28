

# Database Schema Patterns

Common patterns and best practices for PostgreSQL/Supabase database design.

## Table of Contents

1. [Primary Keys](#primary-keys)
2. [Timestamps](#timestamps)
3. [Soft Deletes](#soft-deletes)
4. [Foreign Keys](#foreign-keys)
5. [Indexes](#indexes)
6. [Constraints](#constraints)
7. [Row Level Security (RLS)](#row-level-security-rls)
8. [Common Table Patterns](#common-table-patterns)

---

## Primary Keys

### Pattern: UUID Primary Keys

**Use UUIDs instead of auto-incrementing integers** for better security and distributed systems support.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ...
);
```

**Why**:
- Not guessable (security)
- No collisions in distributed systems
- Can generate client-side
- Better for public-facing IDs

**When to use integers**:
- Internal lookup tables
- Performance-critical tables with millions of rows
- When you need sequential ordering

---

## Timestamps

### Pattern: Created At / Updated At

**Always include timestamp tracking** for audit trails and debugging.

```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ...
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Pattern: Auto-Update Trigger

**Automatically update `updated_at`** on every row change.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_posts_updated_at
  BEFORE UPDATE ON posts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

---

## Soft Deletes

### Pattern: Soft Delete Column

**Use `deleted_at` instead of hard deletes** to preserve data and enable recovery.

```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ...
  deleted_at TIMESTAMPTZ
);
```

### Pattern: Partial Index for Active Records

**Optimize queries on non-deleted records**.

```sql
CREATE INDEX idx_posts_active 
  ON posts(id) 
  WHERE deleted_at IS NULL;
```

### Pattern: Soft Delete in Queries

**Always filter out deleted records** in application queries.

```sql
-- Good
SELECT * FROM posts WHERE deleted_at IS NULL;

-- Better (use views)
CREATE VIEW active_posts AS
  SELECT * FROM posts WHERE deleted_at IS NULL;
```

---

## Foreign Keys

### Pattern: Foreign Key with Cascade

**Define relationship behavior** explicitly.

```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  ...
);
```

**Options**:
- `ON DELETE CASCADE` - Delete child when parent is deleted
- `ON DELETE SET NULL` - Set foreign key to NULL when parent is deleted
- `ON DELETE RESTRICT` - Prevent deletion of parent if children exist (default)

**When to use each**:
- **CASCADE**: Comments on posts (delete comments when post is deleted)
- **SET NULL**: Author of posts (keep posts when user is deleted, set author to NULL)
- **RESTRICT**: Orders with products (prevent deleting products that have orders)

---

## Indexes

### Pattern: Index Foreign Keys

**Always index foreign key columns** for join performance.

```sql
CREATE INDEX idx_posts_user_id ON posts(user_id);
```

### Pattern: Composite Index for Common Queries

**Index multiple columns** used together in WHERE clauses.

```sql
-- For queries like: WHERE user_id = ? AND status = ?
CREATE INDEX idx_posts_user_status ON posts(user_id, status);
```

**Column order matters**:
- Put most selective column first
- Put equality filters before range filters

### Pattern: Partial Index

**Index only relevant rows** to save space and improve performance.

```sql
-- Only index published posts
CREATE INDEX idx_posts_published 
  ON posts(published_at DESC) 
  WHERE status = 'published' AND deleted_at IS NULL;
```

### Pattern: Unique Index

**Enforce uniqueness** at database level.

```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
-- Or in table definition:
-- email TEXT UNIQUE NOT NULL
```

---

## Constraints

### Pattern: Check Constraint for Enums

**Validate column values** at database level.

```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status TEXT CHECK (status IN ('draft', 'published', 'archived')),
  ...
);
```

### Pattern: NOT NULL Constraints

**Require values** for essential columns.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  full_name TEXT NOT NULL,
  ...
);
```

### Pattern: Unique Constraints

**Prevent duplicates** for business-critical columns.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  username TEXT UNIQUE NOT NULL,
  ...
);
```

---

## Row Level Security (RLS)

### Pattern: Enable RLS

**Always enable RLS** for Supabase tables.

```sql
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
```

### Pattern: User-Owned Resources

**Users can only access their own data**.

```sql
-- Read own posts
CREATE POLICY "Users can view own posts"
  ON posts FOR SELECT
  USING (auth.uid() = user_id);

-- Insert own posts
CREATE POLICY "Users can insert own posts"
  ON posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Update own posts
CREATE POLICY "Users can update own posts"
  ON posts FOR UPDATE
  USING (auth.uid() = user_id);

-- Delete own posts
CREATE POLICY "Users can delete own posts"
  ON posts FOR DELETE
  USING (auth.uid() = user_id);
```

### Pattern: Public Read, Authenticated Write

**Anyone can read, only logged-in users can write**.

```sql
CREATE POLICY "Anyone can view published posts"
  ON posts FOR SELECT
  USING (status = 'published' AND deleted_at IS NULL);

CREATE POLICY "Authenticated users can insert posts"
  ON posts FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);
```

### Pattern: Role-Based Access

**Different permissions for different roles**.

```sql
-- Admins can see all posts
CREATE POLICY "Admins can view all posts"
  ON posts FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );
```

---

## Common Table Patterns

### Pattern: Users Table

**Integrate with Supabase Auth**.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);
```

### Pattern: Posts/Articles Table

**Content with status and publishing**.

```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  content TEXT,
  excerpt TEXT,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);
```

### Pattern: Comments Table

**Nested comments with parent reference**.

```sql
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES comments(id) ON DELETE CASCADE, -- For nested comments
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);
```

### Pattern: Tags/Categories (Many-to-Many)

**Junction table for many-to-many relationships**.

```sql
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE post_tags (
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)
);

CREATE INDEX idx_post_tags_post ON post_tags(post_id);
CREATE INDEX idx_post_tags_tag ON post_tags(tag_id);
```

### Pattern: Likes/Reactions

**User interactions with content**.

```sql
CREATE TABLE post_likes (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, post_id)
);

CREATE INDEX idx_post_likes_post ON post_likes(post_id);
```

### Pattern: Followers/Following

**Social relationships**.

```sql
CREATE TABLE follows (
  follower_id UUID REFERENCES users(id) ON DELETE CASCADE,
  following_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (follower_id, following_id),
  CHECK (follower_id != following_id) -- Can't follow yourself
);

CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);
```

### Pattern: Notifications

**User notifications with read status**.

```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('comment', 'like', 'follow', 'mention')),
  title TEXT NOT NULL,
  message TEXT,
  link TEXT,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, created_at DESC) WHERE read_at IS NULL;
```

### Pattern: Audit Log

**Track all changes for compliance**.

```sql
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  table_name TEXT NOT NULL,
  record_id UUID NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
  old_data JSONB,
  new_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
```

---

## Performance Tips

1. **Index foreign keys** - Always
2. **Use partial indexes** - For filtered queries
3. **Composite indexes** - For multi-column queries
4. **EXPLAIN ANALYZE** - Test query performance
5. **Avoid SELECT *** - Select only needed columns
6. **Use connection pooling** - Supabase includes this
7. **Batch operations** - Use bulk inserts/updates
8. **Denormalize when needed** - For read-heavy tables

---

## Security Tips

1. **Enable RLS** - Always, for all tables
2. **Use UUIDs** - Not guessable
3. **Validate at database** - Use CHECK constraints
4. **Soft delete** - Preserve data
5. **Audit logs** - Track changes
6. **Principle of least privilege** - Minimal permissions
7. **Encrypt sensitive data** - Use pgcrypto

---

## Naming Conventions

- **Tables**: Plural, snake_case (`users`, `blog_posts`)
- **Columns**: Singular, snake_case (`user_id`, `created_at`)
- **Indexes**: `idx_table_column` (`idx_users_email`)
- **Foreign keys**: `fk_table_column` (optional, auto-generated)
- **Constraints**: `chk_table_condition` (`chk_users_role`)
- **Triggers**: `trigger_table_action` (`update_users_updated_at`)

---

## Common Mistakes to Avoid

1. ❌ No indexes on foreign keys
2. ❌ Using integers for public IDs
3. ❌ No timestamps
4. ❌ Hard deletes instead of soft deletes
5. ❌ No RLS policies
6. ❌ SELECT * in production
7. ❌ No constraints or validation
8. ❌ Inconsistent naming conventions
9. ❌ No audit trail
10. ❌ Premature optimization

---

## Further Reading

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase Database Guide](https://supabase.com/docs/guides/database)
- [Database Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)
