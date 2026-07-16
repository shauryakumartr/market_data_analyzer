"""Module for generating campaign optimization recommendations based on analytics.
"""

import pandas as pd
import logging
from typing import Any

logger = logging.getLogger(__name__)

MAX_RECOMMENDATIONS: int = 10

def _extract_campaign_recommendation(
    df: pd.DataFrame,
    indexes: pd.Index,
    max_count: int = MAX_RECOMMENDATIONS,
) -> dict[int, dict[str, Any]]:
    """Extract campaign details for recommendation display.
    """
    result = {}
    for i, idx in enumerate(indexes):
        if i >= max_count:
            break
        if idx in df.index:
            row = df.loc[idx]
            result[int(idx)] = {
                'Name': row.get('campaign_name', 'N/A'),
                'Objective': row.get('objective', 'N/A'),
                'Date': str(row.get('date', 'N/A')),
                'Budget': row.get('budget_inr', 0.0),
                'Spend': row.get('spend_inr', 0.0),
                'CTR': round(row.get('ctr_pct', 0.0) * 100, 4) if pd.notna(row.get('ctr_pct')) else 0.0,
                'Conversion Rate': round(row.get('conversion_rate_pct', 0.0) * 100, 4) if pd.notna(row.get('conversion_rate_pct')) else 0.0,
            }
    return result

def _get_top_segment(
    segment_df: pd.DataFrame,
    sort_column: str = 'Segment CTR',
) -> dict[str, Any]:
    """Get the top-performing segment from a segmented analysis DataFrame.
    """
    if segment_df.empty:
        return {}
    top = segment_df.sort_values(by=sort_column, ascending=False).head(1)
    if top.empty:
        return {}
    index = top.index[0]
    return {
        'Name': index,
        'Segment CTR': top.loc[index, 'Segment CTR'] if 'Segment CTR' in top.columns else 0.0,
        'Total Impressions': top.loc[index, 'Total Impressions'] if 'Total Impressions' in top.columns else 0.0,
        'Total Clicks': top.loc[index, 'Total Clicks'] if 'Total Clicks' in top.columns else 0.0,
        'Segment CPC': top.loc[index, 'Segment CPC'] if 'Segment CPC' in top.columns else 0.0,
        'Total Spend': top.loc[index, 'Total Spend'] if 'Total Spend' in top.columns else 0.0,
    }

def generate_recommendations(
    df: pd.DataFrame,
    performance_comparison: dict[str, Any],
    segmented_analysis: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """Generate all campaign recommendations.
    """
    logger.info("Generating marketing recommendations")
    recommendations = {}

    # Campaign-level recommendations
    campaign_categories = {
        'Budget Reallocation': 'High performing campaigns',
        'Reduce Spend': 'Low performing campaigns',
        'Creative Optimization': 'Low CTR campaigns',
        'Landing Page Optimization': 'Low Landing page conversion campaign',
    }
    for rec_name, perf_key in campaign_categories.items():
        indexes = performance_comparison.get(perf_key, pd.Index([]))
        recommendations[rec_name] = _extract_campaign_recommendation(df, indexes)

    # Segment-level recommendations
    segment_mapping = {
        'Gender': 'gender_segment',
        'Age': 'age_segment',
        'Device': 'device_segment',
        'Campaign': 'objective_segment',
    }
    for rec_name, segment_key in segment_mapping.items():
        segment_df = segmented_analysis.get(segment_key, pd.DataFrame())
        recommendations[rec_name] = _get_top_segment(segment_df)

    return recommendations
