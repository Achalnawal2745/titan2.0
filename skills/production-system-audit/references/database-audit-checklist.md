# Database Audit Checklist

Use this checklist to systematically audit database schema and identify data integrity, performance, and reliability issues.

## 1. Foreign Key Constraints

**Purpose:** Enforce referential integrity at database level

**Check for:**
- [ ] All foreign key columns have explicit `.references()` constraints
- [ ] Appropriate `onDelete` behavior specified (`cascade`, `set null`, `restrict`)
- [ ] No orphaned records possible

**Example Issue:**
```typescript
// ❌ Missing FK constraint:
userId: int("userId").notNull(),

// ✅ With FK constraint:
userId: int("userId").notNull().references(() => users.id, { onDelete: "cascade" }),
```

**Common Patterns:**
- User-owned resources: `onDelete: "cascade"` (delete user → delete their data)
- Optional references: `onDelete: "set null"` (delete parent → null the reference)
- Protected references: `onDelete: "restrict"` (prevent deletion if referenced)

---

## 2. Indexes

**Purpose:** Optimize query performance

**Check for:**
- [ ] Indexes on all foreign key columns
- [ ] Composite indexes for common filter combinations
- [ ] Unique indexes on natural keys (email, username, codes)
- [ ] Full-text indexes for search columns

**Example Issues:**
```typescript
// ❌ No index on frequently queried column:
userId: int("userId").notNull(),

// ✅ With index:
userId: int("userId").notNull().index(),

// ✅ Composite index for common query pattern:
.index("idx_user_status", ["userId", "status"])
```

**When to Add Composite Indexes:**
- Queries with multiple WHERE conditions
- Common sort + filter combinations
- JOIN conditions on multiple columns

---

## 3. Unique Constraints

**Purpose:** Prevent duplicate data

**Check for:**
- [ ] Unique constraints on natural keys
- [ ] Unique constraints on codes/identifiers
- [ ] Appropriate handling of NULL values (NULL != NULL in SQL)

**Example:**
```typescript
repCode: varchar("repCode", { length: 50 }).unique(),
sessionCode: varchar("sessionCode", { length: 4 }).unique(),
```

---

## 4. Data Types & Lengths

**Purpose:** Prevent truncation and ensure appropriate storage

**Check for:**
- [ ] VARCHAR lengths appropriate for data (not too short, not excessive)
- [ ] INT vs BIGINT for auto-increment IDs (BIGINT if >2B records expected)
- [ ] TIMESTAMP vs DATETIME (prefer TIMESTAMP for UTC storage)
- [ ] ENUM vs VARCHAR (use ENUM for fixed sets, VARCHAR for extensible)

**Common Issues:**
- VARCHAR(50) for phone numbers (international format needs ~20)
- INT for session IDs (may overflow with high volume)
- DATETIME without timezone info (prefer TIMESTAMP)

---

## 5. NOT NULL Constraints

**Purpose:** Enforce required fields

**Check for:**
- [ ] All required business fields have `.notNull()`
- [ ] Foreign keys are `.notNull()` unless optional relationship
- [ ] Default values for NOT NULL columns

**Example:**
```typescript
// Required field:
name: varchar("name", { length: 255 }).notNull(),

// Optional field:
middleName: varchar("middleName", { length: 255 }),

// Required with default:
status: mysqlEnum("status", ["active", "inactive"]).default("active").notNull(),
```

---

## 6. Timestamps & Audit Trails

**Purpose:** Track record lifecycle

**Check for:**
- [ ] `createdAt` timestamp on all tables
- [ ] `updatedAt` timestamp with `.onUpdateNow()` on mutable tables
- [ ] Soft delete support if needed (`deletedAt` timestamp)

**Standard Pattern:**
```typescript
createdAt: timestamp("createdAt").defaultNow().notNull(),
updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
```

---

## 7. JSON Columns

**Purpose:** Store structured data

**Check for:**
- [ ] JSON columns have clear schema documentation
- [ ] JSON is only used when structure varies (not for fixed schema)
- [ ] Consider separate tables if querying JSON fields frequently

**When to Use JSON:**
- Variable structure (e.g., emotion scores, metadata)
- Rarely queried fields
- Third-party API responses

**When NOT to Use JSON:**
- Fixed schema that could be normalized
- Frequently queried/filtered fields
- Data requiring referential integrity

---

## 8. Enum Definitions

**Purpose:** Constrain values to valid set

**Check for:**
- [ ] All enum values are lowercase with underscores
- [ ] Enum sets are complete and unlikely to change frequently
- [ ] Consider VARCHAR if enum will expand often

**Example:**
```typescript
status: mysqlEnum("status", ["in_progress", "completed", "failed"]).default("in_progress").notNull(),
```

---

## 9. Cascading Deletes & Orphaned Records

**Purpose:** Prevent data inconsistency

**Check for:**
- [ ] Appropriate cascade behavior on all foreign keys
- [ ] No possibility of orphaned child records
- [ ] Soft delete if hard delete would break references

**Cascade Patterns:**
- User deleted → Delete their sessions (cascade)
- Session deleted → Delete conversation turns (cascade)
- Script deleted → Keep sessions, null scriptId (set null)

---

## 10. Performance Considerations

**Purpose:** Ensure scalability

**Check for:**
- [ ] No unbounded TEXT/BLOB columns without size limits
- [ ] Appropriate use of VARCHAR vs TEXT
- [ ] Indexes on columns used in ORDER BY, GROUP BY
- [ ] Avoid SELECT * in queries (specify columns)

**Common Bottlenecks:**
- Full table scans on large tables
- Missing indexes on JOIN columns
- Inefficient JSON queries
- Unbounded result sets

---

## Output Format

For each issue found, document:

1. **Severity:** Critical / High / Medium / Low
2. **Issue:** Brief description
3. **Impact:** What breaks or degrades
4. **Example:** Code snippet showing the problem
5. **Recommendation:** How to fix it

**Example:**
```
#### 🔴 HIGH: Missing Foreign Key Constraints
**Issue:** No explicit foreign key relationships defined between tables
**Impact:** Data integrity not enforced at database level
**Example:**
  practiceSessions.userId references users.id but no FK constraint
**Recommendation:** Add foreign key constraints with appropriate onDelete behavior
```
