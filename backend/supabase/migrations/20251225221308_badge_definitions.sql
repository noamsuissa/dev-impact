-- ============================================================================
-- INSERT BADGE CATEGORIES
-- ============================================================================
INSERT INTO badge_categories (name, display_name, description, display_order) VALUES
('performance', 'Performance & Optimization', 'Speed, efficiency, and resource optimization achievements', 1),
('scale', 'Scale & Infrastructure', 'Massive scale and infrastructure achievements', 2),
('business', 'Business Impact', 'Revenue, cost savings, and business value achievements', 3),
('quality', 'Quality & Reliability', 'Uptime, testing, and quality achievements', 4),
('time', 'Time & Tenure', 'Time-based and consistency achievements', 5),
('innovation', 'Innovation & Technology', 'Cutting-edge tech and innovation achievements', 6),
('team', 'Team & Collaboration', 'Leadership, mentorship, and collaboration achievements', 7),
('github', 'GitHub Activity', 'Open source and code contribution achievements', 8);

-- ============================================================================
-- INSERT ALL 79 BADGE DEFINITIONS
-- ============================================================================

-- PERFORMANCE & OPTIMIZATION (25 badges)
INSERT INTO badge_definitions (badge_key, name, description, category, metric_type, calculation_type, bronze_threshold, silver_threshold, gold_threshold, data_source) VALUES
('speed_demon', 'Speed Demon', 'Achieved significant performance improvements across multiple projects', 'performance', 'performance', 'aggregate', 
    '{"min_projects": 1, "min_improvement": 50}'::jsonb,
    '{"min_projects": 3, "min_improvement": 50}'::jsonb,
    '{"min_projects": 5, "min_improvement": 50}'::jsonb, 'project_metrics'),

('lightning_deploy', 'Lightning Deploy', 'Achieved sub-second load times', 'performance', 'time', 'single_project',
    '{"max_time": 1000, "unit": "ms"}'::jsonb,
    '{"max_time": 500, "unit": "ms"}'::jsonb,
    '{"max_time": 100, "unit": "ms"}'::jsonb, 'project_metrics'),

('10x_impact', '10X Impact', 'Delivered exponential performance improvements', 'performance', 'performance', 'single_project',
    '{"min_multiplier": 5}'::jsonb,
    '{"min_multiplier": 10}'::jsonb,
    '{"min_multiplier": 50}'::jsonb, 'project_metrics'),

('optimization_master', 'Optimization Master', 'Consistent high-level optimization across all projects', 'performance', 'performance', 'aggregate',
    '{"avg_improvement": 30}'::jsonb,
    '{"avg_improvement": 50}'::jsonb,
    '{"avg_improvement": 80}'::jsonb, 'project_metrics'),

('resource_saver', 'Resource Saver', 'Achieved major cost reductions through optimization', 'performance', 'business', 'aggregate',
    '{"cost_reduction_pct": 20}'::jsonb,
    '{"cost_reduction_pct": 50}'::jsonb,
    '{"cost_reduction_pct": 80}'::jsonb, 'project_metrics'),

('cache_master', 'Cache Master', 'Achieved exceptional cache hit rates', 'performance', 'performance', 'single_project',
    '{"min_hit_rate": 80}'::jsonb,
    '{"min_hit_rate": 95}'::jsonb,
    '{"min_hit_rate": 99}'::jsonb, 'project_metrics'),

('memory_optimizer', 'Memory Optimizer', 'Significantly reduced memory footprint', 'performance', 'performance', 'single_project',
    '{"memory_reduction_pct": 30}'::jsonb,
    '{"memory_reduction_pct": 60}'::jsonb,
    '{"memory_reduction_pct": 80}'::jsonb, 'project_metrics'),

('query_surgeon', 'Query Surgeon', 'Dramatically optimized database query performance', 'performance', 'performance', 'single_project',
    '{"query_improvement": "50%"}'::jsonb,
    '{"query_improvement": "10x"}'::jsonb,
    '{"query_improvement": "100x"}'::jsonb, 'project_metrics'),

