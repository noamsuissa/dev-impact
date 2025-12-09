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

