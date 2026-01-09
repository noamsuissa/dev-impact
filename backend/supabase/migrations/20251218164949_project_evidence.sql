-- Migration: Project Evidence
-- Description: Add project_evidence table for storing screenshot evidence in Supabase storage

-- ============================================
-- 1. CREATE PROJECT_EVIDENCE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS project_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES impact_projects(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT project_evidence_file_path_not_empty CHECK (length(trim(file_path)) > 0),
    CONSTRAINT project_evidence_file_name_not_empty CHECK (length(trim(file_name)) > 0),
    CONSTRAINT project_evidence_file_size_positive CHECK (file_size > 0),
    CONSTRAINT project_evidence_mime_type_image CHECK (mime_type LIKE 'image/%')
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_project_evidence_project_id ON project_evidence(project_id);
CREATE INDEX IF NOT EXISTS idx_project_evidence_display_order ON project_evidence(project_id, display_order);

ALTER TABLE project_evidence ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view evidence for their own projects
CREATE POLICY "Users can view their own project evidence"
    ON project_evidence FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM impact_projects ip
            WHERE ip.id = project_evidence.project_id
            AND ip.user_id = auth.uid()
        )
    );

-- Policy: Public can view evidence for published profiles
-- This allows anyone to see evidence for projects that are part of published profiles
-- Handles both: projects linked to specific profiles (via profile_id) and legacy user-level published profiles
CREATE POLICY "Public can view evidence for published profiles"
    ON project_evidence FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM impact_projects ip
            JOIN published_profiles pp ON (
                -- Match by profile_id if project has one, otherwise match by user_id (legacy)
                (ip.profile_id IS NOT NULL AND pp.profile_id = ip.profile_id)
                OR
                (ip.profile_id IS NULL AND pp.user_id = ip.user_id)
            )
            WHERE ip.id = project_evidence.project_id
            AND pp.is_published = true
        )
    );

-- Policy: Users can insert evidence for their own projects
CREATE POLICY "Users can insert their own project evidence"
    ON project_evidence FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM impact_projects ip
            WHERE ip.id = project_evidence.project_id
            AND ip.user_id = auth.uid()
        )
    );

-- Policy: Users can update evidence for their own projects
CREATE POLICY "Users can update their own project evidence"
    ON project_evidence FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM impact_projects ip
            WHERE ip.id = project_evidence.project_id
            AND ip.user_id = auth.uid()
        )
    );

-- Policy: Users can delete evidence for their own projects
CREATE POLICY "Users can delete their own project evidence"
    ON project_evidence FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM impact_projects ip
            WHERE ip.id = project_evidence.project_id
            AND ip.user_id = auth.uid()
        )
    );

-- Grant access to project_evidence table (RLS policies will control access)
-- Public can SELECT (for published profiles), authenticated can INSERT/UPDATE/DELETE
GRANT SELECT ON project_evidence TO anon, authenticated;
