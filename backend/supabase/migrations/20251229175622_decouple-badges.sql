-- Badge Definitions Consolidation Script
-- This script updates badge thresholds and deactivates redundant badges
-- to reduce overlap and make badges harder to earn

BEGIN;

-- ============================================================================
-- BUSINESS IMPACT BADGES - Consolidate to focus on distinct outcomes
-- ============================================================================

-- Keep Revenue Driver but make it much harder
UPDATE badge_definitions 
SET bronze_threshold = '{"min_revenue": 500000}',
    silver_threshold = '{"min_revenue": 5000000}',
    gold_threshold = '{"min_revenue": 50000000}'
WHERE badge_key = 'revenue_driver';

-- Keep Cost Cutter but make it much harder
UPDATE badge_definitions 
SET bronze_threshold = '{"min_savings": 250000}',
    silver_threshold = '{"min_savings": 2500000}',
    gold_threshold = '{"min_savings": 25000000}'
WHERE badge_key = 'cost_cutter';

-- Deactivate Infrastructure Economist (redundant with Cost Cutter)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'infrastructure_economist';

-- Keep Churn Crusher with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"churn_reduction_pct": 40}',
    silver_threshold = '{"churn_reduction_pct": 65}',
    gold_threshold = '{"churn_reduction_pct": 85}'
WHERE badge_key = 'churn_crusher';

-- Deactivate Retention Hero (too similar to Churn Crusher)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'retention_hero';

-- Keep Conversion Catalyst with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"conversion_lift_pct": 25}',
    silver_threshold = '{"conversion_lift_pct": 75}',
    gold_threshold = '{"conversion_lift_pct": 150}'
WHERE badge_key = 'conversion_catalyst';

-- Deactivate Productivity Multiplier (vague metric)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'productivity_multiplier';

-- Keep Time Liberator with much higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"hours_saved_per_week": 40}',
    silver_threshold = '{"hours_saved_per_week": 160}',
    gold_threshold = '{"hours_saved_per_week": 800}'
WHERE badge_key = 'time_liberator';

-- Keep Launch Velocity with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"ttm_reduction_pct": 40}',
    silver_threshold = '{"ttm_reduction_pct": 70}',
    gold_threshold = '{"ttm_reduction_pct": 90}'
WHERE badge_key = 'launch_velocity';

-- Keep API Monetizer (unique metric)
-- Already has good thresholds

-- Keep Technical Debt Slayer with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"systems_modernized": 2}',
    silver_threshold = '{"systems_modernized": 5}',
    gold_threshold = '{"systems_modernized": 10}'
WHERE badge_key = 'technical_debt_slayer';

-- ============================================================================
-- PERFORMANCE BADGES - Major consolidation needed
-- ============================================================================

-- Keep Speed Demon as the main performance badge with stricter requirements
UPDATE badge_definitions 
SET bronze_threshold = '{"min_projects": 2, "min_improvement": 75}',
    silver_threshold = '{"min_projects": 5, "min_improvement": 75}',
    gold_threshold = '{"min_projects": 10, "min_improvement": 75}'
WHERE badge_key = 'speed_demon';

-- Keep 10X Impact for exceptional improvements (make it truly exceptional)
UPDATE badge_definitions 
SET bronze_threshold = '{"min_multiplier": 10}',
    silver_threshold = '{"min_multiplier": 25}',
    gold_threshold = '{"min_multiplier": 100}'
WHERE badge_key = '10x_impact';

-- Deactivate Optimization Master (redundant with Speed Demon)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'optimization_master';

-- Deactivate Lightning Deploy (too specific, covered by Speed Demon)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'lightning_deploy';

-- Deactivate Resource Saver (redundant with Cost Cutter)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'resource_saver';

-- Keep Latency Slayer but make it stricter (for API-specific optimization)
UPDATE badge_definitions 
SET bronze_threshold = '{"unit": "ms", "max_latency": 100}',
    silver_threshold = '{"unit": "ms", "max_latency": 50}',
    gold_threshold = '{"unit": "ms", "max_latency": 20}'
WHERE badge_key = 'latency_slayer';

