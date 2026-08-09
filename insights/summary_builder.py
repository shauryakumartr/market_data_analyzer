"""Module for aggregating and formatting the full summary used as AI context.

Compiles KPIs, top performance details, anomaly indices, recommendations, and segment breakdowns
into a unified dictionary payload for generative AI context consumption.
"""

import pandas as pd
import logging
from typing import Dict, Any, List

# Module-level logger for AI summary building operations
logger: logging.Logger = logging.getLogger(__name__)


def build_ai_summary(
    kpis: Dict[str, Any],
    best_performance: Dict[str, Dict[str, Any]],
    anomalies: Dict[str, pd.Index],
    df: pd.DataFrame,
    recommendations: Dict[str, Any],
    segmented_analysis: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    """Build a summary dictionary payload for AI context integration.

    Parameters
    ----------
    kpis : Dict[str, Any]
        Display-ready KPI summary dictionary.
    best_performance : Dict[str, Dict[str, Any]]
        Best performer details dictionary.
    anomalies : Dict[str, pd.Index]
        Anomaly indexes dictionary.
    df : pd.DataFrame
        Campaign DataFrame.
    recommendations : Dict[str, Any]
        All generated recommendations.
    segmented_analysis : Dict[str, pd.DataFrame]
        Segment breakdown DataFrames map.

    Returns
    -------
    Dict[str, Any]
        Combined summary payload dictionary.
    """
    logger.info("Building summary structure for AI context consumption")
    summary: Dict[str, Any] = {}

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
        anomaly_details: Dict[int, str] = {}
        for idx in indexes:
            if idx in df.index:
                row: pd.Series = df.loc[idx]
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
            display_cols: List[str] = ['Total Spend', 'Total Clicks', 'Total Impressions', 'Total Conversions']
            available_cols: List[str] = [c for c in display_cols if c in segment_df.columns]
            if available_cols:
                summary[segment_name] = segment_df[available_cols]

    logger.info("AI context summary structure generated successfully")

    return summary
