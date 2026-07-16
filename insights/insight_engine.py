"""Module for processing analytics output into display-ready insights.
"""

import pandas as pd
import logging
from typing import Any

logger = logging.getLogger(__name__)

def generate_kpi_summary(basic_kpis: dict[str, float]) -> dict[str, Any]:
    """Transform raw KPI values into a display-ready summary.

    Parameters
    ----------
    basic_kpis : dict[str, float]
        Raw KPIs.

    Returns
    -------
    dict[str, Any]
        Display-ready KPI summary.
    """
    logger.info("Generating KPI summary")
    return {
        'Total Spend': basic_kpis.get('total_spend', 0.0),
        'Total Impressions': basic_kpis.get('total_impressions', 0.0),
        'Total Clicks': basic_kpis.get('total_clicks', 0.0),
        'Total Conversions': basic_kpis.get('total_conversions', 0.0),
        'Total Reach': basic_kpis.get('total_reach', 0.0),
        'Average CTR': round(basic_kpis.get('avg_ctr', 0.0), 2),
        'Average CPC': round(basic_kpis.get('avg_cpc', 0.0), 2),
        'Average CPM': round(basic_kpis.get('avg_cpm', 0.0), 2),
        'Conversion Effectiveness': round(float(basic_kpis.get('avg_conversion_rate', 0.0)), 2),
    }

def _extract_campaign_detail(df: pd.DataFrame, index: int) -> dict[str, Any]:
    """Extract display-ready detail for a single campaign row.
    """
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
    """Identify and extract details for best-performing campaigns.
    """
    logger.info("Extracting best performers details")
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
    """Extract campaign details for a list of row indexes.
    """
    performers = {}
    for idx in indexes:
        if idx in df.index:
            performers[int(idx)] = _extract_campaign_detail(df, idx)
    return performers

def generate_performer_insights(
    df: pd.DataFrame,
    performance_comparison: dict[str, Any],
) -> tuple[dict, dict, dict]:
    """Generate under-performer, high-performer, and low-CTR performer insights.
    """
    logger.info("Generating performer detail insights")
    under = _extract_performers(df, performance_comparison.get('Low performing campaigns', pd.Index([])))
    high = _extract_performers(df, performance_comparison.get('High performing campaigns', pd.Index([])))
    low_ctr = _extract_performers(df, performance_comparison.get('Low CTR campaigns', pd.Index([])))
    return under, high, low_ctr

def _extract_anomaly_details(df: pd.DataFrame, indexes: pd.Index, fields: list[str]) -> dict[int, dict[str, Any]]:
    """Extract anomaly details for given row indexes.
    """
    details = {}
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
            details[int(idx)] = detail
    return details

def generate_anomaly_insights(
    df: pd.DataFrame,
    anomalies: dict[str, pd.Index],
) -> dict[str, dict]:
    """Generate display-ready anomaly insights.
    """
    logger.info("Generating anomaly detail insights")
    common_fields = ['campaign_name', 'objective', 'date', 'budget_inr', 'spend_inr']
    insights = {}
    for anomaly_type, indexes in anomalies.items():
        if len(indexes) > 0:
            fields = common_fields.copy()
            if anomaly_type == 'Missing impressions':
                fields.append('impressions')
            insights[anomaly_type] = _extract_anomaly_details(df, indexes, fields)
        else:
            insights[anomaly_type] = {}
    return insights
