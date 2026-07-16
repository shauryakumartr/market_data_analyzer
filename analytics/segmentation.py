"""Module for segmented cohort analysis on marketing data.
"""

import pandas as pd
import logging
from config.settings import SEGMENT_COLUMNS

logger = logging.getLogger(__name__)

def _aggregate_segment(df: pd.DataFrame, segment_column: str) -> pd.DataFrame:
    """Aggregate campaign metrics by a segment column.

    Parameters
    ----------
    df : pd.DataFrame
        Campaign DataFrame.
    segment_column : str
        Column name to group by.

    Returns
    -------
    pd.DataFrame
        Aggregated segment DataFrame with display columns.
    """
    logger.info("Aggregating segment on column: %s", segment_column)
    
    # Core aggregation
    grouped = df.groupby(segment_column, as_index=True).agg({
        'spend_inr': 'sum',
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum',
        'ctr_pct': 'median',
        'cpc_inr': 'median',
        'conversion_rate_pct': 'median'
    })

    # Calculations
    grouped['Segment CTR'] = (grouped['clicks'] / grouped['impressions']) if 'impressions' in grouped.columns else 0.0
    grouped['Segment CPC'] = (grouped['spend_inr'] / grouped['clicks']) if 'clicks' in grouped.columns else 0.0
    grouped['Segment Conversion Rate'] = (grouped['conversions'] / grouped['clicks']) if 'clicks' in grouped.columns else 0.0

    # Fill NaN values resulting from 0 divisions
    grouped.fillna(0.0, inplace=True)

    # Rename columns for presentation
    grouped.rename(columns={
        'spend_inr': 'Total Spend',
        'impressions': 'Total Impressions',
        'clicks': 'Total Clicks',
        'conversions': 'Total Conversions',
        'ctr_pct': 'Average CTR',
        'cpc_inr': 'Average CPC',
        'conversion_rate_pct': 'Average Conversion Rate'
    }, inplace=True)

    return grouped

def analyze_segments(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Run segmented analysis across all standard segments.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered campaign DataFrame.

    Returns
    -------
    dict[str, pd.DataFrame]
        Segmented analysis results.
    """
    logger.info("Running complete segmented analysis")
    segmented_results = {}

    if df.empty:
        logger.warning("Empty DataFrame passed to analyze_segments")
        return {
            'age_segment': pd.DataFrame(),
            'gender_segment': pd.DataFrame(),
            'device_segment': pd.DataFrame(),
            'objective_segment': pd.DataFrame()
        }

    segment_keys = {
        'age_group': 'age_segment',
        'gender': 'gender_segment',
        'device': 'device_segment',
        'objective': 'objective_segment'
    }

    for col, result_key in segment_keys.items():
        if col in df.columns:
            segmented_results[result_key] = _aggregate_segment(df, col)
        else:
            logger.warning("Segment column '%s' missing from DataFrame. Skipping.", col)
            segmented_results[result_key] = pd.DataFrame()

    return segmented_results