('bundle_buster', 'Bundle Buster', 'Significantly reduced bundle sizes', 'performance', 'performance', 'single_project',
    '{"bundle_reduction_pct": 30}'::jsonb,
    '{"bundle_reduction_pct": 50}'::jsonb,
    '{"bundle_reduction_pct": 70}'::jsonb, 'project_metrics'),

('latency_slayer', 'Latency Slayer', 'Achieved ultra-low API response times', 'performance', 'time', 'single_project',
    '{"max_latency": 200, "unit": "ms"}'::jsonb,
    '{"max_latency": 100, "unit": "ms"}'::jsonb,
    '{"max_latency": 50, "unit": "ms"}'::jsonb, 'project_metrics'),

('throughput_champion', 'Throughput Champion', 'Massively increased request throughput', 'performance', 'performance', 'single_project',
    '{"throughput_multiplier": 2}'::jsonb,
    '{"throughput_multiplier": 5}'::jsonb,
    '{"throughput_multiplier": 10}'::jsonb, 'project_metrics'),

('cold_start_killer', 'Cold Start Killer', 'Optimized serverless cold start times', 'performance', 'time', 'single_project',
    '{"max_cold_start": 2000, "unit": "ms"}'::jsonb,
    '{"max_cold_start": 1000, "unit": "ms"}'::jsonb,
    '{"max_cold_start": 500, "unit": "ms"}'::jsonb, 'project_metrics'),

('build_speed_demon', 'Build Speed Demon', 'Dramatically accelerated CI/CD pipeline', 'performance', 'time', 'single_project',
    '{"build_improvement_pct": 50}'::jsonb,
    '{"build_improvement_pct": 75}'::jsonb,
    '{"build_improvement_pct": 90}'::jsonb, 'project_metrics'),

('render_wizard', 'Render Wizard', 'Achieved lightning-fast first contentful paint', 'performance', 'time', 'single_project',
    '{"max_fcp": 2000, "unit": "ms"}'::jsonb,
    '{"max_fcp": 1000, "unit": "ms"}'::jsonb,
    '{"max_fcp": 500, "unit": "ms"}'::jsonb, 'project_metrics'),

('algorithm_architect', 'Algorithm Architect', 'Improved algorithmic complexity significantly', 'performance', 'performance', 'single_project',
    '{"complexity_improvement": "O(n²) to O(n log n)"}'::jsonb,
    '{"complexity_improvement": "O(n log n) to O(n)"}'::jsonb,
    '{"complexity_improvement": "O(n) to O(1)"}'::jsonb, 'project_metrics');

-- SCALE & INFRASTRUCTURE (11 badges)
INSERT INTO badge_definitions (badge_key, name, description, category, metric_type, calculation_type, bronze_threshold, silver_threshold, gold_threshold, data_source) VALUES
('million_user_club', 'Million User Club', 'Served massive user bases', 'scale', 'scale', 'single_project',
    '{"min_users": 100000}'::jsonb,
    '{"min_users": 1000000}'::jsonb,
    '{"min_users": 10000000}'::jsonb, 'project_metrics'),

('global_reach', 'Global Reach', 'Deployed across multiple regions', 'scale', 'scale', 'single_project',
    '{"min_regions": 2}'::jsonb,
    '{"min_regions": 5}'::jsonb,
    '{"global": true}'::jsonb, 'project_metrics'),

('scale_master', 'Scale Master', 'Handled massive concurrent load', 'scale', 'scale', 'single_project',
    '{"min_rps": 10000}'::jsonb,
    '{"min_rps": 100000}'::jsonb,
    '{"min_rps": 1000000}'::jsonb, 'project_metrics'),

('traffic_tsunami', 'Traffic Tsunami', 'Handled peak traffic at scale', 'scale', 'scale', 'single_project',
    '{"min_concurrent": 10000}'::jsonb,
    '{"min_concurrent": 100000}'::jsonb,
    '{"min_concurrent": 1000000}'::jsonb, 'project_metrics'),

