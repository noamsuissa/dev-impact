-- ============================================================================
-- BADGE CATEGORIES TABLE
-- Metadata about badge categories for organization
-- ============================================================================
CREATE TABLE IF NOT EXISTS badge_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    color VARCHAR(50),
    display_order INTEGER DEFAULT 0,
    
    -- Stats (can be computed or cached)
    total_badges INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- BADGE DEFINITIONS TABLE
-- Stores all available badge types and their metadata
-- ============================================================================
CREATE TABLE IF NOT EXISTS badge_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Info
    badge_key VARCHAR(100) UNIQUE NOT NULL, -- e.g. 'speed_demon', 'cache_master'
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL REFERENCES badge_categories(name), -- 'performance', 'scale', 'business', 'quality', 'time', 'innovation', 'team', 'github'
    
    -- Tier System
    has_tiers BOOLEAN DEFAULT true,
    bronze_threshold JSONB, -- Flexible threshold definition
    silver_threshold JSONB,
    gold_threshold JSONB,
    
    -- Requirements & Calculation
    metric_type VARCHAR(50), -- Links to project metric types: 'performance', 'scale', 'business', 'quality', 'time'
    calculation_type VARCHAR(50) NOT NULL, -- 'aggregate', 'single_project', 'github_sync', 'manual', 'time_based'
    calculation_logic JSONB, -- Stores complex calculation rules
    
    -- Data Source
    data_source VARCHAR(50) NOT NULL DEFAULT 'project_metrics', -- 'project_metrics', 'github_api', 'user_profile', 'custom'
    requires_github BOOLEAN DEFAULT false,
    
    -- Display
    icon_name VARCHAR(100), -- For future icon system
    color_scheme JSONB, -- {bronze: '#CD7F32', silver: '#C0C0C0', gold: '#FFD700'}
    display_order INTEGER DEFAULT 0,
    
    -- Visibility & Status
    is_active BOOLEAN DEFAULT true,
    is_hidden BOOLEAN DEFAULT false, -- Hidden badges (easter eggs)
    is_beta BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- Index for fast lookups
CREATE INDEX idx_badge_definitions_category ON badge_definitions(category);
CREATE INDEX idx_badge_definitions_active ON badge_definitions(is_active) WHERE is_active = true;
CREATE INDEX idx_badge_definitions_key ON badge_definitions(badge_key);

-- ============================================================================
-- USER BADGES TABLE
-- Tracks which badges users have earned
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relations
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES badge_definitions(id) ON DELETE CASCADE,
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE, -- Optional: link to specific portfolio
    
    -- Achievement Details
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('bronze', 'silver', 'gold', 'platinum')), -- Added platinum for future
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Supporting Data
    achievement_value NUMERIC, -- The actual value that earned the badge (e.g., 95.5 for 95.5% performance improvement)
    achievement_data JSONB, -- Flexible field for badge-specific data
    
    -- Source Tracking
    source_project_ids UUID[], -- Array of project IDs that contributed
    source_metric_ids UUID[], -- Array of metric IDs that contributed
    github_data JSONB, -- For GitHub-synced badges
    
    -- Display & Sharing
    is_featured BOOLEAN DEFAULT false, -- User can feature badges on profile
    is_public BOOLEAN DEFAULT true, -- User can hide specific badges
    display_order INTEGER,
    
    -- Progression Tracking
    progress_to_next_tier NUMERIC, -- Percentage progress to next tier (0-100)
    previous_tier VARCHAR(20), -- For tracking upgrades
    upgraded_at TIMESTAMPTZ, -- When last upgraded
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, badge_id, tier) -- User can't earn same badge+tier twice
);

