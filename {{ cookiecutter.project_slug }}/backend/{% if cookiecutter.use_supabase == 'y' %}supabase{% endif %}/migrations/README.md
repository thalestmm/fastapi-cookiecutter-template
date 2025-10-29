# Supabase Migrations

This directory contains all database migration files for the {{ cookiecutter.project_name }} application.

## Structure

```
migrations/
├── README.md                         # This file
└── 001_initial_schema.sql            # Initial database schema
```

## Migration Naming Convention

Migrations follow the naming pattern: `NNN_description.sql`

- `NNN` - Sequential migration number (001, 002, 003, etc.)
- `description` - Brief description of changes (lowercase, underscores)

**Examples**:
- `001_initial_schema.sql` - Create initial tables
- `002_add_whatsapp_column.sql` - Add WhatsApp column to clinic_settings
- `003_create_notifications_table.sql` - Create notifications table

## Current Migrations

---

## How to Create a New Migration

### Step 1: Create Migration File

```bash
# Using Supabase CLI (automatic naming)
supabase migration new add_notifications_table

# Or manually create
touch backend/supabase/migrations/002_add_notifications_table.sql
```

### Step 2: Write Migration SQL

```sql
-- =====================================================
-- Migration: 002_add_notifications_table
-- Description: Create notifications table for client alerts
-- =====================================================

CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read_at ON public.notifications(read_at);

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own notifications"
    ON public.notifications FOR SELECT
    USING (user_id = auth.uid());
```

### Step 3: Test Locally (if using Supabase CLI)

```bash
supabase db push
```

### Step 4: Verify Changes

```sql
-- Check new table exists
SELECT * FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'notifications';

-- Check indexes
SELECT * FROM pg_indexes 
WHERE tablename = 'notifications';

-- Check RLS policies
SELECT * FROM pg_policies 
WHERE tablename = 'notifications';
```

### Step 5: Commit to Git

```bash
git add backend/supabase/migrations/002_add_notifications_table.sql
git commit -m "migration: add notifications table"
```

---

## Migration Best Practices

### ✅ DO

- Use **IF NOT EXISTS** for idempotent migrations
- Add **descriptive comments** explaining complex changes
- Create **indexes** on foreign keys and frequently queried columns
- Use **CHECK constraints** for data validation
- Include **RLS policies** for security
- Test migrations in **development first**
- Use **CASCADE** for related data cleanup
- Keep migrations **small and focused**
- Use **clear naming** conventions

### ❌ DON'T

- ❌ Modify old migration files after they're merged
- ❌ Drop tables/columns without migration
- ❌ Use generic names like `changes.sql` or `update.sql`
- ❌ Forget to add indexes on foreign keys
- ❌ Forget RLS policies
- ❌ Leave migration files uncommitted
- ❌ Run migrations without backups in production
- ❌ Mix multiple unrelated changes in one migration

---

## Handling Migration Conflicts

### If Two Migrations Have Same Number

1. Rename the newer one to the next sequence number
2. Update the migration comments if needed
3. Re-run migrations in order

Example:
```bash
# Conflict: both are 002_*
git mv 002_notifications_table.sql 003_notifications_table.sql
git add backend/supabase/migrations/003_notifications_table.sql
git commit -m "fix: resolve migration conflict"
```

### If Migration Fails in Production

1. **DO NOT** modify the migration file
2. Create a **new rollback migration** (next number)
3. Apply the rollback migration
4. Create a **new fix migration** with corrections

Example:
```sql
-- 003_rollback_notifications_table.sql
DROP TABLE IF EXISTS public.notifications CASCADE;

-- 004_fix_notifications_table.sql
-- (corrected version of the original migration)
CREATE TABLE public.notifications (
    ...
);
```

---

## Running Migrations

### Method 1: Supabase CLI (Recommended)

```bash
cd /home/thalesmeier/Desktop/Code/lilaas-nexus
supabase db push
```

### Method 2: Supabase Dashboard

1. Go to SQL Editor
2. Copy migration content
3. Paste and run

### Method 3: Direct psql Connection

```bash
psql "postgresql://..." -f backend/supabase/migrations/001_initial_schema.sql
```

---

## Reverting Changes

### Revert Last Migration

```bash
supabase db push --dry-run  # Preview changes
supabase migration list      # List all migrations
```

### Complete Rollback

⚠️ **Development Only**

```sql
-- Run rollback migration (next sequence number)
-- Creates new migration file with DROP statements
```

### Production Rollback

1. Create new migration with data recovery SQL
2. Test thoroughly in staging
3. Run during maintenance window
4. Have backups ready

---

## Migration Status

| ID | Name | Status | Last Updated |
|----|------|--------|--------------|
| 001 | initial_schema | ✅ Production | 2025-10-25 |

---

## Related Documentation

- [Full Migration Guide](../../MIGRATION_GUIDE.md)
- [Quick Reference](../../QUICK_MIGRATION_REFERENCE.md)
- [Supabase CLI Docs](https://supabase.com/docs/guides/cli)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---