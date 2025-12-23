-- Migration: Make Legacy Metric Columns Nullable
-- Description: Allow NULL values for primary_value and label to support standardized metrics

-- ============================================
-- MAKE LEGACY COLUMNS NULLABLE
-- ============================================

-- Drop existing NOT NULL constraints on legacy columns to allow standardized metrics
ALTER TABLE project_metrics 
ALTER COLUMN primary_value DROP NOT NULL;

ALTER TABLE project_metrics 
ALTER COLUMN label DROP NOT NULL;

-- Note: The metric_format_check constraint from the previous migration ensures
-- that either legacy format (both filled) OR standardized format (both NULL with
-- metric_type and metric_data filled) must be present.