-- Indexes for performance
CREATE INDEX idx_user_badges_user ON user_badges(user_id);
CREATE INDEX idx_user_badges_badge ON user_badges(badge_id);
CREATE INDEX idx_user_badges_earned ON user_badges(earned_at DESC);
CREATE INDEX idx_user_badges_featured ON user_badges(user_id, is_featured) WHERE is_featured = true;
CREATE INDEX idx_user_badges_portfolio ON user_badges(portfolio_id) WHERE portfolio_id IS NOT NULL;

-- ============================================================================
-- BADGE PROGRESS TABLE
-- Tracks user progress toward badges they haven't earned yet
-- ============================================================================
CREATE TABLE IF NOT EXISTS badge_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES badge_definitions(id) ON DELETE CASCADE,
    
    -- Progress Tracking
    current_value NUMERIC NOT NULL DEFAULT 0,
    target_value NUMERIC NOT NULL,
    target_tier VARCHAR(20) NOT NULL CHECK (target_tier IN ('bronze', 'silver', 'gold', 'platinum')),
    progress_percentage NUMERIC GENERATED ALWAYS AS (
        CASE 
            WHEN target_value > 0 THEN LEAST(100, (current_value / target_value * 100))
            ELSE 0
        END
    ) STORED,
    
    -- Supporting Data
    contributing_projects UUID[], -- Projects contributing to progress
    last_contribution_at TIMESTAMPTZ,
    progress_data JSONB, -- Flexible field for badge-specific progress tracking
    
    -- Metadata
    first_tracked_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, badge_id, target_tier)
);

CREATE INDEX idx_badge_progress_user ON badge_progress(user_id);
CREATE INDEX idx_badge_progress_updated ON badge_progress(last_updated_at DESC);

-- ============================================================================
-- BADGE AUDIT LOG
-- Track all badge-related events for debugging and analytics
-- ============================================================================
CREATE TABLE IF NOT EXISTS badge_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES badge_definitions(id) ON DELETE CASCADE,
    
    event_type VARCHAR(50) NOT NULL, -- 'earned', 'upgraded', 'revoked', 'progress_updated'
    tier VARCHAR(20),
    old_value NUMERIC,
    new_value NUMERIC,
    
    event_data JSONB,
    triggered_by VARCHAR(50), -- 'manual', 'automatic', 'github_sync', 'recalculation'
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_badge_audit_user ON badge_audit_log(user_id, created_at DESC);
CREATE INDEX idx_badge_audit_badge ON badge_audit_log(badge_id, created_at DESC);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to relevant tables
CREATE TRIGGER update_badge_definitions_updated_at BEFORE UPDATE ON badge_definitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_badges_updated_at BEFORE UPDATE ON user_badges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_badge_progress_updated_at BEFORE UPDATE ON badge_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- User badge summary with definition details
CREATE OR REPLACE VIEW user_badges_with_details AS
SELECT 
    ub.*,
    bd.badge_key,
    bd.name,
    bd.description,
    bd.category,
    bd.icon_name,
    bd.color_scheme
FROM user_badges ub
JOIN badge_definitions bd ON ub.badge_id = bd.id
WHERE bd.is_active = true;

-- User badge statistics
CREATE OR REPLACE VIEW user_badge_stats AS
SELECT 
    ub.user_id,
    COUNT(*) as total_badges,
    COUNT(*) FILTER (WHERE ub.tier = 'bronze') as bronze_count,
    COUNT(*) FILTER (WHERE ub.tier = 'silver') as silver_count,
    COUNT(*) FILTER (WHERE ub.tier = 'gold') as gold_count,
    COUNT(DISTINCT ub.badge_id) as unique_badges,
    MAX(ub.earned_at) as most_recent_badge,
    (
        SELECT jsonb_object_agg(category, category_count)
        FROM (
            SELECT bd.category, COUNT(*) as category_count
            FROM user_badges ub2
            JOIN badge_definitions bd ON ub2.badge_id = bd.id
            WHERE ub2.user_id = ub.user_id
            GROUP BY bd.category
        ) category_counts
    ) as badges_by_category
FROM user_badges ub
GROUP BY ub.user_id;