('data_wrangler', 'Data Wrangler', 'Processed massive data volumes', 'scale', 'scale', 'single_project',
    '{"min_data": "1TB"}'::jsonb,
    '{"min_data": "100TB"}'::jsonb,
    '{"min_data": "1PB"}'::jsonb, 'project_metrics'),

('microservices_maestro', 'Microservices Maestro', 'Orchestrated complex microservices architecture', 'scale', 'scale', 'single_project',
    '{"min_services": 5}'::jsonb,
    '{"min_services": 20}'::jsonb,
    '{"min_services": 50}'::jsonb, 'project_metrics'),

('elastic_architect', 'Elastic Architect', 'Built highly elastic auto-scaling systems', 'scale', 'scale', 'single_project',
    '{"scaling_capacity": "2x"}'::jsonb,
    '{"scaling_capacity": "10x"}'::jsonb,
    '{"scaling_capacity": "100x"}'::jsonb, 'project_metrics'),

('queue_commander', 'Queue Commander', 'Handled massive message throughput', 'scale', 'scale', 'single_project',
    '{"min_msgs_per_sec": 10000}'::jsonb,
    '{"min_msgs_per_sec": 100000}'::jsonb,
    '{"min_msgs_per_sec": 1000000}'::jsonb, 'project_metrics'),

('database_titan', 'Database Titan', 'Managed databases at massive scale', 'scale', 'scale', 'single_project',
    '{"min_records": 1000000}'::jsonb,
    '{"min_records": 100000000}'::jsonb,
    '{"min_records": 1000000000}'::jsonb, 'project_metrics'),

('cdn_strategist', 'CDN Strategist', 'Deployed across global edge locations', 'scale', 'scale', 'single_project',
    '{"min_edge_locations": 10}'::jsonb,
    '{"min_edge_locations": 50}'::jsonb,
    '{"min_edge_locations": 200}'::jsonb, 'project_metrics'),

('container_captain', 'Container Captain', 'Managed large Kubernetes deployments', 'scale', 'scale', 'single_project',
    '{"min_pods": 100}'::jsonb,
    '{"min_pods": 1000}'::jsonb,
    '{"min_pods": 10000}'::jsonb, 'project_metrics');

-- BUSINESS IMPACT (11 badges)
INSERT INTO badge_definitions (badge_key, name, description, category, metric_type, calculation_type, bronze_threshold, silver_threshold, gold_threshold, data_source) VALUES
('revenue_driver', 'Revenue Driver', 'Generated significant business value', 'business', 'business', 'aggregate',
    '{"min_revenue": 100000}'::jsonb,
    '{"min_revenue": 1000000}'::jsonb,
    '{"min_revenue": 10000000}'::jsonb, 'project_metrics'),

('cost_cutter', 'Cost Cutter', 'Achieved major cost savings', 'business', 'business', 'aggregate',
    '{"min_savings": 50000}'::jsonb,
    '{"min_savings": 500000}'::jsonb,
    '{"min_savings": 5000000}'::jsonb, 'project_metrics'),

('time_liberator', 'Time Liberator', 'Automated away significant manual work', 'business', 'time', 'aggregate',
    '{"hours_saved_per_week": 10}'::jsonb,
    '{"hours_saved_per_week": 50}'::jsonb,
    '{"hours_saved_per_week": 200}'::jsonb, 'project_metrics'),

('conversion_catalyst', 'Conversion Catalyst', 'Dramatically improved conversion rates', 'business', 'business', 'single_project',
    '{"conversion_lift_pct": 10}'::jsonb,
    '{"conversion_lift_pct": 50}'::jsonb,
    '{"conversion_lift_pct": 100}'::jsonb, 'project_metrics'),

('retention_hero', 'Retention Hero', 'Significantly improved user retention', 'business', 'business', 'single_project',
    '{"retention_increase_pct": 20}'::jsonb,
    '{"retention_increase_pct": 50}'::jsonb,
    '{"retention_increase_pct": 80}'::jsonb, 'project_metrics'),

