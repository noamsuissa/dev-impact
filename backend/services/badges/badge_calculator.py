"""
Badge Calculator - Core logic for evaluating and awarding badges
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from supabase import Client
from backend.schemas.badge import (
    BadgeDefinition,
    UserBadge,
    UserBadge,
    UserBadgeWithDetails,
)
import json
from backend.llm.litellm_provider import LiteLLMProvider

class BadgeCalculator:
    """
    Calculates badges for a user based on their project metrics.
    
    This class handles:
    1. Fetching user metrics and badge definitions
    2. Evaluating metrics against badge thresholds
    3. Determining achieved tiers (bronze, silver, gold)
    4. detecting upgrades from previous tiers
    """

    @staticmethod
    def calculate_badges_for_user(
        client: Client, 
        user_id: str, 
        project_ids: Optional[List[str]] = None
    ) -> List[UserBadgeWithDetails]:
        """
        Calculate all applicable badges for a user.
        """
        # 1. Fetch all active badge definitions
        badge_defs = BadgeCalculator._fetch_badge_definitions(client)
        single_project_badges = [b for b in badge_defs if b.calculation_type == 'single_project']
        aggregate_badges = [b for b in badge_defs if b.calculation_type == 'aggregate']
        
        # 2. Fetch user's project metrics
        metrics = BadgeCalculator._fetch_user_metrics(client, user_id, project_ids)
        
        if not metrics:
            return []
            
        # 3. Fetch user subscription type
        subscription_type = BadgeCalculator._fetch_user_subscription(client, user_id)
        
        # 4. Initialize LLM Provider
        llm_provider = LiteLLMProvider()

        earned_badges: List[UserBadgeWithDetails] = []

        # 5. Evaluate Single Project Badges (BATCHED per Project)
        # Group metrics by project
        project_metrics_map: Dict[str, List[Dict[str, Any]]] = {}
        for m in metrics:
            pid = m.get('project_id') or m.get('project', {}).get('id')
            if pid:
                if pid not in project_metrics_map:
                    project_metrics_map[pid] = []
                project_metrics_map[pid].append(m)

        for pid, p_metrics in project_metrics_map.items():
            # Identify metric types present in this project
            p_metric_types = set()
            for m in p_metrics:
                if m.get('metric_type'):
                    p_metric_types.add(m.get('metric_type'))

            # Filter relevant badges
            relevant_badges = [b for b in single_project_badges if b.metric_type in p_metric_types]
            
            if relevant_badges:
                batch_results = BadgeCalculator._evaluate_project_batch_with_llm(
                    p_metrics, relevant_badges, subscription_type, llm_provider
                )
                earned_badges.extend(batch_results)

        # 6. Evaluate Aggregate Badges (Iterative or separate logic)
        for badge in aggregate_badges:
            result = BadgeCalculator._evaluate_aggregate(badge, metrics, subscription_type, llm_provider)
            if result:
                earned_badges.append(result)
                
        return earned_badges

    @staticmethod
    def _fetch_badge_definitions(client: Client) -> List[BadgeDefinition]:
        """Fetch all active badge definitions."""
        response = client.table("badge_definitions")\
            .select("*")\
            .eq("is_active", True)\
            .execute()
        return [BadgeDefinition(**b) for b in response.data]

    @staticmethod
    def _fetch_user_subscription(client: Client, user_id: str) -> str:
        """Fetch user subscription type (free or pro)."""
        try:
            response = client.table("profiles")\
                .select("subscription_type")\
                .eq("id", user_id)\
                .single()\
                .execute()
            return response.data.get("subscription_type", "free")
        except Exception:
            return "free"

    @staticmethod
    def _fetch_user_metrics(client: Client, user_id: str, project_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fetch project metrics for the user.
        """
        query = client.table("project_metrics")\
            .select("*, project:impact_projects!inner(*)")\
            .eq("project.user_id", user_id)
            
        if project_ids:
            query = query.in_("project_id", project_ids)
            
        response = query.execute()
        return response.data

    @staticmethod
    def _evaluate_project_batch_with_llm(
        metrics: List[Dict[str, Any]],
        badges: List[BadgeDefinition],
        subscription_type: str,
        llm_provider: LiteLLMProvider
    ) -> List[UserBadgeWithDetails]:
        """
        Evaluate a batch of badges for a single project using one LLM call.
        """
        if not badges or not metrics:
            return []

        # Prepare context data
        # Compact metrics representation
        metrics_summary = []
        for m in metrics:
            metrics_summary.append({
                "type": m.get("metric_type") or m.get("type"),
                "data": m.get("metric_data"),
                "legacy_value": m.get("primary_value")
            })

        # Project details (extracted from the first metric as they are all for the same project)
        project_context = {}
        if metrics:
            raw_project = metrics[0].get("project", {})
            # Select relevant fields for context
            project_context = {
                "name": raw_project.get("project_name"),
                "company": raw_project.get("company"),
                "role": raw_project.get("role"),
                "description": raw_project.get("problem"), # map problem to description
                "tech_stack": raw_project.get("tech_stack"),
                "team_size": raw_project.get("team_size")
            }

        # Compact badges representation
        badges_context = []
        badge_map = {b.badge_key: b for b in badges}
        
        for b in badges:
            badges_context.append({
                "key": b.badge_key,
                "name": b.name,
                "description": b.description,
                "thresholds": {
                    "bronze": b.bronze_threshold,
                    "silver": b.silver_threshold,
                    "gold": b.gold_threshold
                }
            })

        prompt = f"""
You are an expert badge awarder system. 
Analyze the Project Context and Project Metrics against the list of Available Badges.
Identify ALL badges that have been earned based on the thresholds.
If a badge is not earned, do not include it in the response.
Look for the before and after values of the metric in the metric data to determine the multiplier or improvement.

PROJECT CONTEXT:
{json.dumps(project_context, indent=2)}

PROJECT METRICS:
{json.dumps(metrics_summary, indent=2)}

AVAILABLE BADGES & THRESHOLDS:
{json.dumps(badges_context, indent=2)}

INSTRUCTIONS:
1. For EACH badge, check if the metrics meet the criteria for Bronze, Silver, or Gold.
2. Determine the HIGHEST tier fully met.
3. BE STRICT. Do not award badges if thresholds are not met.
4. METRIC CALCULATION RULES:
   - Calculate improvement = (Value Before / Value After) or (Value After / Value Before) depending on direction.
   - 10 minutes to 2 minutes is a 5x improvement (10/2 = 5).
   - "5x" IS LESS THAN "10x". It does NOT meet a 10x threshold.
   - "1x" primary value means NO CHANGE.
   - Do NOT argue that a project "achieved exponential improvement" if the numbers don't show it.
   - If Bronze threshold is 10x and actual is 5x, the badge is NOT earned.
5. PRIORITIZE METRIC BEFORE AND AFTER VALUES OVER PRIMARY VALUE. Primary values can be rounded up or down, therefore you should only look at the before and after values when making a decision. Primary values are only there for context.
6. If a badge is NOT earned, DO NOT include it in the response.
7. Format:
{{
  "earned_badges": [
    {{
      "key": "badge_key",
      "tier": "bronze" | "silver" | "gold",
      "reason": "Detailed explanation for why the badge was earned."
    }}
  ]
}}
If no badges are earned, return {{"earned_badges": []}}.
8. Return JSON object.
9. Provide a detailed explanation for each badge earned.

"""

        try:
            response = llm_provider.generate_completion_sync(
                provider="groq",
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.get("content", "{}")
            result_json = json.loads(content)
            earned_list = result_json.get("earned_badges", [])
            
            results = []
            for item in earned_list:
                key = item.get("key")
                raw_tier = item.get("tier", "").lower()
                reason = item.get("reason")
                
                if key not in badge_map or raw_tier not in ["bronze", "silver", "gold"]:
                    continue
                    
                badge_def = badge_map[key]
                
                # Tier Logic
                final_tier = raw_tier
                eligible_tier = None
                
                if subscription_type == "free":
                    if raw_tier in ["silver", "gold"]:
                        final_tier = "bronze"
                        eligible_tier = raw_tier
                
                extra_data = {"llm_reason": reason}
                if eligible_tier:
                    extra_data["eligible_tier"] = eligible_tier
                    
                # Use the first metric's project ID (since this is a single project batch)
                project_id = metrics[0].get("project_id") or metrics[0].get("project", {}).get("id")

                result_obj = BadgeCalculator._construct_badge_result(
                    badge_def, final_tier, 0.0, project_id, extra_data
                )
                results.append(result_obj)
                
            return results

        except Exception as e:
            print(f"Batch Badge Evaluation Failed: {e}")
            return []

    @staticmethod
    def _evaluate_aggregate(
        badge: BadgeDefinition, 
        metrics: List[Dict[str, Any]],
        subscription_type: str,
        llm_provider: LiteLLMProvider
    ) -> Optional[UserBadgeWithDetails]:
        """
        Evaluate badges that aggregate data across all projects.
        """
        # Collect relevant metrics
        relevant_metrics = []
        for m in metrics:
            if badge.metric_type and m.get("metric_type") == badge.metric_type:
                 relevant_metrics.append(m)
            elif m.get("type") == badge.metric_type:
                 relevant_metrics.append(m)
        
        if not relevant_metrics:
            return None

        thresholds = {
            "bronze": badge.bronze_threshold,
            "silver": badge.silver_threshold,
            "gold": badge.gold_threshold
        }
        
        # Prepare metrics with context for aggregation
        metrics_with_context = []
        for m in relevant_metrics:
            raw_project = m.get("project", {})
            metrics_with_context.append({
                "project_name": raw_project.get("project_name"),
                "project_context": {
                    "company": raw_project.get("company"),
                    "description": raw_project.get("problem"),
                    "tech_stack": raw_project.get("tech_stack"),
                },
                "metric_data": m.get("metric_data") or {"val": m.get("primary_value")},
                "legacy_value": m.get("primary_value")
            })
        
        prompt = f"""
You are an expert badge awarder system.
Determine if the user has earned the AGGREGATE badge '{badge.name}'.
You must aggregate the values from the provided metric entries across projects as implied by the badge description and thresholds.
Pay close attention to requirements like "across X projects" or "total value".
BE STRICT. Do not award if criteria are not clearly met.

BADGE: {badge.name}
DESC: {badge.description}
THRESHOLDS: {json.dumps(thresholds, indent=2)}

CONTRIBUTING METRICS (Grouped by Project):
{json.dumps(metrics_with_context, indent=2)}

INSTRUCTIONS:
1. Verify if the metrics meet the criteria (e.g. count distinct projects if required, or sum values).
2. If earned, determine the HIGHEST tier fully met.
3. Return JSON: {{ "earned": bool, "tier": "bronze"|"silver"|"gold", "reason": "detailed explanation" }}
"""
        try:
             response = llm_provider.generate_completion_sync(
                provider="groq",
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                response_format={"type": "json_object"}
            )
             content = response.get("content", "{}")
             res = json.loads(content)
             
             if res.get("earned"):
                 raw_tier = res.get("tier", "").lower()
                 if raw_tier in ["bronze", "silver", "gold"]:
                     
                     final_tier = raw_tier
                     eligible_tier = None
                     if subscription_type == "free" and raw_tier != "bronze":
                         final_tier = "bronze"
                         eligible_tier = raw_tier
                         
                     extra_data = {"llm_reason": res.get("reason")}
                     if eligible_tier: extra_data["eligible_tier"] = eligible_tier
                     
                     return BadgeCalculator._construct_badge_result(
                         badge, final_tier, 0.0, None, extra_data
                     )
        except Exception:
            pass
            
        return None

    @staticmethod
    def _construct_badge_result(
        badge: BadgeDefinition, 
        tier: str, 
        value: float, 
        project_id: Optional[str], 
        extra_data: Any
    ) -> UserBadgeWithDetails:
        """Helper to construct the response object."""
        return UserBadgeWithDetails(
            id="pending", 
            user_id="pending",
            badge_id=badge.id,
            badge_key=badge.badge_key,
            name=badge.name,
            description=badge.description,
            category=badge.category,
            icon_name=badge.icon_name,
            color_scheme=badge.color_scheme,
            tier=tier, # type: ignore
            achievement_value=value,
            achievement_data=extra_data,
            source_project_ids=[project_id] if project_id else None,
            earned_at=datetime.utcnow().isoformat(),
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            is_public=True,
            is_featured=False
        )
