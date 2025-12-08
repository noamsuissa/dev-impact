# Migration Scripts

## check_migrations.py

Verifies that all required database migrations have been applied to your Supabase database.

### Usage

```bash
cd backend
python scripts/check_migrations.py
```

### What it checks

The script verifies that the following tables exist:
- `profiles` (from 001_initial_schema.sql)
- `published_profiles` (from 002_published_profiles.sql)
- `user_profiles` (from 003_user_profiles.sql)

### Output

- ✓ EXISTS - Table exists and migration has been applied
- ✗ MISSING - Table is missing, migration needs to be run

### Requirements

- `.env` file must be configured with `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` (or `SUPABASE_ANON_KEY`)