('churn_crusher', 'Churn Crusher', 'Dramatically reduced user churn', 'business', 'business', 'single_project',
    '{"churn_reduction_pct": 25}'::jsonb,
    '{"churn_reduction_pct": 50}'::jsonb,
    '{"churn_reduction_pct": 75}'::jsonb, 'project_metrics'),

('launch_velocity', 'Launch Velocity', 'Accelerated time to market', 'business', 'time', 'single_project',
    '{"ttm_reduction_pct": 20}'::jsonb,
    '{"ttm_reduction_pct": 50}'::jsonb,
    '{"ttm_reduction_pct": 80}'::jsonb, 'project_metrics'),

('technical_debt_slayer', 'Technical Debt Slayer', 'Modernized legacy systems', 'business', 'quality', 'aggregate',
    '{"systems_modernized": 1}'::jsonb,
    '{"systems_modernized": 3}'::jsonb,
    '{"systems_modernized": 5}'::jsonb, 'project_metrics'),

('infrastructure_economist', 'Infrastructure Economist', 'Optimized cloud infrastructure costs', 'business', 'business', 'single_project',
    '{"cost_optimization_pct": 15}'::jsonb,
    '{"cost_optimization_pct": 40}'::jsonb,
    '{"cost_optimization_pct": 70}'::jsonb, 'project_metrics'),

('api_monetizer', 'API Monetizer', 'Generated revenue from API products', 'business', 'business', 'single_project',
    '{"monthly_revenue": 10000}'::jsonb,
    '{"monthly_revenue": 100000}'::jsonb,
    '{"monthly_revenue": 1000000}'::jsonb, 'project_metrics'),

('productivity_multiplier', 'Productivity Multiplier', 'Boosted team velocity significantly', 'business', 'business', 'single_project',
    '{"velocity_increase_pct": 25}'::jsonb,
    '{"velocity_increase_pct": 75}'::jsonb,
    '{"velocity_increase_pct": 150}'::jsonb, 'project_metrics');

-- QUALITY & RELIABILITY (10 badges)
INSERT INTO badge_definitions (badge_key, name, description, category, metric_type, calculation_type, bronze_threshold, silver_threshold, gold_threshold, data_source) VALUES
('zero_downtime', 'Zero Downtime', 'Achieved exceptional uptime', 'quality', 'quality', 'single_project',
    '{"min_uptime_pct": 99.9}'::jsonb,
    '{"min_uptime_pct": 99.99}'::jsonb,
    '{"min_uptime_pct": 99.999}'::jsonb, 'project_metrics'),

('bug_squasher', 'Bug Squasher', 'Dramatically reduced defect rates', 'quality', 'quality', 'single_project',
    '{"defect_reduction_pct": 30}'::jsonb,
    '{"defect_reduction_pct": 60}'::jsonb,
    '{"defect_reduction_pct": 90}'::jsonb, 'project_metrics'),

('security_guardian', 'Security Guardian', 'Fixed critical vulnerabilities', 'quality', 'quality', 'aggregate',
    '{"vulnerabilities_fixed": 10}'::jsonb,
    '{"vulnerabilities_fixed": 50}'::jsonb,
    '{"vulnerabilities_fixed": 200}'::jsonb, 'project_metrics'),

('test_coverage_champion', 'Test Coverage Champion', 'Achieved comprehensive test coverage', 'quality', 'quality', 'single_project',
    '{"min_coverage_pct": 70}'::jsonb,
    '{"min_coverage_pct": 85}'::jsonb,
    '{"min_coverage_pct": 95}'::jsonb, 'project_metrics'),

('error_eliminator', 'Error Eliminator', 'Reduced error rates dramatically', 'quality', 'quality', 'single_project',
    '{"error_reduction_pct": 50}'::jsonb,
    '{"error_reduction_pct": 80}'::jsonb,
    '{"error_reduction_pct": 95}'::jsonb, 'project_metrics'),

