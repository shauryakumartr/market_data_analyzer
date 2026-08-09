"""Module for generating prioritized deterministic recommendations.

Translates market analysis observations into actionable business recommendations categorized into four priority tiers:
Critical (immediate budget protection), High (underperforming campaign reduction), Medium (scaling top performers), and Low (ad fatigue / monitoring).
"""

import pandas as pd
import logging
from typing import Dict, Any, List, Optional

# Module-level logger for recommendation engine operations
logger: logging.Logger = logging.getLogger(__name__)

MAX_RECOMMENDATIONS: int = 10


def generate_recommendations(
    df: pd.DataFrame,
    performance_comparison: Dict[str, Any],
    segmented_analysis: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    """Legacy recommendations interface for app compatibility.

    Parameters
    ----------
    df : pd.DataFrame
        Campaign DataFrame.
    performance_comparison : Dict[str, Any]
        Performance comparison index mappings.
    segmented_analysis : Dict[str, pd.DataFrame]
        Segment breakdown DataFrames.

    Returns
    -------
    Dict[str, Any]
        Structured recommendation dictionary.
    """
    logger.info("Generating marketing recommendations using legacy interface")
    recommendations: Dict[str, Any] = {}

    campaign_categories: Dict[str, str] = {
        'Budget Reallocation': 'High performing campaigns',
        'Reduce Spend': 'Low performing campaigns',
        'Creative Optimization': 'Low CTR campaigns',
        'Landing Page Optimization': 'Low Landing page conversion campaign',
    }
    for rec_name, perf_key in campaign_categories.items():
        indexes: pd.Index = performance_comparison.get(perf_key, pd.Index([]))
        recommendations[rec_name] = _extract_campaign_recommendation(df, indexes)

    segment_mapping: Dict[str, str] = {
        'Gender': 'gender_segment',
        'Age': 'age_segment',
        'Device': 'device_segment',
        'Campaign': 'objective_segment',
    }
    for rec_name, segment_key in segment_mapping.items():
        segment_df: pd.DataFrame = segmented_analysis.get(segment_key, pd.DataFrame())
        recommendations[rec_name] = _get_top_segment(segment_df)

    return recommendations


def _extract_campaign_recommendation(
    df: pd.DataFrame,
    indexes: pd.Index,
    max_count: int = MAX_RECOMMENDATIONS,
) -> Dict[int, Dict[str, Any]]:
    """Helper function to extract campaign details for index list.

    Parameters
    ----------
    df : pd.DataFrame
        Campaign DataFrame.
    indexes : pd.Index
        List of target DataFrame indexes.
    max_count : int, default=10
        Maximum recommendations count limit.

    Returns
    -------
    Dict[int, Dict[str, Any]]
        Extracted campaign details dictionary keyed by index.
    """
    result: Dict[int, Dict[str, Any]] = {}
    for i, idx in enumerate(indexes):
        if i >= max_count:
            break
        if idx in df.index:
            row: pd.Series = df.loc[idx]
            result[int(idx)] = {
                'Name': str(row.get('campaign_name', 'N/A')),
                'Objective': str(row.get('objective', 'N/A')),
                'Date': str(row.get('date', 'N/A')),
                'Budget': float(row.get('budget_inr', 0.0)),
                'Spend': float(row.get('spend_inr', 0.0)),
                'CTR': round(float(row.get('ctr_pct', 0.0)) * 100.0, 4) if pd.notna(row.get('ctr_pct')) else 0.0,
                'Conversion Rate': round(float(row.get('conversion_rate_pct', 0.0)) * 100.0, 4) if pd.notna(row.get('conversion_rate_pct')) else 0.0,
            }
    return result


def _get_top_segment(
    segment_df: pd.DataFrame,
    sort_column: str = 'Segment CTR',
) -> Dict[str, Any]:
    """Helper to extract top segment metric summary.

    Parameters
    ----------
    segment_df : pd.DataFrame
        Segment analysis DataFrame.
    sort_column : str, default='Segment CTR'
        Sorting column name.

    Returns
    -------
    Dict[str, Any]
        Top segment summary.
    """
    if segment_df.empty:
        return {}
    top: pd.DataFrame = segment_df.sort_values(by=sort_column, ascending=False).head(1)
    if top.empty:
        return {}
    index: Any = top.index[0]
    return {
        'Name': str(index),
        'Segment CTR': float(top.loc[index, 'Segment CTR']) if 'Segment CTR' in top.columns else 0.0,
        'Total Impressions': float(top.loc[index, 'Total Impressions']) if 'Total Impressions' in top.columns else 0.0,
        'Total Clicks': float(top.loc[index, 'Total Clicks']) if 'Total Clicks' in top.columns else 0.0,
        'Segment CPC': float(top.loc[index, 'Segment CPC']) if 'Segment CPC' in top.columns else 0.0,
        'Total Spend': float(top.loc[index, 'Total Spend']) if 'Total Spend' in top.columns else 0.0,
    }


def generate_action_recommendations(
    insights: Any,
    anomalies: Dict[str, Any],
    analytics: Dict[str, Any]
) -> Dict[str, List[Dict[str, str]]]:
    """Generate prioritized business recommendations organized into Critical, High, Medium, and Low priority tiers.

    Parameters
    ----------
    insights : Any
        Structured insights report.
    anomalies : Dict[str, Any]
        Detected anomalies report.
    analytics : Dict[str, Any]
        Full raw analytics report dictionary.

    Returns
    -------
    Dict[str, List[Dict[str, str]]]
        Prioritized recommendations dictionary containing lists for critical, high, medium, and low.
    """
    logger.info("Executing prioritized recommendation engine across analytics outputs")
    critical_recs: List[Dict[str, str]] = []
    high_recs: List[Dict[str, str]] = []
    medium_recs: List[Dict[str, str]] = []
    low_recs: List[Dict[str, str]] = []

    # 1. CRITICAL PRIORITY: Revenue loss, budget waste, ROAS collapse, zero conversions on spend
    critical_anomalies: List[Dict[str, Any]] = anomalies.get('critical', [])
    for a in critical_anomalies:
        issue: str = str(a.get('issue', ''))
        name: str = str(a.get('campaign_name', 'Campaign'))
        if 'zero conversion' in issue.lower() or 'high spend' in issue.lower():
            critical_recs.append({
                'category': 'Campaign Delivery',
                'title': f"Pause '{name}' Immediately",
                'reason': f"Campaign is spending significantly without yielding conversions: {a.get('details', '')}",
                'action': f"Pause campaign '{name}' immediately to stop budget leakage and inspect landing page tracking."
            })
        elif 'roas collapse' in issue.lower():
            critical_recs.append({
                'category': 'ROAS Collapse',
                'title': f"Review Return Drop on '{name}'",
                'reason': str(a.get('details', '')),
                'action': f"Audit bidding strategy and audience targeting parameters for '{name}'."
            })
        elif 'budget' in issue.lower():
            critical_recs.append({
                'category': 'Budget Waste',
                'title': f"Cap Daily Spend on '{name}'",
                'reason': str(a.get('details', '')),
                'action': f"Set hard daily caps on ad account for '{name}' to enforce target limits."
            })

    # 2. HIGH PRIORITY: Poor efficiency, low CTR, low conversion rate on high spend
    campaigns: Dict[str, Any] = analytics.get('campaigns', {})
    efficiency: Dict[str, Any] = campaigns.get('efficiency', {})
    c_metrics: Dict[str, Any] = campaigns.get('campaign_metrics', {})
    low_performers: List[str] = campaigns.get('low_performers', [])

    for name in low_performers:
        if name in c_metrics:
            m: Dict[str, Any] = c_metrics[name]
            high_recs.append({
                'category': 'Underperforming Campaign',
                'title': f"Reduce Budget on '{name}'",
                'reason': f"Campaign is classified as low-performing with a performance score of {m.get('performance_score', 0.0):.1f}/100.",
                'action': f"Reduce budget for '{name}' by 20-30% and test new ad creative variations."
            })

    for name, eff in efficiency.items():
        if eff.get('status') == 'Inefficient' and name not in [r['title'] for r in high_recs]:
            high_recs.append({
                'category': 'Budget Inefficiency',
                'title': f"Re-evaluate Allocation for '{name}'",
                'reason': f"Consumed {eff.get('spend_share', 0.0):.1f}% budget but produced only {eff.get('conversion_share', 0.0):.1f}% conversions.",
                'action': f"Reallocate budget from '{name}' towards high-efficiency campaigns."
            })

    # 3. MEDIUM PRIORITY: Optimization opportunities, scaling high performers, device/audience shifts
    high_performers: List[str] = campaigns.get('high_performers', [])
    for name in high_performers:
        if name in c_metrics:
            m = c_metrics[name]
            medium_recs.append({
                'category': 'Scaling Opportunity',
                'title': f"Scale High Performer '{name}'",
                'reason': f"Campaign is performing in top tier with performance score {m.get('performance_score', 0.0):.1f}/100.",
                'action': f"Increase budget allocation for '{name}' by 15-25%."
            })

    audience: Dict[str, Any] = analytics.get('audience', {})
    best_aud: Dict[str, Any] = audience.get('best_audience', {})
    if best_aud.get('highest_roas_age'):
        medium_recs.append({
            'category': 'Demographic Optimization',
            'title': f"Increase Budget for Age Group '{best_aud['highest_roas_age']}'",
            'reason': "This age demographic generates the highest ROAS across campaign cohorts.",
            'action': f"Increase bid modifiers for the {best_aud['highest_roas_age']} age group."
        })

    devices: Dict[str, Any] = analytics.get('devices', {})
    if devices.get('best_device'):
        medium_recs.append({
            'category': 'Device Allocation',
            'title': f"Prioritize Budget for Device '{devices['best_device']}'",
            'reason': f"Device '{devices['best_device']}' delivers top conversion efficiency.",
            'action': f"Shift 10-15% of ad budget to targeting {devices['best_device']} users."
        })

    # 4. LOW PRIORITY: Monitoring suggestions, frequency checks, stable performance
    for a in anomalies.get('minor', []):
        issue = str(a.get('issue', ''))
        name = str(a.get('campaign_name', 'Campaign'))
        if 'frequency' in issue.lower():
            low_recs.append({
                'category': 'Ad Fatigue',
                'title': f"Refresh Creatives on '{name}'",
                'reason': str(a.get('details', '')),
                'action': "Rotate new image/video assets to reduce user ad fatigue."
            })
        elif 'landing page' in issue.lower() or 'ctr' in issue.lower():
            low_recs.append({
                'category': 'Landing Page Review',
                'title': f"Optimize Page Experience for '{name}'",
                'reason': str(a.get('details', '')),
                'action': "Audit landing page hero section and CTA visibility."
            })

    if not critical_recs and not high_recs and not medium_recs and not low_recs:
        low_recs.append({
            'category': 'Routine Monitoring',
            'title': 'Maintain Current Campaign Settings',
            'reason': 'Campaign metrics are performing stably within expected ranges.',
            'action': 'Continue monitoring weekly trend metrics.'
        })

    logger.info("Prioritized recommendation engine completed successfully")

    return {
        'critical': critical_recs,
        'high': high_recs,
        'medium': medium_recs,
        'low': low_recs
    }
