"""Module for converting analytics metrics into structured business insights.

Translates quantitative analytics measurements into factual observations across 9 dedicated categories:
KPIs, Campaigns, Audience, Devices, Objectives, Trends, Budget, Funnel, and Overall Summary.
Provides helper extractors for best performers, campaign performer details, and anomaly insights.
"""

import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Tuple

# Module-level logger for business insight generation
logger: logging.Logger = logging.getLogger(__name__)


def generate_kpi_summary(basic_kpis: Dict[str, float]) -> Dict[str, Any]:
    """Format raw KPIs for display metrics cards.

    Parameters
    ----------
    basic_kpis : Dict[str, float]
        Raw account-level KPIs dictionary.

    Returns
    -------
    Dict[str, Any]
        Display-ready metric card dictionary.
    """
    return {
        'Total Spend': basic_kpis.get('spend', 0.0),
        'Total Impressions': basic_kpis.get('impressions', 0.0),
        'Total Clicks': basic_kpis.get('clicks', 0.0),
        'Total Conversions': basic_kpis.get('conversions', 0.0),
        'Total Reach': basic_kpis.get('reach', 0.0),
        'Average CTR': round(float(basic_kpis.get('ctr', 0.0)), 2),
        'Average CPC': round(float(basic_kpis.get('cpc', 0.0)), 2),
        'Average CPM': round(float(basic_kpis.get('cpm', 0.0)), 2),
        'Conversion Effectiveness': round(float(basic_kpis.get('conversion_rate', 0.0)), 2),
    }