('sla_defender', 'SLA Defender', 'Maintained exceptional SLA compliance', 'quality', 'quality', 'single_project',
    '{"min_sla_compliance": 95}'::jsonb,
    '{"min_sla_compliance": 99}'::jsonb,
    '{"min_sla_compliance": 99.9}'::jsonb, 'project_metrics'),

('incident_responder', 'Incident Responder', 'Achieved rapid mean time to recovery', 'quality', 'time', 'single_project',
    '{"max_mttr_minutes": 30}'::jsonb,
    '{"max_mttr_minutes": 10}'::jsonb,
    '{"max_mttr_minutes": 5}'::jsonb, 'project_metrics'),

('monitoring_maven', 'Monitoring Maven', 'Implemented comprehensive observability', 'quality', 'quality', 'single_project',
    '{"observability_coverage": 70}'::jsonb,
    '{"observability_coverage": 90}'::jsonb,
    '{"observability_coverage": 99}'::jsonb, 'project_metrics'),

('rollback_ninja', 'Rollback Ninja', 'Achieved zero-incident deployment streak', 'quality', 'quality', 'aggregate',
    '{"successful_deployments": 10}'::jsonb,
    '{"successful_deployments": 50}'::jsonb,
    '{"successful_deployments": 200}'::jsonb, 'project_metrics'),

('accessibility_advocate', 'Accessibility Advocate', 'Achieved WCAG compliance', 'quality', 'quality', 'single_project',
    '{"wcag_level": "A"}'::jsonb,
    '{"wcag_level": "AA"}'::jsonb,
    '{"wcag_level": "AAA"}'::jsonb, 'project_metrics');

-- DEVELOPER EXPERIENCE (7 badges)
INSERT INTO badge_definitions (badge_key, name, description, category, metric_type, calculation_type, bronze_threshold, silver_threshold, gold_threshold, data_source) VALUES
('documentation_hero', 'Documentation Hero', 'Created comprehensive documentation', 'team', null, 'manual',
    '{"systems_documented": 1}'::jsonb,
    '{"systems_documented": 3}'::jsonb,
    '{"systems_documented": 10}'::jsonb, 'custom'),

('code_reviewer', 'Code Reviewer', 'Reviewed extensive pull requests', 'github', null, 'github_sync',
    '{"prs_reviewed": 100}'::jsonb,
    '{"prs_reviewed": 500}'::jsonb,
    '{"prs_reviewed": 2000}'::jsonb, 'github_api'),

('mentor', 'Mentor', 'Mentored fellow developers', 'team', null, 'manual',
    '{"developers_mentored": 3}'::jsonb,
    '{"developers_mentored": 10}'::jsonb,
    '{"developers_mentored": 25}'::jsonb, 'custom'),

('open_source_champion', 'Open Source Champion', 'Made significant OSS contributions', 'github', null, 'github_sync',
    '{"oss_prs": 10}'::jsonb,
    '{"oss_prs": 50}'::jsonb,
    '{"oss_prs": 200}'::jsonb, 'github_api'),

('tool_smith', 'Tool Smith', 'Built internal developer tools', 'team', null, 'manual',
    '{"tools_created": 1}'::jsonb,
    '{"tools_created": 3}'::jsonb,
    '{"tools_created": 10}'::jsonb, 'custom'),

('api_designer', 'API Designer', 'Designed well-documented APIs', 'team', null, 'manual',
    '{"apis_designed": 1}'::jsonb,
    '{"apis_designed": 5}'::jsonb,
    '{"apis_designed": 15}'::jsonb, 'custom'),

('dx_pioneer', 'DX Pioneer', 'Achieved high developer satisfaction', 'team', null, 'manual',
    '{"satisfaction_score": 70}'::jsonb,
    '{"satisfaction_score": 85}'::jsonb,
    '{"satisfaction_score": 95}'::jsonb, 'custom');

