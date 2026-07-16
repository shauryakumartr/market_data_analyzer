"""Module for aggregating and formatting the full summary used as AI context.
"""

import pandas as pd
import logging
from typing import Any

logger = logging.getLogger(__name__)

def build_ai_summary(
    kpis: dict[str, Any],
    best_performance: dict[str, dict],
    anomalies: dict[str, pd.Index],
    df: pd.DataFrame,
    recommendations: dict[str, Any],
    segmented_analysis: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """Build a summary dictionary for AI context.

    Parameters
    ----------
    kpis : dict
        Display-ready KPI summary.
    best_performance : dict
        Best performer details.
    anomalies : dict
        Anomaly indexes.
    df : pd.DataFrame
        Campaign DataFrame.
    recommendations : dict
        All recommendations.
    segmented_analysis : dict
        All segment DataFrames.

    Returns
    -------
    dict[str, Any]
        Combined summary for AI context.
    """
    logger.info("Building summary structure for AI context")
    summary = {}

    # KPIs
    summary['KPIs'] = kpis

    # Best performers
    for category, details in best_performance.items():
        summary[category] = {
            'Name': details.get('Name', 'N/A'),
            'CTR': details.get('CTR', 0.0),
            'Date': details.get('Date', 'N/A'),
            'Spend': details.get('Spend', 0.0),
        }

    # Anomalies summary
    for anomaly_type, indexes in anomalies.items():
        anomaly_details = {}
        for idx in indexes:
            if idx in df.index:
                row = df.loc[idx]
                anomaly_details[int(idx)] = (
                    f"Name {row.get('campaign_name', 'N/A')}, "
                    f"objective {row.get('objective', 'N/A')}, "
                    f"date {row.get('date', 'N/A')}, "
                    f"budget {row.get('budget_inr', 0.0)}, "
                    f"spend {row.get('spend_inr', 0.0)}"
                )
        if anomaly_details:
            summary[f"{anomaly_type} anomaly"] = anomaly_details

    # Recommendations
    for rec_key in ['Budget Reallocation', 'Reduce Spend', 'Creative Optimization', 'Landing Page Optimization']:
        if rec_key in recommendations and recommendations[rec_key]:
            summary[rec_key] = pd.DataFrame(recommendations[rec_key]).T

    # Segmented analysis summaries
    for segment_name, segment_df in segmented_analysis.items():
        if not segment_df.empty:
            display_cols = ['Total Spend', 'Total Clicks', 'Total Impressions', 'Total Conversions']
            available_cols = [c for c in display_cols if c in segment_df.columns]
            if available_cols:
                summary[segment_name] = segment_df[available_cols]

    return summary
