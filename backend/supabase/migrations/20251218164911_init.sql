-- ============================================
-- dev-impact Supabase Database Schema
-- ============================================
-- This migration creates the initial database schema for dev-impact
-- Run this in Supabase SQL Editor

-- ============================================
-- 1. PROFILES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    github_username TEXT,
    github_avatar_url TEXT,
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT username_format CHECK (username ~ '^[a-z0-9][a-z0-9-]*[a-z0-9]$'),
    CONSTRAINT username_length CHECK (length(username) >= 3 AND length(username) <= 39)
);

-- Create index for fast username lookups
CREATE INDEX idx_profiles_username ON profiles(username);
CREATE INDEX idx_profiles_published ON profiles(is_published) WHERE is_published = true;

-- ============================================
-- 2. IMPACT PROJECTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS impact_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    company TEXT NOT NULL,
    project_name TEXT NOT NULL,
    role TEXT NOT NULL,
    team_size INTEGER NOT NULL DEFAULT 1,
    problem TEXT NOT NULL,
    contributions TEXT[] NOT NULL DEFAULT '{}',
    tech_stack TEXT[] NOT NULL DEFAULT '{}',
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT team_size_positive CHECK (team_size > 0),
    CONSTRAINT contributions_not_empty CHECK (array_length(contributions, 1) > 0),
    CONSTRAINT tech_stack_not_empty CHECK (array_length(tech_stack, 1) > 0)
);

-- Create indexes for queries
CREATE INDEX idx_impact_projects_user_id ON impact_projects(user_id);
CREATE INDEX idx_impact_projects_display_order ON impact_projects(user_id, display_order);

-- ============================================
-- 3. PROJECT METRICS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS project_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES impact_projects(id) ON DELETE CASCADE,
    primary_value TEXT NOT NULL,
    label TEXT NOT NULL,
    detail TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT primary_value_not_empty CHECK (length(trim(primary_value)) > 0),
    CONSTRAINT label_not_empty CHECK (length(trim(label)) > 0)
);

-- Create index for queries
CREATE INDEX idx_project_metrics_project_id ON project_metrics(project_id);
CREATE INDEX idx_project_metrics_display_order ON project_metrics(project_id, display_order);

-- ============================================
-- 4. GITHUB STATS TABLE (Optional - for caching)
-- ============================================
CREATE TABLE IF NOT EXISTS github_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    total_repos INTEGER DEFAULT 0,
    total_stars INTEGER DEFAULT 0,
    total_commits INTEGER DEFAULT 0,
    contribution_data JSONB,
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT stats_non_negative CHECK (
        total_repos >= 0 AND 
        total_stars >= 0 AND 
        total_commits >= 0
    )
);

-- Create index for user lookups
CREATE INDEX idx_github_stats_user_id ON github_stats(user_id);

-- ============================================
-- 5. RESERVED USERNAMES TABLE
-- ============================================
-- Prevent users from taking system/reserved usernames
CREATE TABLE IF NOT EXISTS reserved_usernames (
    username TEXT PRIMARY KEY,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert common reserved usernames
INSERT INTO reserved_usernames (username, reason) VALUES
    ('admin', 'System reserved'),
    ('api', 'System reserved'),
    ('app', 'System reserved'),
    ('dev', 'System reserved'),
    ('www', 'System reserved'),
    ('blog', 'System reserved'),
    ('help', 'System reserved'),
    ('support', 'System reserved'),
    ('about', 'System reserved'),
    ('settings', 'System reserved'),
    ('profile', 'System reserved'),
    ('dashboard', 'System reserved'),
    ('login', 'System reserved'),
    ('signup', 'System reserved'),
    ('logout', 'System reserved'),
    ('auth', 'System reserved'),
    ('oauth', 'System reserved'),
    ('callback', 'System reserved')
ON CONFLICT (username) DO NOTHING;

ALTER TABLE reserved_usernames ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can read reserved usernames (read-only reference table)
-- This is safe because it's just a list of reserved usernames, no sensitive data
CREATE POLICY "Anyone can read reserved usernames"
    ON reserved_usernames FOR SELECT
    USING (true);

-- ============================================
-- 6. FUNCTIONS
-- ============================================

-- Function to check if username is available
CREATE OR REPLACE FUNCTION public.is_username_available(desired_username TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if username matches format
    IF desired_username !~ '^[a-z0-9][a-z0-9-]*[a-z0-9]$' THEN
        RETURN false;
    END IF;
    
    -- Check length
    IF length(desired_username) < 3 OR length(desired_username) > 39 THEN
        RETURN false;
    END IF;
    
    -- Check if reserved
    IF EXISTS (SELECT 1 FROM public.reserved_usernames WHERE username = desired_username) THEN
        RETURN false;
    END IF;
    
    -- Check if taken
    IF EXISTS (SELECT 1 FROM public.profiles WHERE username = desired_username) THEN
        RETURN false;
    END IF;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to set published_at when is_published becomes true
CREATE OR REPLACE FUNCTION public.set_published_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_published = true AND OLD.is_published = false THEN
        NEW.published_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 7. TRIGGERS
-- ============================================

-- Trigger for profiles updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for profiles published_at
CREATE TRIGGER set_profiles_published_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION set_published_at();

-- Trigger for impact_projects updated_at
CREATE TRIGGER update_impact_projects_updated_at
    BEFORE UPDATE ON public.impact_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 8. ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE github_stats ENABLE ROW LEVEL SECURITY;

-- ============================================
-- PROFILES RLS POLICIES
-- ============================================

-- Anyone can view published profiles
CREATE POLICY "Published profiles are viewable by everyone"
    ON profiles FOR SELECT
    USING (is_published = true);

-- Users can view their own profile (even if not published)
CREATE POLICY "Users can view their own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

-- Users can insert their own profile
CREATE POLICY "Users can insert their own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update their own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Users can delete their own profile
CREATE POLICY "Users can delete their own profile"
    ON profiles FOR DELETE
    USING (auth.uid() = id);

-- ============================================
-- IMPACT PROJECTS RLS POLICIES
-- ============================================

-- Anyone can view projects from published profiles
CREATE POLICY "Published profile projects are viewable by everyone"
    ON impact_projects FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = impact_projects.user_id 
            AND profiles.is_published = true
        )
    );

