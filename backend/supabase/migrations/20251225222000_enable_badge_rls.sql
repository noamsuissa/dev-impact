-- ============================================================================
-- ENABLE ROW LEVEL SECURITY FOR BADGE TABLES
-- Enables RLS on all badge-related tables to avoid errors
-- Note: Using service keys, so policies are not strictly enforced
-- ============================================================================

-- Enable RLS on badge_categories
ALTER TABLE badge_categories ENABLE ROW LEVEL SECURITY;

-- Enable RLS on badge_definitions
ALTER TABLE badge_definitions ENABLE ROW LEVEL SECURITY;

-- Enable RLS on user_badges
ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;

-- Enable RLS on badge_progress
ALTER TABLE badge_progress ENABLE ROW LEVEL SECURITY;

-- Enable RLS on badge_audit_log
ALTER TABLE badge_audit_log ENABLE ROW LEVEL SECURITY;

