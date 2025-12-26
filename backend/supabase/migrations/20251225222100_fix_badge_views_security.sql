-- ============================================================================
-- FIX BADGE VIEWS SECURITY
-- Updates views to use security_invoker=true for proper RLS handling
-- ============================================================================

-- Recreate user_badges_with_details view with security_invoker
CREATE OR REPLACE VIEW user_badges_with_details
WITH (security_invoker=true) AS
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

-- Recreate user_badge_stats view with security_invoker
CREATE OR REPLACE VIEW user_badge_stats
WITH (security_invoker=true) AS
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