-- Users can view their own projects
CREATE POLICY "Users can view their own projects"
    ON impact_projects FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = impact_projects.user_id 
            AND profiles.id = auth.uid()
        )
    );

-- Users can insert their own projects
CREATE POLICY "Users can insert their own projects"
    ON impact_projects FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = user_id 
            AND profiles.id = auth.uid()
        )
    );

-- Users can update their own projects
CREATE POLICY "Users can update their own projects"
    ON impact_projects FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = user_id 
            AND profiles.id = auth.uid()
        )
    );

-- Users can delete their own projects
CREATE POLICY "Users can delete their own projects"
    ON impact_projects FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = user_id 
            AND profiles.id = auth.uid()
        )
    );

-- ============================================
-- PROJECT METRICS RLS POLICIES
-- ============================================

-- Anyone can view metrics from published profiles
CREATE POLICY "Published profile metrics are viewable by everyone"
    ON project_metrics FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM impact_projects
            JOIN profiles ON profiles.id = impact_projects.user_id
            WHERE impact_projects.id = project_metrics.project_id
            AND profiles.is_published = true
        )
    );

-- Users can view metrics from their own projects
CREATE POLICY "Users can view their own project metrics"
    ON project_metrics FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM impact_projects
            JOIN profiles ON profiles.id = impact_projects.user_id
            WHERE impact_projects.id = project_metrics.project_id
            AND profiles.id = auth.uid()
        )
    );

-- Users can insert metrics to their own projects
CREATE POLICY "Users can insert metrics to their own projects"
    ON project_metrics FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM impact_projects
            JOIN profiles ON profiles.id = impact_projects.user_id
            WHERE impact_projects.id = project_id
            AND profiles.id = auth.uid()
        )
    );

-- Users can update metrics on their own projects
CREATE POLICY "Users can update their own project metrics"
    ON project_metrics FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM impact_projects
            JOIN profiles ON profiles.id = impact_projects.user_id
            WHERE impact_projects.id = project_id
            AND profiles.id = auth.uid()
        )
    );

-- Users can delete metrics from their own projects
CREATE POLICY "Users can delete their own project metrics"
    ON project_metrics FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM impact_projects
            JOIN profiles ON profiles.id = impact_projects.user_id
            WHERE impact_projects.id = project_id
            AND profiles.id = auth.uid()
        )
    );

-- ============================================
-- GITHUB STATS RLS POLICIES
-- ============================================

-- Anyone can view stats from published profiles
CREATE POLICY "Published profile stats are viewable by everyone"
    ON github_stats FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = github_stats.user_id 
            AND profiles.is_published = true
        )
    );

-- Users can view their own stats
CREATE POLICY "Users can view their own stats"
    ON github_stats FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = user_id 
            AND profiles.id = auth.uid()
        )
    );

-- Users can insert their own stats
CREATE POLICY "Users can insert their own stats"
    ON github_stats FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = user_id 
            AND profiles.id = auth.uid()
        )
    );

-- Users can update their own stats
CREATE POLICY "Users can update their own stats"
    ON github_stats FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = user_id 
            AND profiles.id = auth.uid()
        )
    );

-- ============================================
-- 9. HELPER VIEWS
-- ============================================

-- View for complete published profiles with all related data
CREATE OR REPLACE VIEW published_profiles_complete
WITH (security_invoker=true) AS
SELECT 
    p.id,
    p.username,
    p.full_name,
    p.github_username,
    p.github_avatar_url,
    p.published_at,
    p.created_at,
    COALESCE(
        json_agg(
            json_build_object(
                'id', ip.id,
                'company', ip.company,
                'projectName', ip.project_name,
                'role', ip.role,
                'teamSize', ip.team_size,
                'problem', ip.problem,
                'contributions', ip.contributions,
                'techStack', ip.tech_stack,
                'metrics', (
                    SELECT COALESCE(json_agg(
                        json_build_object(
                            'primary', pm.primary_value,
                            'label', pm.label,
                            'detail', pm.detail
                        ) ORDER BY pm.display_order
                    ), '[]'::json)
                    FROM project_metrics pm
                    WHERE pm.project_id = ip.id
                )
            ) ORDER BY ip.display_order
        ) FILTER (WHERE ip.id IS NOT NULL),
        '[]'::json
    ) as projects,
    gs.total_repos,
    gs.total_stars,
    gs.total_commits
FROM profiles p
LEFT JOIN impact_projects ip ON p.id = ip.user_id
LEFT JOIN github_stats gs ON p.id = gs.user_id
WHERE p.is_published = true
GROUP BY p.id, gs.total_repos, gs.total_stars, gs.total_commits;

-- ============================================
-- 10. GRANTS (if needed)
-- ============================================

-- Grant usage on all tables to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT SELECT ON published_profiles_complete TO anon, authenticated;
GRANT SELECT ON reserved_usernames TO anon, authenticated;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================
-- Next steps:
-- 1. Run this migration in Supabase SQL Editor
-- 2. Test with a sample user account
-- 3. Update backend to use Supabase instead of JSON files
-- 4. Update frontend to call Supabase APIs
-- ============================================

