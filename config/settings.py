"""Central settings and configuration values for the marketing analytics platform.

Contains column sets, aliases for mapping, and configuration defaults.
"""

from typing import Set, Dict, List, Optional

MANDATORY_COLUMNS: Set[str] = {
    'date',
    'budget_inr',
    'spend_inr',
    'impressions',
    'reach',
    'clicks',
    'conversions',
}

OPTIONAL_COLUMNS: Set[str] = {
    'platform',
    'campaign_name',
    'ad_set_name',
    'objective',
    'result_type',
    'region',
    'age_group',
    'gender',
    'device',
    'creative_format',
    'cta',
    'add_to_cart',
    'purchases',
}

DERIVED_COLUMNS: Set[str] = {
    'ctr_pct',
    'cpc_inr',
    'conversion_rate_pct',
    'cost_per_conversion_inr',
    'roas',
}

COLUMN_ALIASES: Dict[str, List[str]] = {
    "date": ["date", "day", "report_date", "reporting_date", "timestamp", "dt"],
    "platform": ["platform", "source", "medium", "publisher_platform", "channel", "network"],
    "campaign_name": ["campaign_name", "campaign", "campaign_title", "utm_campaign", "cid"],
    "ad_set_name": ["ad_set_name", "ad_set", "adgroup", "ad_group_name", "ad_group", "targeting_group"],
    "objective": ["objective", "campaign_objective", "goal", "marketing_objective", "optimization_goal"],
    "result_type": ["result_type", "results_type", "outcome_type", "conversion_type", "goal_type"],
    "region": ["region", "state", "location", "geo", "country", "province"],
    "age_group": ["age_group", "age_range", "age", "demographic_age"],
    "gender": ["gender", "sex", "demographic_gender"],
    "device": ["device", "device_type", "platform_device", "impression_device", "hardware"],
    "creative_format": ["creative_format", "ad_format", "format", "creative_type", "ad_type", "placement_type"],
    "cta": ["cta", "call_to_action", "button_text", "cta_text"],
    "budget_inr": ["budget", "campaign_budget", "daily_budget", "total_budget", "budget_amount", "budget_inr"],
    "spend_inr": ["spend", "amount_spent", "ad_spend", "cost", "total_cost", "investment", "spend_inr"],
    "impressions": ["impressions", "impr", "views", "total_impressions"],
    "reach": ["reach", "unique_reach", "unique_users", "reach_count"],
    "frequency": ["frequency", "avg_frequency", "frequency_score", "repetition"],
    "clicks": ["clicks", "link_clicks", "all_clicks", "clicks_total"],
    "ctr_pct": ["ctr_pct", "ctr", "click_through_rate", "click_thru_rate", "ctr_percent"],
    "cpc_inr": ["cpc_inr", "cpc", "cost_per_click", "avg_cpc", "cpc_amount"],
    "landing_page_views": ["landing_page_views", "lp_views", "sessions", "page_views", "visits", "website_visits"],
    "add_to_cart": ["add_to_cart", "cart_adds", "atc", "adds_to_cart", "cart_actions"],
    "purchases": ["purchases", "purchase", "orders", "transactions", "checkout_completed"],
    "conversions": ["conversions", "conv", "total_conversions", "goals_completed", "actions"],
    "conversion_rate_pct": ["conversion_rate_pct", "conversion_rate", "cvr", "conv_rate", "cvr_pct"],
    "cost_per_conversion_inr": ["cost_per_conversion_inr", "cost_per_conv", "cpa", "cac", "cost_per_action", "cost_per_lead"],
    "roas": ["roas", "return_on_ad_spend", "purchase_roas", "purchase_revenue_roas"],
    "primary_text": ["primary text","primary text (body)","body","ad text","text","primary copy","ad creative text","caption","copy","post text","main text"],
    "headline": ["headline","ad headline","ad title","title","headline 1","link headline","link text"],
    "ad_description": ["description","ad description","link description","link text description","subheadline","sub-headline","caption snippet"],
    "creative_format": ["creative format","ad format","format","placement","ad placement","creative placement"],
    "creative_type": ["creative type","ad type","content type","asset type","media type","creative asset type"],
    "language": ["language","ad language","creative language","content language","language code","locale"]
}

NUMERIC_COLUMNS: List[str] = [
    'budget_inr',
    'spend_inr',
    'impressions',
    'reach',
    'clicks',
    'conversions',
    'frequency',
    'landing_page_views',
    'add_to_cart',
    'purchases',
]

PERCENTAGE_COLUMNS: List[str] = [
    'ctr_pct',
    'conversion_rate_pct',
]

SEGMENT_COLUMNS: List[str] = [
    'age_group',
    'gender',
    'device',
    'objective',
]

MAPPING_DROPDOWN_OPTIONS: List[Optional[str]] = [
    None,
    "date",
    "platform",
    "campaign_name",
    "ad_set_name",
    "objective",
    "result_type",
    "region",
    "age_group",
    "gender",
    "device",
    "creative_format",
    "cta",
    "budget_inr",
    "spend_inr",
    "impressions",
    "reach",
    "frequency",
    "clicks",
    "ctr_pct",
    "cpc_inr",
    "landing_page_views",
    "add_to_cart",
    "purchases",
    "conversions",
    "conversion_rate_pct",
    "cost_per_conversion_inr",
    "roas",
    "Ignore Column",
    "Custom Column"

]


##QUALITATIVE ANALYSIS

MANDATORY_QUALITATIVE_COLUMNS: Set[str]={"primary_text"}


OPTIONAL_QUALITATIVE_COLUMNS: Set[str] = {
    "headline",
    "ad_description",
    "creative_format", 
    "creative_type"  }


QUALITATIVE_MAPPING_DROPDOWN_OPTIONS: List[Optional[str]] = [

    None,
    "primary_text",
    "headline",
    "ad_description",
    "creative_format", 
    "creative_type",
    "Ignore Column",
    "Custom Column"
]

