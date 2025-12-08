#!/usr/bin/env python3
"""
Migration Verification Script
Checks if required database tables exist in Supabase
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def check_table_exists(supabase: Client, table_name: str) -> bool:
    """Check if a table exists by trying to query it"""
    try:
        # Try to select from the table (limit 0 to avoid fetching data)
        result = supabase.table(table_name).select("id").limit(0).execute()
        return True
    except Exception as e:
        error_str = str(e).lower()
        if "could not find the table" in error_str or "relation" in error_str and "does not exist" in error_str:
            return False
        # If it's a different error (like permission), the table might exist
        # But we'll return False to be safe
        print(f"Warning: Error checking table {table_name}: {e}")
        return False

def main():
    """Check if all required migrations have been applied"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        sys.exit(1)
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Required tables from migrations
    required_tables = [
        ("profiles", "001_initial_schema.sql"),
        ("published_profiles", "002_published_profiles.sql"),
        ("user_profiles", "003_user_profiles.sql"),
    ]
    
    print("Checking database migrations...")
    print("=" * 60)
    
    all_exist = True
    for table_name, migration_file in required_tables:
        exists = check_table_exists(supabase, table_name)
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"{status} - {table_name:25} (from {migration_file})")
        if not exists:
            all_exist = False
    
    print("=" * 60)
    
    if all_exist:
        print("\n✓ All migrations have been applied successfully!")
        return 0
    else:
        print("\n✗ Some migrations are missing!")
        print("\nTo apply missing migrations:")
        print("1. Open Supabase Dashboard → SQL Editor")
        print("2. Run the migration files in order:")
        print("   - migrations/001_initial_schema.sql")
        print("   - migrations/002_published_profiles.sql")
        print("   - migrations/003_user_profiles.sql")
        print("3. After running migrations, PostgREST will automatically refresh its schema cache")
        return 1

if __name__ == "__main__":
    sys.exit(main())
