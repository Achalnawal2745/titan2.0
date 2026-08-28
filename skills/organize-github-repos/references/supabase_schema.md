# Maverick Town Supabase Schema Reference

## Overview

This document describes the expected Supabase schema for the Maverick Town project, specifically the tables related to GitHub repository management.

## Tables

### repositories

**Purpose**: Store metadata about connected GitHub repositories

**Schema**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `name` | TEXT | NO | Repository name (e.g., "my-repo") |
| `owner` | TEXT | NO | GitHub owner/organization (e.g., "username") |
| `github_url` | TEXT | NO | Full GitHub URL (e.g., "https://github.com/username/my-repo") |
| `visibility` | TEXT | NO | "public" or "private" |
| `default_branch` | TEXT | YES | Default branch name (e.g., "main", "master") |
| `description` | TEXT | YES | Repository description |
| `last_sync` | TIMESTAMP | YES | Last successful sync timestamp |
| `active` | BOOLEAN | NO | Whether the repository is actively tracked (default: true) |
| `created_at` | TIMESTAMP | NO | When the record was created |
| `updated_at` | TIMESTAMP | NO | When the record was last updated |
| `webhook_id` | TEXT | YES | GitHub webhook ID for this repository |
| `webhook_secret` | TEXT | YES | Secret for webhook validation |

**Indexes**:
- Primary key on `id`
- Unique index on `(owner, name)`
- Index on `active` for filtering
- Index on `last_sync` for sorting

**Example Query**:
```sql
SELECT id, name, owner, github_url, visibility, default_branch, last_sync, active
FROM repositories
WHERE active = true
ORDER BY last_sync DESC NULLS LAST;
```

---

### sync_logs

**Purpose**: Track synchronization events and errors

**Schema**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `repository_id` | UUID | NO | Foreign key to `repositories.id` |
| `sync_type` | TEXT | NO | Type of sync: "full", "incremental", "webhook" |
| `status` | TEXT | NO | Status: "success", "failure", "partial" |
| `started_at` | TIMESTAMP | NO | When the sync started |
| `completed_at` | TIMESTAMP | YES | When the sync completed |
| `error_message` | TEXT | YES | Error message if status = "failure" |
| `records_processed` | INTEGER | YES | Number of records processed |
| `records_failed` | INTEGER | YES | Number of records that failed |
| `metadata` | JSONB | YES | Additional sync metadata |

**Indexes**:
- Primary key on `id`
- Foreign key on `repository_id` references `repositories(id)`
- Index on `status` for filtering
- Index on `started_at` for sorting

**Example Query**:
```sql
SELECT sl.*, r.name as repo_name, r.owner
FROM sync_logs sl
JOIN repositories r ON sl.repository_id = r.id
WHERE sl.status = 'failure'
  AND sl.started_at > NOW() - INTERVAL '7 days'
ORDER BY sl.started_at DESC;
```

---

### webhook_events

**Purpose**: Store incoming webhook events from GitHub

**Schema**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `repository_id` | UUID | NO | Foreign key to `repositories.id` |
| `event_type` | TEXT | NO | GitHub event type (e.g., "push", "pull_request") |
| `payload` | JSONB | NO | Full webhook payload |
| `received_at` | TIMESTAMP | NO | When the webhook was received |
| `processed` | BOOLEAN | NO | Whether the event has been processed (default: false) |
| `processed_at` | TIMESTAMP | YES | When the event was processed |
| `processing_error` | TEXT | YES | Error message if processing failed |

**Indexes**:
- Primary key on `id`
- Foreign key on `repository_id` references `repositories(id)`
- Index on `processed` for filtering unprocessed events
- Index on `received_at` for sorting

**Example Query**:
```sql
SELECT we.*, r.name as repo_name
FROM webhook_events we
JOIN repositories r ON we.repository_id = r.id
WHERE we.processed = false
  AND we.received_at > NOW() - INTERVAL '1 hour'
ORDER BY we.received_at ASC;
```

---

## Foreign Key Relationships

```
repositories (1) ──< (N) sync_logs
repositories (1) ──< (N) webhook_events
```

## Common Queries

### Get all repositories with failed syncs in the last 24 hours
```sql
SELECT DISTINCT r.*
FROM repositories r
JOIN sync_logs sl ON r.id = sl.repository_id
WHERE sl.status = 'failure'
  AND sl.started_at > NOW() - INTERVAL '24 hours'
  AND r.active = true;
```

### Get repositories that haven't synced recently
```sql
SELECT *
FROM repositories
WHERE active = true
  AND (last_sync IS NULL OR last_sync < NOW() - INTERVAL '7 days');
```

### Get webhook events that failed to process
```sql
SELECT we.*, r.name, r.owner
FROM webhook_events we
JOIN repositories r ON we.repository_id = r.id
WHERE we.processed = true
  AND we.processing_error IS NOT NULL
ORDER BY we.received_at DESC
LIMIT 50;
```

## Data Integrity Constraints

1. **No orphaned sync logs**: All `sync_logs.repository_id` must reference valid `repositories.id`
2. **No orphaned webhook events**: All `webhook_events.repository_id` must reference valid `repositories.id`
3. **Unique repository identifiers**: Each `(owner, name)` pair must be unique
4. **Valid visibility values**: `repositories.visibility` must be either "public" or "private"
5. **Valid sync status values**: `sync_logs.status` must be one of "success", "failure", "partial"
6. **Timestamps are reasonable**: `created_at` <= `updated_at`, `started_at` <= `completed_at`

## Expected Data Types

- **UUID**: Standard UUID v4 format
- **TEXT**: UTF-8 encoded strings
- **TIMESTAMP**: ISO 8601 format with timezone (e.g., "2026-02-10T12:00:00+00:00")
- **BOOLEAN**: true/false
- **INTEGER**: Signed 32-bit integer
- **JSONB**: Valid JSON stored in binary format

## Notes for Verification Script

When comparing Supabase data with GitHub:

1. **Repository name**: Supabase `name` should match GitHub `name`
2. **Owner**: Supabase `owner` should match GitHub `owner.login`
3. **Visibility**: Supabase `visibility` should match GitHub `private` (true → "private", false → "public")
4. **Default branch**: Supabase `default_branch` should match GitHub `default_branch`
5. **URL format**: Supabase `github_url` should be `https://github.com/{owner}/{name}`

## Troubleshooting

**"Foreign key constraint violation"**
- Ensure repository exists before creating sync_logs or webhook_events
- Check that repository_id is valid UUID

**"Unique constraint violation on (owner, name)"**
- Repository already exists in Supabase
- Check for case sensitivity issues (GitHub is case-insensitive for usernames)

**"Invalid timestamp format"**
- Ensure timestamps include timezone information
- Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS+00:00`
