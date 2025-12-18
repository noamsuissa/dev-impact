-- Migration: Waitlist
-- Description: Add waitlist table for collecting user emails before launch

-- ============================================
-- 1. CREATE WAITLIST TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS waitlist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    notified_at TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT waitlist_email_not_empty CHECK (length(trim(email)) > 0),
    CONSTRAINT waitlist_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist(email);
CREATE INDEX IF NOT EXISTS idx_waitlist_created_at ON waitlist(created_at);

-- ============================================
-- 2. ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on waitlist table
ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists (for idempotency)
DROP POLICY IF EXISTS "Anyone can sign up for waitlist" ON waitlist;

-- Policy: Allow anonymous users to insert (sign up for waitlist)
CREATE POLICY "Anyone can sign up for waitlist"
    ON waitlist FOR INSERT
    WITH CHECK (true);

-- Note: No SELECT/UPDATE/DELETE policies are created
-- This means only the service role (which bypasses RLS) can perform these operations
-- This protects email addresses from being exposed if the anon key is accidentally used
