-- Migration: Rename profile_id to portfolio_id in foreign key columns
-- Description: Update foreign key column names to use consistent "portfolio" terminology

-- ============================================
-- 1. RENAME FOREIGN KEY COLUMNS
-- ============================================

-- Rename profile_id to portfolio_id in impact_projects table
ALTER TABLE impact_projects RENAME COLUMN profile_id TO portfolio_id;

-- Rename profile_id to portfolio_id in published_profiles table
ALTER TABLE published_profiles RENAME COLUMN profile_id TO portfolio_id;

-- ============================================
-- 2. UPDATE COLUMN COMMENTS
-- ============================================

COMMENT ON COLUMN impact_projects.portfolio_id IS 'Links project to a specific portfolio (nullable for unassigned projects)';
COMMENT ON COLUMN published_profiles.portfolio_id IS 'References the portfolio that is published';

-- Note: Foreign key constraints remain functional as they reference tables by OID, not by column name
-- The constraints automatically work with the renamed columns
