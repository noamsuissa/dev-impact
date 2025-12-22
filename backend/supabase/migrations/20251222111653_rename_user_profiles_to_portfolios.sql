-- Migration: Rename user_profiles to portfolios
-- Description: Rename user_profiles table to portfolios to better reflect that these are organizational tabs containing projects

-- ============================================
-- 1. RENAME TABLE
-- ============================================
ALTER TABLE user_profiles RENAME TO portfolios;

-- ============================================
-- 2. RENAME INDEXES
-- ============================================
ALTER INDEX IF EXISTS idx_user_profiles_user_id RENAME TO idx_portfolios_user_id;
ALTER INDEX IF EXISTS idx_user_profiles_slug RENAME TO idx_portfolios_slug;
ALTER INDEX IF EXISTS idx_user_profiles_display_order RENAME TO idx_portfolios_display_order;

-- ============================================
-- 3. RENAME CONSTRAINTS
-- ============================================
ALTER TABLE portfolios RENAME CONSTRAINT user_profiles_name_not_empty TO portfolios_name_not_empty;
ALTER TABLE portfolios RENAME CONSTRAINT user_profiles_slug_format TO portfolios_slug_format;
ALTER TABLE portfolios RENAME CONSTRAINT user_profiles_slug_length TO portfolios_slug_length;
ALTER TABLE portfolios RENAME CONSTRAINT user_profiles_unique_slug_per_user TO portfolios_unique_slug_per_user;

-- ============================================
-- 4. UPDATE RLS POLICIES
-- ============================================
-- Drop old policies
DROP POLICY IF EXISTS "Users can view their own profiles" ON portfolios;
DROP POLICY IF EXISTS "Users can insert their own profiles" ON portfolios;
DROP POLICY IF EXISTS "Users can update their own profiles" ON portfolios;
DROP POLICY IF EXISTS "Users can delete their own profiles" ON portfolios;

-- Create new policies with updated names
CREATE POLICY "Users can view their own portfolios"
    ON portfolios FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own portfolios"
    ON portfolios FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own portfolios"
    ON portfolios FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own portfolios"
    ON portfolios FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- 5. UPDATE PUBLISHED_PROFILES POLICIES
-- ============================================
-- Update policies to reference portfolios table
DROP POLICY IF EXISTS "Users can publish their own profiles" ON published_profiles;
DROP POLICY IF EXISTS "Users can update their own published profiles" ON published_profiles;
DROP POLICY IF EXISTS "Users can delete their own published profiles" ON published_profiles;

CREATE POLICY "Users can publish their own portfolios"
    ON published_profiles FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM portfolios 
            WHERE portfolios.id = published_profiles.profile_id 
            AND portfolios.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own published portfolios"
    ON published_profiles FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM portfolios 
            WHERE portfolios.id = published_profiles.profile_id 
            AND portfolios.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete their own published portfolios"
    ON published_profiles FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM portfolios 
            WHERE portfolios.id = published_profiles.profile_id 
            AND portfolios.user_id = auth.uid()
        )
    );

-- ============================================
-- 6. RENAME TRIGGER FUNCTIONS
-- ============================================
ALTER FUNCTION update_user_profiles_updated_at() RENAME TO update_portfolios_updated_at;

-- Drop old trigger
DROP TRIGGER IF EXISTS update_user_profiles_updated_at_trigger ON portfolios;

-- Create new trigger with updated name
CREATE TRIGGER update_portfolios_updated_at_trigger
    BEFORE UPDATE ON portfolios
    FOR EACH ROW
    EXECUTE FUNCTION update_portfolios_updated_at();

-- ============================================
-- 7. UPDATE COMMENTS
-- ============================================
COMMENT ON TABLE portfolios IS 'Stores multiple portfolios per user to group related projects';
COMMENT ON COLUMN portfolios.slug IS 'URL-friendly identifier for the portfolio (lowercase, dashes, unique per user)';
COMMENT ON COLUMN portfolios.display_order IS 'Order in which portfolios are displayed to the user';
COMMENT ON COLUMN published_profiles.profile_id IS 'References the portfolio that is published';
COMMENT ON COLUMN published_profiles.profile_slug IS 'URL slug for the portfolio (e.g., username.dev-impact.io/portfolio-slug)';
COMMENT ON COLUMN impact_projects.profile_id IS 'Links project to a specific portfolio (nullable for backward compatibility)';

-- Note: Foreign key constraints in impact_projects and published_profiles remain unchanged
-- as they reference the table by OID, not by name. The references are automatically updated.