def generate_business_insights(analytics_data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """Convert analytics measurements into factual observations across 9 dedicated categories.

    Parameters
    ----------
    analytics_data : Dict[str, Any]
        Combined raw analytics dictionary.

    Returns
    -------
    Dict[str, List[Dict[str, str]]]
        Structured insights report containing 9 observation lists.
    """
    logger.info("Generating factual business insights across analytics dimensions")

    kpis: Dict[str, float] = analytics_data.get('kpis', {})
    campaigns: Dict[str, Any] = analytics_data.get('campaigns', {})
    audience: Dict[str, Any] = analytics_data.get('audience', {})
    devices: Dict[str, Any] = analytics_data.get('devices', {})
    objectives: Dict[str, Any] = analytics_data.get('objectives', {})
    time_series: Dict[str, Any] = analytics_data.get('time', {})
    funnel: Dict[str, Any] = analytics_data.get('funnel', {})

    kpi_insights: List[Dict[str, str]] = []
    campaign_insights: List[Dict[str, str]] = []
    audience_insights: List[Dict[str, str]] = []
    device_insights: List[Dict[str, str]] = []
    objective_insights: List[Dict[str, str]] = []
    trend_insights: List[Dict[str, str]] = []
    budget_insights: List[Dict[str, str]] = []
    funnel_insights: List[Dict[str, str]] = []
    overall_insights: List[Dict[str, str]] = []

    # 1. KPI INSIGHTS
    avg_ctr: float = float(kpis.get('ctr', 0.0))
    avg_cpc: float = float(kpis.get('cpc', 0.0))
    avg_cvr: float = float(kpis.get('conversion_rate', 0.0))
    roas: float = float(kpis.get('roas', 0.0))

    if avg_ctr > 2.0:
        kpi_insights.append({'type': 'positive', 'title': 'Strong Account CTR', 'message': f"Account Click-Through Rate is performing strongly at {avg_ctr:.2f}%."})
    else:
        kpi_insights.append({'type': 'warning', 'title': 'Subdued Account CTR', 'message': f"Account Click-Through Rate is currently at {avg_ctr:.2f}%."})

    if avg_cvr > 3.0:
        kpi_insights.append({'type': 'positive', 'title': 'High Conversion Efficiency', 'message': f"Account conversion rate is robust at {avg_cvr:.2f}%."})
    else:
        kpi_insights.append({'type': 'info', 'title': 'Conversion Rate Baseline', 'message': f"Account conversion rate sits at {avg_cvr:.2f}%."})

    # 2. CAMPAIGN INSIGHTS
    high_perf: List[str] = campaigns.get('high_performers', [])
    low_perf: List[str] = campaigns.get('low_performers', [])
    top_c: Dict[str, Any] = campaigns.get('top_campaigns', {})

    if high_perf:
        campaign_insights.append({'type': 'positive', 'title': 'High Performing Campaigns Identified', 'message': f"{len(high_perf)} campaign(s) classified as High Performers based on majority performance criteria."})
    if low_perf:
        campaign_insights.append({'type': 'warning', 'title': 'Underperforming Campaigns Detected', 'message': f"{len(low_perf)} campaign(s) exhibiting below-average efficiency metrics across CTR, CVR, and CPC."})
    if top_c.get('highest_spend', {}).get('name'):
        h_spend_name: Any = top_c['highest_spend']['name']
        h_spend_val: float = float(top_c['highest_spend']['value'])
        campaign_insights.append({'type': 'info', 'title': 'Top Budget Consumer', 'message': f"Campaign '{h_spend_name}' accounts for the highest total spend at ₹{h_spend_val:,.2f}."})

    # 3. AUDIENCE INSIGHTS
    best_aud: Dict[str, Any] = audience.get('best_audience', {})
    if best_aud.get('highest_cvr_age'):
        audience_insights.append({'type': 'positive', 'title': 'Optimal Age Demographic', 'message': f"Age group '{best_aud['highest_cvr_age']}' delivered the highest conversion rate across demographics."})
    if best_aud.get('highest_cvr_gender'):
        audience_insights.append({'type': 'positive', 'title': 'Optimal Gender Demographic', 'message': f"Gender segment '{best_aud['highest_cvr_gender']}' achieved the top conversion efficiency."})

    # 4. DEVICE INSIGHTS
    best_dev: Optional[str] = devices.get('best_device')
    dev_metrics: Dict[str, Any] = devices.get('device_metrics', {})
    if best_dev and best_dev in dev_metrics:
        dev_info: Dict[str, Any] = dev_metrics[best_dev]
        device_insights.append({'type': 'positive', 'title': 'Leading Device Hardware', 'message': f"Device '{best_dev}' ranks highest in performance score with {dev_info.get('ctr', 0.0):.2f}% CTR and {dev_info.get('conversion_rate', 0.0):.2f}% CVR."})

    # 5. OBJECTIVE INSIGHTS
    best_obj: Optional[str] = objectives.get('best_objective')
    if best_obj:
        objective_insights.append({'type': 'positive', 'title': 'Top Performing Objective', 'message': f"Campaign objective '{best_obj}' delivered the strongest performance score across active goals."})

    # 6. TREND INSIGHTS
    growth: Dict[str, Any] = time_series.get('growth_rates', {}).get('daily', {})
    spend_g: float = float(growth.get('spend_growth_pct', 0.0))
    conv_g: float = float(growth.get('conversions_growth_pct', 0.0))
    if spend_g != 0 or conv_g != 0:
        trend_insights.append({'type': 'info', 'title': 'Period Trend Velocity', 'message': f"Recent daily period logged spend growth of {spend_g:+.2f}% and conversion growth of {conv_g:+.2f}%."})

    # 7. BUDGET INSIGHTS
    efficiency_map: Dict[str, Any] = campaigns.get('efficiency', {})
    inefficient_c: List[str] = [name for name, eff in efficiency_map.items() if eff.get('status') == 'Inefficient']
    if inefficient_c:
        budget_insights.append({'type': 'warning', 'title': 'Budget Allocation Discrepancy', 'message': f"{len(inefficient_c)} campaign(s) are absorbing spend share exceeding their conversion share yield."})
    else:
        budget_insights.append({'type': 'positive', 'title': 'Balanced Budget Distribution', 'message': "Campaign spend share aligns effectively with conversion generation across active assets."})

    # 8. FUNNEL INSIGHTS
    largest_drop: Optional[str] = funnel.get('largest_drop_off_stage')
    drop_pcts: Dict[str, float] = funnel.get('drop_off_pct', {})
    if largest_drop and largest_drop in drop_pcts:
        funnel_insights.append({'type': 'warning', 'title': 'Primary Funnel Bottleneck', 'message': f"The largest drop-off occurs at stage '{largest_drop}' with a {drop_pcts[largest_drop]:.2f}% customer drop-off rate."})

    # 9. OVERALL INSIGHTS
    total_campaign_count: int = len(campaigns.get('campaign_metrics', {}))
    overall_insights.append({'type': 'info', 'title': 'Account Performance Overview', 'message': f"Account analysis evaluated {total_campaign_count} active campaign(s) across {len(dev_metrics)} device category(ies)."})

    logger.info("Business insights report generated successfully across 9 categories")

    return {
        'kpis': kpi_insights,
        'campaigns': campaign_insights,
        'audience': audience_insights,
        'devices': device_insights,
        'objectives': objective_insights,
        'trends': trend_insights,
        'budget': budget_insights,
        'funnel': funnel_insights,
        'overall': overall_insights
    }


def _extract_campaign_detail(df: pd.DataFrame, index: Any) -> Dict[str, Any]:
    """Extract display-ready detail for a single campaign row.

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame.
    index : Any
        Target row index.

    Returns
    -------
    Dict[str, Any]
        Extracted campaign details map.
    """
    row: pd.Series = df.loc[index]
    return {
        'Campaign Name': row.get('campaign_name', 'N/A'),
        'Date': str(row.get('date', 'N/A')),
        'CTR': round(float(row.get('ctr_pct', 0.0)) * 100.0, 2) if pd.notna(row.get('ctr_pct')) else 0.0,
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
    performance_comparison: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Identify and extract details for best-performing campaigns.

    Parameters
    ----------
    df : pd.DataFrame
        Source campaign DataFrame.
    performance_comparison : Dict[str, Any]
        Performance comparison index dictionary.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        Extracted best performer details dictionary.
    """
    logger.info("Extracting best performers details")
    best_performance: Dict[str, Dict[str, Any]] = {}
    categories: List[str] = ['Best CTR', 'Highest conversion campaign']
    for category in categories:
        idx: Any = performance_comparison.get(category)
        if idx is not None and idx in df.index:
            row: pd.Series = df.loc[idx]
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


def _extract_performers(df: pd.DataFrame, indexes: pd.Index) -> Dict[int, Dict[str, Any]]:
    """Extract campaign details for a list of row indexes.

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame.
    indexes : pd.Index
        List of campaign row indexes.

    Returns
    -------
    Dict[int, Dict[str, Any]]
        Dictionary of campaign details keyed by index.
    """
    performers: Dict[int, Dict[str, Any]] = {}
    for idx in indexes:
        if idx in df.index:
            performers[int(idx)] = _extract_campaign_detail(df, idx)
    return performers


def generate_performer_insights(
    df: pd.DataFrame,
    performance_comparison: Dict[str, Any],
) -> Tuple[Dict[int, Dict[str, Any]], Dict[int, Dict[str, Any]], Dict[int, Dict[str, Any]]]:
    """Generate under-performer, high-performer, and low-CTR performer insights.

    Parameters
    ----------
    df : pd.DataFrame
        Source campaign DataFrame.
    performance_comparison : Dict[str, Any]
        Performance comparison index dictionary.

    Returns
    -------
    Tuple[Dict[int, Dict[str, Any]], Dict[int, Dict[str, Any]], Dict[int, Dict[str, Any]]]
        Tuple of (under_performers, high_performers, low_ctr_performers).
    """
    logger.info("Generating performer detail insights")
    under: Dict[int, Dict[str, Any]] = _extract_performers(df, performance_comparison.get('Low performing campaigns', pd.Index([])))
    high: Dict[int, Dict[str, Any]] = _extract_performers(df, performance_comparison.get('High performing campaigns', pd.Index([])))
    low_ctr: Dict[int, Dict[str, Any]] = _extract_performers(df, performance_comparison.get('Low CTR campaigns', pd.Index([])))
    return under, high, low_ctr


def _extract_anomaly_details(df: pd.DataFrame, indexes: pd.Index, fields: List[str]) -> Dict[int, Dict[str, Any]]:
    """Extract anomaly details for given row indexes.

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame.
    indexes : pd.Index
        Target anomaly row indexes.
    fields : List[str]
        List of field names to extract.

    Returns
    -------
    Dict[int, Dict[str, Any]]
        Extracted anomaly details map keyed by index.
    """
    details: Dict[int, Dict[str, Any]] = {}
    for idx in indexes:
        if idx in df.index:
            row: pd.Series = df.loc[idx]
            detail: Dict[str, Any] = {}
            for field in fields:
                val: Any = row.get(field, 'N/A')
                if field in ('budget_inr', 'spend_inr'):
                    detail[field.replace('_', ' ').title()] = f"₹ {val}" if val != 'N/A' else val
                else:
                    detail[field.replace('_', ' ').title()] = str(val) if field == 'date' else val
            details[int(idx)] = detail
    return details


def generate_anomaly_insights(
    df: pd.DataFrame,
    anomalies: Dict[str, Any],
) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Generate display-ready anomaly insights.

    Parameters
    ----------
    df : pd.DataFrame
        Source campaign DataFrame.
    anomalies : Dict[str, Any]
        Anomaly index dictionary mapping anomaly names to index series.

    Returns
    -------
    Dict[str, Dict[int, Dict[str, Any]]]
        Dictionary mapping anomaly names to row details dictionaries.
    """
    logger.info("Generating anomaly detail insights")
    common_fields: List[str] = ['campaign_name', 'objective', 'date', 'budget_inr', 'spend_inr']
    insights: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for anomaly_type, indexes in anomalies.items():
        if isinstance(indexes, (list, pd.Index)) and len(indexes) > 0:
            fields: List[str] = common_fields.copy()
            if anomaly_type == 'Missing impressions':
                fields.append('impressions')
            insights[anomaly_type] = _extract_anomaly_details(df, pd.Index(indexes), fields)
        else:
            insights[anomaly_type] = {}
    return insights
