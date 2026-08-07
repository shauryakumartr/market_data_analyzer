"""Module for converting analytics metrics into structured business insights.
"""

import pandas as pd
import logging
from typing import Any

logger = logging.getLogger(__name__)

def generate_kpi_summary(basic_kpis: dict[str, float]) -> dict[str, Any]:
    """Format raw KPIs for display cards.
    """
    return {
        'Total Spend': basic_kpis.get('spend', 0.0),
        'Total Impressions': basic_kpis.get('impressions', 0.0),
        'Total Clicks': basic_kpis.get('clicks', 0.0),
        'Total Conversions': basic_kpis.get('conversions', 0.0),
        'Total Reach': basic_kpis.get('reach', 0.0),
        'Average CTR': round(basic_kpis.get('ctr', 0.0), 2),
        'Average CPC': round(basic_kpis.get('cpc', 0.0), 2),
        'Average CPM': round(basic_kpis.get('cpm', 0.0), 2),
        'Conversion Effectiveness': round(basic_kpis.get('conversion_rate', 0.0), 2),
    }

def generate_business_insights(analytics_data: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """Convert analytics into business observations across 9 dedicated categories.

    Returns dict containing:
    - kpi_insights
    - campaign_insights
    - audience_insights
    - device_insights
    - objective_insights
    - trend_insights
    - budget_insights
    - funnel_insights
    - overall_insights
    """
    logger.info("Generating business insights report")

    kpis = analytics_data.get('kpis', {})
    campaigns = analytics_data.get('campaigns', {})
    audience = analytics_data.get('audience', {})
    devices = analytics_data.get('devices', {})
    objectives = analytics_data.get('objectives', {})
    time_series = analytics_data.get('time', {})
    funnel = analytics_data.get('funnel', {})

    kpi_insights = []
    campaign_insights = []
    audience_insights = []
    device_insights = []
    objective_insights = []
    trend_insights = []
    budget_insights = []
    funnel_insights = []
    overall_insights = []

    # 1. KPI INSIGHTS
    avg_ctr = kpis.get('ctr', 0.0)
    avg_cpc = kpis.get('cpc', 0.0)
    avg_roas = kpis.get('roas', 0.0)
    avg_cvr = kpis.get('conversion_rate', 0.0)

    if avg_ctr > 1.5:
        kpi_insights.append({'metric': 'CTR', 'type': 'positive', 'observation': f"Account CTR ({avg_ctr:.2f}%) is healthy and above average benchmark, indicating strong ad headline interest."})
    else:
        kpi_insights.append({'metric': 'CTR', 'type': 'negative', 'observation': f"Account CTR ({avg_ctr:.2f}%) is below recommended benchmark, indicating potential ad creative fatigue."})

    if avg_roas >= 2.0:
        kpi_insights.append({'metric': 'ROAS', 'type': 'positive', 'observation': f"Account ROAS ({avg_roas:.2f}x) is strong, returning profitable revenue per rupee spent."})
    elif avg_roas > 0:
        kpi_insights.append({'metric': 'ROAS', 'type': 'negative', 'observation': f"Account ROAS ({avg_roas:.2f}x) is underperforming profitability thresholds."})

    # 2. CAMPAIGN INSIGHTS
    top_c = campaigns.get('top_campaigns', {})
    bottom_c = campaigns.get('bottom_campaigns', {})
    c_metrics = campaigns.get('campaign_metrics', {})
    efficiency = campaigns.get('efficiency', {})

    if top_c.get('highest_roas', {}).get('name'):
        h_roas_name = top_c['highest_roas']['name']
        h_roas_val = top_c['highest_roas']['value']
        campaign_insights.append({'type': 'Highest ROAS Campaign', 'observation': f"Campaign '{h_roas_name}' generated the highest ROAS at {h_roas_val:.2f}x."})

    if top_c.get('highest_ctr', {}).get('name'):
        h_ctr_name = top_c['highest_ctr']['name']
        h_ctr_val = top_c['highest_ctr']['value']
        campaign_insights.append({'type': 'Highest CTR Campaign', 'observation': f"Campaign '{h_ctr_name}' achieved strong engagement with a top CTR of {h_ctr_val:.2f}%."})

    for name, eff in efficiency.items():
        if eff.get('status') == 'Efficient':
            campaign_insights.append({'type': 'Budget Efficient Campaign', 'observation': f"Campaign '{name}' is highly efficient: produced {eff.get('conversion_share', 0):.1f}% of conversions with {eff.get('spend_share', 0):.1f}% of budget."})
        elif eff.get('status') == 'Inefficient':
            campaign_insights.append({'type': 'Budget Inefficient Campaign', 'observation': f"Campaign '{name}' is budget inefficient: consumed {eff.get('spend_share', 0):.1f}% of budget for only {eff.get('conversion_share', 0):.1f}% of conversions."})

    # 3. AUDIENCE INSIGHTS
    best_aud = audience.get('best_audience', {})
    worst_aud = audience.get('worst_audience', {})
    age_analysis = audience.get('age_analysis', {})
    gender_analysis = audience.get('gender_analysis', {})

    if best_aud.get('highest_roas_age'):
        audience_insights.append({'type': 'Most Valuable Age Group', 'observation': f"Age cohort '{best_aud['highest_roas_age']}' delivered the highest ROAS across demographic segments."})
    if best_aud.get('highest_cvr_age'):
        audience_insights.append({'type': 'Highest Intent Age Group', 'observation': f"Age cohort '{best_aud['highest_cvr_age']}' has the highest conversion intent rate."})
    if best_aud.get('highest_roas_gender'):
        audience_insights.append({'type': 'Most Valuable Gender', 'observation': f"Gender segment '{best_aud['highest_roas_gender']}' generated the highest return on ad spend."})

    # 4. DEVICE INSIGHTS
    dev_metrics = devices.get('device_metrics', {})
    best_dev = devices.get('best_device')
    if best_dev and best_dev in dev_metrics:
        device_insights.append({'type': 'Best Performing Device', 'observation': f"Device '{best_dev}' achieved the highest overall performance score."})
    if devices.get('most_cost_efficient_device'):
        device_insights.append({'type': 'Most Cost Efficient Device', 'observation': f"Device '{devices['most_cost_efficient_device']}' registered the lowest cost per click (CPC)."})

    # 5. OBJECTIVE INSIGHTS
    obj_metrics = objectives.get('objective_metrics', {})
    best_obj = objectives.get('best_overall_objective')
    if best_obj and best_obj in obj_metrics:
        objective_insights.append({'type': 'Best Objective', 'observation': f"Objective '{best_obj}' delivered the best overall conversion and return metrics."})
    if objectives.get('most_budget_allocation_objective'):
        objective_insights.append({'type': 'Most Budget Allocation Objective', 'observation': f"Objective '{objectives['most_budget_allocation_objective']}' received the largest portion of total campaign spend."})

    # 6. TREND INSIGHTS
    growth_rates = time_series.get('growth_rates', {})
    directions = time_series.get('trend_directions', {})
    if 'weekly' in directions:
        d = directions['weekly']
        trend_insights.append({'metric': 'Spend', 'direction': d.get('spend', 'flat'), 'observation': f"Weekly spend trend is {d.get('spend', 'flat')}."})
        trend_insights.append({'metric': 'CTR', 'direction': d.get('ctr', 'flat'), 'observation': f"Weekly CTR trend is {d.get('ctr', 'flat')}."})
        trend_insights.append({'metric': 'Conversions', 'direction': d.get('conversions', 'flat'), 'observation': f"Weekly conversions trend is {d.get('conversions', 'flat')}."})

    # 7. FUNNEL INSIGHTS
    if funnel.get('largest_drop_off_stage'):
        funnel_insights.append({'type': 'Weakest Stage', 'observation': f"Largest conversion drop-off occurred during the '{funnel['largest_drop_off_stage']}' transition."})
    if funnel.get('strongest_stage'):
        funnel_insights.append({'type': 'Strongest Stage', 'observation': f"Highest retention rate registered at the '{funnel['strongest_stage']}' stage."})

    # 8. BUDGET INSIGHTS
    concentrated_spend = any(m.get('spend_share', 0) > 40 for m in c_metrics.values())
    if concentrated_spend:
        budget_insights.append({'type': 'Budget Concentration', 'observation': "Budget is heavily concentrated in a small subset of active campaigns."})
    else:
        budget_insights.append({'type': 'Budget Distribution', 'observation': "Spend is evenly distributed across campaigns."})

    # 9. OVERALL INSIGHTS
    h_performers = campaigns.get('high_performers', [])
    l_performers = campaigns.get('low_performers', [])
    overall_insights.append({'type': 'Biggest Strength', 'observation': f"Identified {len(h_performers)} high-performing campaigns operating at top performance scores."})
    overall_insights.append({'type': 'Highest Risk', 'observation': f"Identified {len(l_performers)} underperforming campaigns consuming budget with below-average conversion efficiency."})

    return {
        'kpi_insights': kpi_insights,
        'campaign_insights': campaign_insights,
        'audience_insights': audience_insights,
        'device_insights': device_insights,
        'objective_insights': objective_insights,
        'trend_insights': trend_insights,
        'budget_insights': budget_insights,
        'funnel_insights': funnel_insights,
        'overall_insights': overall_insights
    }

# Legacy helper functions for app compatibility
def _extract_campaign_detail(df: pd.DataFrame, index: int) -> dict[str, Any]:
    row = df.loc[index]
    return {
        'Campaign Name': row.get('campaign_name', 'N/A'),
        'Date': str(row.get('date', 'N/A')),
        'CTR': round(row.get('ctr_pct', 0.0) * 100, 2) if pd.notna(row.get('ctr_pct')) else 0.0,
        'CTA': row.get('cta', 'N/A'),
        'Budget': f"₹ {row.get('budget_inr', 0.0)}",
        'Spend': f"₹ {row.get('spend_inr', 0.0)}",
        'Impressions': row.get('impressions', 0.0),
        'Clicks': row.get('clicks', 0.0),
        'Purchases': row.get('purchases', 0.0),
        'Conversions': row.get('conversions', 0.0),
    }

def generate_best_performers(
    df: pd.DataFrame,
    performance_comparison: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    best_performance = {}
    categories = ['Best CTR', 'Highest conversion campaign']
    for category in categories:
        idx = performance_comparison.get(category)
        if idx is not None and idx in df.index:
            row = df.loc[idx]
            best_performance[category] = {
                'Name': row.get('campaign_name', 'N/A'),
                'Date': str(row.get('date', 'N/A')),
                'CTR': row.get('ctr_pct', 0.0),
                'CTA': row.get('cta', 'N/A'),
                'Budget': row.get('budget_inr', 0.0),
                'Spend': row.get('spend_inr', 0.0),
                'Impressions': row.get('impressions', 0.0),
                'Clicks': row.get('clicks', 0.0),
                'Purchases': row.get('purchases', 0.0),
                'Conversions': row.get('conversions', 0.0),
            }
    return best_performance

def _extract_performers(df: pd.DataFrame, indexes: pd.Index) -> dict[int, dict[str, Any]]:
    performers = {}
    for idx in indexes:
        if idx in df.index:
            performers[int(idx)] = _extract_campaign_detail(df, idx)
    return performers

def generate_performer_insights(
    df: pd.DataFrame,
    performance_comparison: dict[str, Any],
) -> tuple[dict, dict, dict]:
    under = _extract_performers(df, performance_comparison.get('Low performing campaigns', pd.Index([])))
    high = _extract_performers(df, performance_comparison.get('High performing campaigns', pd.Index([])))
    low_ctr = _extract_performers(df, performance_comparison.get('Low CTR campaigns', pd.Index([])))
    return under, high, low_ctr

def generate_anomaly_insights(
    df: pd.DataFrame,
    anomalies: dict[str, pd.Index],
) -> dict[str, dict]:
    common_fields = ['campaign_name', 'objective', 'date', 'budget_inr', 'spend_inr']
    insights = {}
    for anomaly_type, indexes in anomalies.items():
        if len(indexes) > 0:
            fields = common_fields.copy()
            if anomaly_type == 'Missing impressions':
                fields.append('impressions')
            insights[anomaly_type] = {}
            for idx in indexes:
                if idx in df.index:
                    row = df.loc[idx]
                    detail = {}
                    for field in fields:
                        val = row.get(field, 'N/A')
                        if field in ('budget_inr', 'spend_inr'):
                            detail[field.replace('_', ' ').title()] = f"₹ {val}" if val != 'N/A' else val
                        else:
                            detail[field.replace('_', ' ').title()] = str(val) if field == 'date' else val
                    insights[anomaly_type][int(idx)] = detail
        else:
            insights[anomaly_type] = {}
    return insights