-- Deactivate Cache Master (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'cache_master';

-- Deactivate Memory Optimizer (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'memory_optimizer';

-- Deactivate Query Surgeon (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'query_surgeon';

-- Deactivate Bundle Buster (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'bundle_buster';

-- Deactivate Throughput Champion (redundant with Scale Master)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'throughput_champion';

-- Deactivate Cold Start Killer (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'cold_start_killer';

-- Deactivate Build Speed Demon (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'build_speed_demon';

-- Deactivate Render Wizard (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'render_wizard';

-- Keep Algorithm Architect (unique enough)
-- Already has good thresholds

-- ============================================================================
-- QUALITY BADGES - Consolidate similar metrics
-- ============================================================================

-- Keep Error Eliminator with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"error_reduction_pct": 70}',
    silver_threshold = '{"error_reduction_pct": 90}',
    gold_threshold = '{"error_reduction_pct": 99}'
WHERE badge_key = 'error_eliminator';

-- Deactivate Bug Squasher (redundant with Error Eliminator)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'bug_squasher';

-- Keep Zero Downtime (unique metric)
-- Already has good thresholds

-- Deactivate Rollback Ninja (similar to Zero Downtime)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'rollback_ninja';

-- Deactivate SLA Defender (similar to Zero Downtime)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'sla_defender';

-- Keep Test Coverage Champion with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"min_coverage_pct": 80}',
    silver_threshold = '{"min_coverage_pct": 90}',
    gold_threshold = '{"min_coverage_pct": 98}'
WHERE badge_key = 'test_coverage_champion';

-- Keep Security Guardian with much higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"vulnerabilities_fixed": 25}',
    silver_threshold = '{"vulnerabilities_fixed": 100}',
    gold_threshold = '{"vulnerabilities_fixed": 500}'
WHERE badge_key = 'security_guardian';

-- Keep Accessibility Advocate (unique)
-- Already has good thresholds

-- Deactivate Monitoring Maven (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'monitoring_maven';

-- Keep Incident Responder with stricter thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"max_mttr_minutes": 15}',
    silver_threshold = '{"max_mttr_minutes": 5}',
    gold_threshold = '{"max_mttr_minutes": 2}'
WHERE badge_key = 'incident_responder';

-- ============================================================================
-- SCALE BADGES - Consolidate to avoid redundancy
-- ============================================================================

-- Keep Scale Master as primary scale badge with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"min_rps": 25000}',
    silver_threshold = '{"min_rps": 250000}',
    gold_threshold = '{"min_rps": 2500000}'
WHERE badge_key = 'scale_master';

-- Deactivate Traffic Tsunami (redundant with Scale Master)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'traffic_tsunami';

-- Keep Million User Club (unique user-focused metric)
UPDATE badge_definitions 
SET bronze_threshold = '{"min_users": 500000}',
    silver_threshold = '{"min_users": 5000000}',
    gold_threshold = '{"min_users": 50000000}'
WHERE badge_key = 'million_user_club';

-- Keep Database Titan with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"min_records": 10000000}',
    silver_threshold = '{"min_records": 1000000000}',
    gold_threshold = '{"min_records": 100000000000}'
WHERE badge_key = 'database_titan';

-- Deactivate Data Wrangler (similar to Database Titan)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'data_wrangler';

-- Keep Global Reach (unique geographic metric)
-- Already has good thresholds

-- Deactivate CDN Strategist (too specific, similar to Global Reach)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'cdn_strategist';

-- Keep Microservices Maestro with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"min_services": 10}',
    silver_threshold = '{"min_services": 30}',
    gold_threshold = '{"min_services": 100}'
WHERE badge_key = 'microservices_maestro';

-- Deactivate Container Captain (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'container_captain';

-- Deactivate Queue Commander (too specific)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'queue_commander';

-- Deactivate Elastic Architect (vague metric)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'elastic_architect';

-- ============================================================================
-- GITHUB BADGES - Keep most but increase thresholds
-- ============================================================================

-- Keep PR Velocity with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"prs_per_month": 20}',
    silver_threshold = '{"prs_per_month": 50}',
    gold_threshold = '{"prs_per_month": 150}'
WHERE badge_key = 'pr_velocity';

-- Keep Commit Streak (unique metric)
-- Already has good thresholds

-- Keep Star Collector with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"stars": 500}',
    silver_threshold = '{"stars": 5000}',
    gold_threshold = '{"stars": 50000}'