-- INNOVATION & TECHNOLOGY (6 badges)
INSERT INTO badge_definitions (badge_key, name, description, category, metric_type, calculation_type, bronze_threshold, silver_threshold, gold_threshold, data_source) VALUES
('ai_integrator', 'AI Integrator', 'Deployed machine learning models to production systems', 'innovation', 'ai', 'aggregate',
    '{"ml_models_deployed": 1}'::jsonb,
    '{"ml_models_deployed": 3}'::jsonb,
    '{"ml_models_deployed": 10}'::jsonb, 'project_metrics'),

('realtime_architect', 'Real-time Architect', 'Implemented real-time communication using WebSocket or SSE', 'innovation', 'realtime', 'aggregate',
    '{"realtime_impls": 1}'::jsonb,
    '{"realtime_impls": 3}'::jsonb,
    '{"realtime_impls": 10}'::jsonb, 'project_metrics'),

('blockchain_builder', 'Blockchain Builder', 'Launched projects using Web3 or blockchain technology', 'innovation', 'blockchain', 'aggregate',
    '{"web3_projects": 1}'::jsonb,
    '{"web3_projects": 3}'::jsonb,
    '{"web3_projects": 5}'::jsonb, 'project_metrics'),

('edge_computing_pioneer', 'Edge Computing Pioneer', 'Deployed edge functions to production', 'innovation', 'edge', 'aggregate',
    '{"edge_functions_deployed": 5}'::jsonb,
    '{"edge_functions_deployed": 20}'::jsonb,
    '{"edge_functions_deployed": 100}'::jsonb, 'project_metrics'),

('graphql_guru', 'GraphQL Guru', 'Designed GraphQL APIs and schemas', 'innovation', 'graphql', 'aggregate',
    '{"graphql_schemas": 1}'::jsonb,
    '{"graphql_schemas": 3}'::jsonb,
    '{"graphql_schemas": 10}'::jsonb, 'project_metrics'),

('serverless_savant', 'Serverless Savant', 'Deployed serverless functions (e.g., Lambda, Cloud Functions)', 'innovation', 'serverless', 'aggregate',
    '{"serverless_functions": 10}'::jsonb,
    '{"serverless_functions": 50}'::jsonb,
    '{"serverless_functions": 200}'::jsonb, 'project_metrics');

-- GITHUB-SYNCED BADGES (12 badges)
INSERT INTO badge_definitions (badge_key, name, description, category, metric_type, calculation_type, bronze_threshold, silver_threshold, gold_threshold, data_source, requires_github) VALUES
('commit_streak', 'Commit Streak', 'Consecutive days with at least one GitHub commit', 'github', 'commit_streak', 'github_sync',
    '{"min_days": 30}'::jsonb,
    '{"min_days": 100}'::jsonb,
    '{"min_days": 365}'::jsonb, 'github_api', true),

('pr_velocity', 'PR Velocity', 'Pull Requests merged per month', 'github', 'pr_merged', 'github_sync',
    '{"prs_per_month": 10}'::jsonb,
    '{"prs_per_month": 30}'::jsonb,
    '{"prs_per_month": 100}'::jsonb, 'github_api', true),

('code_volume', 'Code Volume', 'Lines of code contributed on GitHub', 'github', 'loc', 'github_sync',
    '{"loc": 10000}'::jsonb,
    '{"loc": 100000}'::jsonb,
    '{"loc": 1000000}'::jsonb, 'github_api', true),

('language_polyglot', 'Language Polyglot', 'Number of programming languages used in GitHub commits', 'github', 'languages', 'github_sync',
    '{"languages": 3}'::jsonb,
    '{"languages": 7}'::jsonb,
    '{"languages": 12}'::jsonb, 'github_api', true),

('repository_creator', 'Repository Creator', 'Number of GitHub repositories owned', 'github', 'repos_owned', 'github_sync',
    '{"repos": 5}'::jsonb,
    '{"repos": 20}'::jsonb,
    '{"repos": 50}'::jsonb, 'github_api', true),

