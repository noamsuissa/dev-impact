-- Migration: User Profiles
-- Description: Add multi-profile system where users can create multiple profiles to group projects

-- ============================================
-- 1. CREATE USER_PROFILES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    slug TEXT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT user_profiles_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT user_profiles_slug_format CHECK (slug ~ '^[a-z0-9-]+$'),
    CONSTRAINT user_profiles_slug_length CHECK (length(slug) >= 1 AND length(slug) <= 100),
    CONSTRAINT user_profiles_unique_slug_per_user UNIQUE (user_id, slug)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_slug ON user_profiles(user_id, slug);
CREATE INDEX IF NOT EXISTS idx_user_profiles_display_order ON user_profiles(user_id, display_order);

-- ============================================
-- 2. UPDATE IMPACT_PROJECTS TABLE
-- ============================================
-- Add profile_id column to link projects to profiles
ALTER TABLE impact_projects
ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL;

-- Create index for profile_id
CREATE INDEX IF NOT EXISTS idx_impact_projects_profile_id ON impact_projects(profile_id);

-- ============================================
-- 3. UPDATE PUBLISHED_PROFILES TABLE
-- ============================================
-- Add profile_id and profile_slug columns
ALTER TABLE published_profiles
ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE;

ALTER TABLE published_profiles
ADD COLUMN IF NOT EXISTS profile_slug TEXT;

-- Update unique constraint to allow multiple profiles per user
-- Drop old unique constraint on username if it exists
ALTER TABLE published_profiles
DROP CONSTRAINT IF EXISTS published_profiles_username_key;

-- Create new unique constraint on (username, profile_slug)
-- This allows username.dev-impact.io/profile-slug format
-- First, drop existing constraint if it exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'published_profiles_username_profile_slug_unique'
    ) THEN
        ALTER TABLE published_profiles
        DROP CONSTRAINT published_profiles_username_profile_slug_unique;
    END IF;
END $$;

-- Add unique constraint
ALTER TABLE published_profiles
ADD CONSTRAINT published_profiles_username_profile_slug_unique
UNIQUE (username, profile_slug);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_published_profiles_username_profile_slug
ON published_profiles(username, profile_slug);

-- Keep unique constraint on username for backward compatibility (when profile_slug is NULL)
-- This is handled by a partial unique index
CREATE UNIQUE INDEX IF NOT EXISTS idx_published_profiles_username_unique
ON published_profiles(username)
WHERE profile_slug IS NULL;

-- Create index for profile_id
CREATE INDEX IF NOT EXISTS idx_published_profiles_profile_id ON published_profiles(profile_id);

-- ============================================
-- 4. ROW LEVEL SECURITY POLICIES
-- ============================================

-- Enable RLS on user_profiles
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own profiles" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert their own profiles" ON user_profiles;
DROP POLICY IF EXISTS "Users can update their own profiles" ON user_profiles;
DROP POLICY IF EXISTS "Users can delete their own profiles" ON user_profiles;

-- Policy: Users can view their own profiles
CREATE POLICY "Users can view their own profiles"
    ON user_profiles FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own profiles
CREATE POLICY "Users can insert their own profiles"
    ON user_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own profiles
CREATE POLICY "Users can update their own profiles"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own profiles
CREATE POLICY "Users can delete their own profiles"
    ON user_profiles FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- 5. UPDATE PUBLISHED_PROFILES POLICIES
-- ============================================
-- Update existing policies to work with profile_id
-- Drop old policies that reference user_id directly
DROP POLICY IF EXISTS "Users can publish their own profile" ON published_profiles;
DROP POLICY IF EXISTS "Users can update their own published profile" ON published_profiles;
DROP POLICY IF EXISTS "Users can delete their own published profile" ON published_profiles;
DROP POLICY IF EXISTS "Users can publish their own profiles" ON published_profiles;
DROP POLICY IF EXISTS "Users can update their own published profiles" ON published_profiles;
DROP POLICY IF EXISTS "Users can delete their own published profiles" ON published_profiles;

-- New policy: Users can publish profiles they own (via profile_id)
CREATE POLICY "Users can publish their own profiles"
    ON published_profiles FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = published_profiles.profile_id
            AND user_profiles.user_id = auth.uid()
        )
    );

-- New policy: Users can update their own published profiles
CREATE POLICY "Users can update their own published profiles"
    ON published_profiles FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = published_profiles.profile_id
            AND user_profiles.user_id = auth.uid()
        )
    );

-- New policy: Users can delete their own published profiles
CREATE POLICY "Users can delete their own published profiles"
    ON published_profiles FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = published_profiles.profile_id
            AND user_profiles.user_id = auth.uid()
        )
    );

-- ============================================
-- 6. HELPER FUNCTIONS
-- ============================================

-- Function to update updated_at timestamp for user_profiles
CREATE OR REPLACE FUNCTION public.update_user_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updating updated_at
DROP TRIGGER IF EXISTS update_user_profiles_updated_at_trigger ON public.user_profiles;
CREATE TRIGGER update_user_profiles_updated_at_trigger
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_user_profiles_updated_at();

-- ============================================
-- 7. COMMENTS
-- ============================================
COMMENT ON TABLE user_profiles IS 'Stores multiple profiles per user to group related projects';
COMMENT ON COLUMN user_profiles.slug IS 'URL-friendly identifier for the profile (lowercase, dashes, unique per user)';
COMMENT ON COLUMN user_profiles.display_order IS 'Order in which profiles are displayed to the user';
COMMENT ON COLUMN impact_projects.profile_id IS 'Links project to a specific user profile (nullable for backward compatibility)';
COMMENT ON COLUMN published_profiles.profile_id IS 'References the user_profile that is published';
COMMENT ON COLUMN published_profiles.profile_slug IS 'URL slug for the profile (e.g., username.dev-impact.io/profile-slug)';