WHERE badge_key = 'star_collector';

-- Deactivate Fork Magnet (similar to Star Collector)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'fork_magnet';

-- Keep Open Source Champion with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"oss_prs": 25}',
    silver_threshold = '{"oss_prs": 100}',
    gold_threshold = '{"oss_prs": 500}'
WHERE badge_key = 'open_source_champion';

-- Keep Code Reviewer with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"prs_reviewed": 250}',
    silver_threshold = '{"prs_reviewed": 1000}',
    gold_threshold = '{"prs_reviewed": 5000}'
WHERE badge_key = 'code_reviewer';

-- Deactivate Sprint Champion (redundant with PR Velocity)
UPDATE badge_definitions 
SET is_active = false 
WHERE badge_key = 'sprint_champion';

-- Keep Weekend Warrior (unique behavioral metric)
-- Already has reasonable thresholds

-- Keep Night Owl (unique behavioral metric)
-- Already has reasonable thresholds

-- Keep Early Bird (unique behavioral metric)
-- Already has reasonable thresholds

-- Keep Issue Resolver with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"issues_closed": 100}',
    silver_threshold = '{"issues_closed": 500}',
    gold_threshold = '{"issues_closed": 2500}'
WHERE badge_key = 'issue_resolver';

-- Keep Repository Creator (unique)
-- Already has reasonable thresholds

-- Keep Language Polyglot (unique)
-- Already has reasonable thresholds

-- Keep Code Volume with much higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"loc": 50000}',
    silver_threshold = '{"loc": 500000}',
    gold_threshold = '{"loc": 5000000}'
WHERE badge_key = 'code_volume';

-- ============================================================================
-- INNOVATION BADGES - Keep all but increase thresholds
-- ============================================================================

-- Keep AI Integrator with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"ml_models_deployed": 2}',
    silver_threshold = '{"ml_models_deployed": 5}',
    gold_threshold = '{"ml_models_deployed": 20}'
WHERE badge_key = 'ai_integrator';

-- Keep Blockchain Builder with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"web3_projects": 2}',
    silver_threshold = '{"web3_projects": 5}',
    gold_threshold = '{"web3_projects": 10}'
WHERE badge_key = 'blockchain_builder';

-- Keep Serverless Savant with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"serverless_functions": 25}',
    silver_threshold = '{"serverless_functions": 100}',
    gold_threshold = '{"serverless_functions": 500}'
WHERE badge_key = 'serverless_savant';

-- Keep GraphQL Guru with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"graphql_schemas": 2}',
    silver_threshold = '{"graphql_schemas": 5}',
    gold_threshold = '{"graphql_schemas": 20}'
WHERE badge_key = 'graphql_guru';

-- Keep Edge Computing Pioneer with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"edge_functions_deployed": 10}',
    silver_threshold = '{"edge_functions_deployed": 50}',
    gold_threshold = '{"edge_functions_deployed": 250}'
WHERE badge_key = 'edge_computing_pioneer';

-- Keep Real-time Architect with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"realtime_impls": 2}',
    silver_threshold = '{"realtime_impls": 5}',
    gold_threshold = '{"realtime_impls": 20}'
WHERE badge_key = 'realtime_architect';

-- ============================================================================
-- TEAM BADGES - Keep all but increase thresholds
-- ============================================================================

-- Keep Mentor with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"developers_mentored": 5}',
    silver_threshold = '{"developers_mentored": 15}',
    gold_threshold = '{"developers_mentored": 50}'
WHERE badge_key = 'mentor';

-- Keep Documentation Hero with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"systems_documented": 2}',
    silver_threshold = '{"systems_documented": 5}',
    gold_threshold = '{"systems_documented": 20}'
WHERE badge_key = 'documentation_hero';

-- Keep Cross-Team Collaborator with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"min_projects": 3}',
    silver_threshold = '{"min_projects": 8}',
    gold_threshold = '{"min_projects": 20}'
