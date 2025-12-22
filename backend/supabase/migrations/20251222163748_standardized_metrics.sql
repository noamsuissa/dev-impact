-- Migration: Standardized Project Metrics
-- Description: Add support for structured metrics with types, units, comparisons, and context

-- ============================================
-- 1. ADD NEW COLUMNS TO PROJECT_METRICS TABLE
-- ============================================

-- Add metric_type column for categorization
ALTER TABLE project_metrics 
ADD COLUMN IF NOT EXISTS metric_type TEXT;

-- Add metric_data column for storing full structured metric as JSONB
ALTER TABLE project_metrics 
ADD COLUMN IF NOT EXISTS metric_data JSONB;

-- ============================================
-- 2. ADD CONSTRAINTS
-- ============================================

-- Add check constraint to ensure either legacy format OR new format is present
-- Legacy format: primary_value and label must be set
-- New format: metric_type and metric_data must be set
ALTER TABLE project_metrics
ADD CONSTRAINT metric_format_check CHECK (
    (primary_value IS NOT NULL AND label IS NOT NULL AND metric_type IS NULL AND metric_data IS NULL)
    OR
    (metric_type IS NOT NULL AND metric_data IS NOT NULL)
);

-- Add check constraint for metric_type values
ALTER TABLE project_metrics
ADD CONSTRAINT metric_type_valid CHECK (
    metric_type IS NULL OR 
    metric_type IN ('performance', 'scale', 'business', 'quality', 'time')
);

-- ============================================
-- 3. CREATE INDEX FOR METRIC_TYPE
-- ============================================

-- Index for filtering/grouping by metric type (useful for future badge/leaderboard features)
CREATE INDEX IF NOT EXISTS idx_project_metrics_type ON project_metrics(metric_type) 
WHERE metric_type IS NOT NULL;

-- ============================================
-- 4. ADD COMMENTS
-- ============================================

COMMENT ON COLUMN project_metrics.metric_type IS 'Type of metric: performance, scale, business, quality, or time';
COMMENT ON COLUMN project_metrics.metric_data IS 'Structured metric data in JSONB format containing primary, comparison, context, and timeframe';
COMMENT ON COLUMN project_metrics.primary_value IS 'Legacy: Simple metric value (kept for backward compatibility)';
COMMENT ON COLUMN project_metrics.label IS 'Legacy: Simple metric label (kept for backward compatibility)';
COMMENT ON COLUMN project_metrics.detail IS 'Legacy: Simple metric detail (kept for backward compatibility)';