('star_collector', 'Star Collector', 'Total GitHub stars on owned repositories', 'github', 'stars', 'github_sync',
    '{"stars": 100}'::jsonb,
    '{"stars": 1000}'::jsonb,
    '{"stars": 10000}'::jsonb, 'github_api', true),

('fork_magnet', 'Fork Magnet', 'Total forks on owned repositories', 'github', 'forks', 'github_sync',
    '{"forks": 50}'::jsonb,
    '{"forks": 500}'::jsonb,
    '{"forks": 5000}'::jsonb, 'github_api', true),

('issue_resolver', 'Issue Resolver', 'Number of GitHub issues closed', 'github', 'issues_closed', 'github_sync',
    '{"issues_closed": 50}'::jsonb,
    '{"issues_closed": 200}'::jsonb,
    '{"issues_closed": 1000}'::jsonb, 'github_api', true),

('early_bird', 'Early Bird', 'Consistent first commits in the early morning (all local times)', 'github', 'commit_time', 'github_sync',
    '{"hour_range": [6,8], "min_commits": 10}'::jsonb,
    '{"hour_range": [5,6], "min_commits": 25}'::jsonb,
    '{"hour_range": [4,5], "min_commits": 50}'::jsonb, 'github_api', true),

('night_owl', 'Night Owl', 'Consistent late-night commits', 'github', 'commit_time', 'github_sync',
    '{"hour_range": [22,24], "min_commits": 10}'::jsonb,
    '{"hour_range": [0,2], "min_commits": 25}'::jsonb,
    '{"hour_range": [2,4], "min_commits": 50}'::jsonb, 'github_api', true),

('weekend_warrior', 'Weekend Warrior', 'Percent of GitHub commits made on weekends', 'github', 'weekend_commit_pct', 'github_sync',
    '{"percent": 20}'::jsonb,
    '{"percent": 40}'::jsonb,
    '{"percent": 60}'::jsonb, 'github_api', true),

('sprint_champion', 'Sprint Champion', 'Most commits in a single week', 'github', 'weekly_commits', 'github_sync',
    '{"weekly_commits": 50}'::jsonb,
    '{"weekly_commits": 100}'::jsonb,
    '{"weekly_commits": 200}'::jsonb, 'github_api', true);

-- TEAM & COLLABORATION (5 badges)
INSERT INTO badge_definitions (badge_key, name, description, category, metric_type, calculation_type, bronze_threshold, silver_threshold, gold_threshold, data_source) VALUES
('cross_team_collaborator', 'Cross-Team Collaborator', 'Worked on projects spanning multiple teams', 'team', 'projects_across_teams', 'aggregate',
    '{"min_projects": 2}'::jsonb,
    '{"min_projects": 5}'::jsonb,
    '{"min_projects": 10}'::jsonb, 'project_metrics'),

('knowledge_sharer', 'Knowledge Sharer', 'Delivered tech talks or workshops for the team or company', 'team', 'tech_talks', 'aggregate',
    '{"min_talks": 3}'::jsonb,
    '{"min_talks": 10}'::jsonb,
    '{"min_talks": 25}'::jsonb, 'user_profile'),

('onboarding_champion', 'Onboarding Champion', 'Successfully onboarded new developers', 'team', 'onboarded_developers', 'aggregate',
    '{"min_onboarded": 3}'::jsonb,
    '{"min_onboarded": 10}'::jsonb,
    '{"min_onboarded": 25}'::jsonb, 'user_profile'),

('process_improver', 'Process Improver', 'Championed successful process or workflow optimizations', 'team', 'process_optimizations', 'aggregate',
    '{"min_optimizations": 1}'::jsonb,
    '{"min_optimizations": 3}'::jsonb,
    '{"min_optimizations": 10}'::jsonb, 'project_metrics'),

('culture_builder', 'Culture Builder', 'Led team-wide initiatives to improve work culture or morale', 'team', 'culture_initiatives', 'aggregate',
    '{"min_initiatives": 1}'::jsonb,
    '{"min_initiatives": 3}'::jsonb,
    '{"min_initiatives": 10}'::jsonb, 'user_profile');