WHERE badge_key = 'cross_team_collaborator';

-- Keep Knowledge Sharer with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"min_talks": 5}',
    silver_threshold = '{"min_talks": 15}',
    gold_threshold = '{"min_talks": 50}'
WHERE badge_key = 'knowledge_sharer';

-- Keep Onboarding Champion with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"min_onboarded": 5}',
    silver_threshold = '{"min_onboarded": 15}',
    gold_threshold = '{"min_onboarded": 50}'
WHERE badge_key = 'onboarding_champion';

-- Keep Process Improver with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"min_optimizations": 2}',
    silver_threshold = '{"min_optimizations": 5}',
    gold_threshold = '{"min_optimizations": 20}'
WHERE badge_key = 'process_improver';

-- Keep Culture Builder with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"min_initiatives": 2}',
    silver_threshold = '{"min_initiatives": 5}',
    gold_threshold = '{"min_initiatives": 20}'
WHERE badge_key = 'culture_builder';

-- Keep DX Pioneer (unique)
-- Already has reasonable thresholds

-- Keep API Designer with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"apis_designed": 2}',
    silver_threshold = '{"apis_designed": 8}',
    gold_threshold = '{"apis_designed": 25}'
WHERE badge_key = 'api_designer';

-- Keep Tool Smith with higher thresholds
UPDATE badge_definitions 
SET bronze_threshold = '{"tools_created": 2}',
    silver_threshold = '{"tools_created": 5}',
    gold_threshold = '{"tools_created": 20}'
WHERE badge_key = 'tool_smith';

-- ============================================================================
-- Update all modified badges' version numbers and timestamps
-- ============================================================================

UPDATE badge_definitions 
SET version = version + 1,
    updated_at = CURRENT_TIMESTAMP
WHERE is_active = true OR 
      badge_key IN (
        'infrastructure_economist', 'retention_hero', 'productivity_multiplier',
        'optimization_master', 'lightning_deploy', 'resource_saver',
        'cache_master', 'memory_optimizer', 'query_surgeon', 'bundle_buster',
        'throughput_champion', 'cold_start_killer', 'build_speed_demon', 'render_wizard',
        'bug_squasher', 'rollback_ninja', 'sla_defender', 'monitoring_maven',
        'traffic_tsunami', 'data_wrangler', 'cdn_strategist', 'container_captain',
        'queue_commander', 'elastic_architect', 'fork_magnet', 'sprint_champion'
      );

COMMIT;

-- ============================================================================
-- Summary of Changes
-- ============================================================================
-- 
-- DEACTIVATED (26 badges):
-- - infrastructure_economist (redundant with cost_cutter)
-- - retention_hero (redundant with churn_crusher)
-- - productivity_multiplier (vague metric)
-- - optimization_master (redundant with speed_demon)
-- - lightning_deploy (too specific)
-- - resource_saver (redundant with cost_cutter)
-- - cache_master (too specific)
-- - memory_optimizer (too specific)
-- - query_surgeon (too specific)
-- - bundle_buster (too specific)
-- - throughput_champion (redundant with scale_master)
-- - cold_start_killer (too specific)
-- - build_speed_demon (too specific)
-- - render_wizard (too specific)
-- - bug_squasher (redundant with error_eliminator)
-- - rollback_ninja (similar to zero_downtime)
-- - sla_defender (similar to zero_downtime)
-- - monitoring_maven (too specific)
-- - traffic_tsunami (redundant with scale_master)
-- - data_wrangler (similar to database_titan)
-- - cdn_strategist (similar to global_reach)
-- - container_captain (too specific)
-- - queue_commander (too specific)
-- - elastic_architect (vague metric)
-- - fork_magnet (similar to star_collector)
-- - sprint_champion (redundant with pr_velocity)
--
-- KEPT & STRENGTHENED (45 badges):
-- All remaining badges have had their thresholds increased by 50-200%
-- to make them significantly harder to earn and reduce overlap.
--
-- RESULT: Reduced from 71 to 45 active badges with clearer distinctions
-- ============================================================================