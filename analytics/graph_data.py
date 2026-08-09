"""Module for preparing data frames and series required by UI graphs.

Generates aggregated chart datasets (Spend over time, CTR vs Conversions, Segment breakdowns,
Objective distributions, and Scatter aggregations) consumed by Plotly visualization builders.
"""

import pandas as pd
import logging
from typing import Dict, Union, Any

# Module-level logger for graph data preparation
logger: logging.Logger = logging.getLogger(__name__)


def prepare_graph_data(df: pd.DataFrame) -> Dict[str, Union[pd.DataFrame, pd.Series]]:
    """Prepare all data structures needed for chart visualization.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered campaign DataFrame.

    Returns
    -------
    Dict[str, Union[pd.DataFrame, pd.Series]]
        Aggregated chart data series and data frames mapped by figure key.
    """
    logger.info("Preparing visualization graph dataset across %d records", len(df))
    graph_data: Dict[str, Union[pd.DataFrame, pd.Series]] = {}

    if df.empty:
        logger.warning("Empty DataFrame passed to prepare_graph_data")
        return graph_data

    try:
        # Campaign Name vs Spend
        if 'campaign_name' in df.columns and 'spend_inr' in df.columns:
            graph_data['campaign_name_vs_spend'] = df.groupby('campaign_name')['spend_inr'].sum()

        # Campaign Name vs Conversion Rate
        if 'campaign_name' in df.columns and 'conversions' in df.columns and 'clicks' in df.columns:
            total_conversions: pd.Series = df.groupby('campaign_name')['conversions'].sum()
            total_clicks: pd.Series = df.groupby('campaign_name')['clicks'].sum()
            graph_data['campaign_name_vs_conversion_rate'] = (total_conversions / total_clicks.replace(0, float('nan'))).fillna(0) * 100.0

        # Device vs Conversion Rate
        if 'device' in df.columns and 'conversions' in df.columns and 'clicks' in df.columns:
            total_conversions = df.groupby('device')['conversions'].sum()
            total_clicks = df.groupby('device')['clicks'].sum()
            graph_data['device_vs_conversion_rate'] = (total_conversions / total_clicks.replace(0, float('nan'))).fillna(0) * 100.0

        # Spend vs Conversions
        if 'campaign_name' in df.columns and 'spend_inr' in df.columns and 'conversions' in df.columns:
            graph_data['spend_vs_conversions'] = df.groupby('campaign_name').agg({'spend_inr': 'sum', 'conversions': 'sum'})

        # Campaign name vs CTR
        if 'campaign_name' in df.columns and 'clicks' in df.columns and 'impressions' in df.columns:
            total_clicks = df.groupby('campaign_name')['clicks'].sum()
            total_impressions: pd.Series = df.groupby('campaign_name')['impressions'].sum()
            graph_data['campaign_name_vs_ctr'] = (total_clicks / total_impressions.replace(0, float('nan'))).fillna(0) * 100.0

        # Campaign name vs CPC
        if 'campaign_name' in df.columns and 'spend_inr' in df.columns and 'clicks' in df.columns:
            total_spend: pd.Series = df.groupby('campaign_name')['spend_inr'].sum()
            total_clicks = df.groupby('campaign_name')['clicks'].sum()
            graph_data['campaign_name_vs_cpc'] = (total_spend / total_clicks.replace(0, float('nan'))).fillna(0)

        # Objective vs Spend
        if 'objective' in df.columns and 'spend_inr' in df.columns:
            graph_data['objective_vs_spend'] = df.groupby('objective')['spend_inr'].sum()

        # Objective vs Conversion Rate
        if 'objective' in df.columns and 'conversions' in df.columns and 'clicks' in df.columns:
            total_conversions = df.groupby('objective')['conversions'].sum()
            total_clicks = df.groupby('objective')['clicks'].sum()
            graph_data['objective_vs_conversion_rate'] = (total_conversions / total_clicks.replace(0, float('nan'))).fillna(0) * 100.0

        # Device vs CTR
        if 'device' in df.columns and 'clicks' in df.columns and 'impressions' in df.columns:
            total_clicks = df.groupby('device')['clicks'].sum()
            total_impressions = df.groupby('device')['impressions'].sum()
            graph_data['device_vs_ctr'] = (total_clicks / total_impressions.replace(0, float('nan'))).fillna(0) * 100.0

        # Device vs CPC
        if 'device' in df.columns and 'spend_inr' in df.columns and 'clicks' in df.columns:
            total_spend = df.groupby('device')['spend_inr'].sum()
            total_clicks = df.groupby('device')['clicks'].sum()
            graph_data['device_vs_cpc'] = (total_spend / total_clicks.replace(0, float('nan'))).fillna(0)

        # Gender vs CTR
        if 'gender' in df.columns and 'clicks' in df.columns and 'impressions' in df.columns:
            total_clicks = df.groupby('gender')['clicks'].sum()
            total_impressions = df.groupby('gender')['impressions'].sum()
            graph_data['gender_vs_ctr'] = (total_clicks / total_impressions.replace(0, float('nan'))).fillna(0) * 100.0

        # Gender vs Conversion Rate
        if 'gender' in df.columns and 'conversions' in df.columns and 'clicks' in df.columns:
            total_conversions = df.groupby('gender')['conversions'].sum()
            total_clicks = df.groupby('gender')['clicks'].sum()
            graph_data['gender_vs_conversion_rate'] = (total_conversions / total_clicks.replace(0, float('nan'))).fillna(0) * 100.0

        # Age Group vs CTR
        if 'age_group' in df.columns and 'clicks' in df.columns and 'impressions' in df.columns:
            total_clicks = df.groupby('age_group')['clicks'].sum()
            total_impressions = df.groupby('age_group')['impressions'].sum()
            graph_data['age_group_vs_ctr'] = (total_clicks / total_impressions.replace(0, float('nan'))).fillna(0) * 100.0

        # Age Group vs Conversion Rate
        if 'age_group' in df.columns and 'conversions' in df.columns and 'clicks' in df.columns:
            total_conversions = df.groupby('age_group')['conversions'].sum()
            total_clicks = df.groupby('age_group')['clicks'].sum()
            graph_data['age_group_vs_conversion_rate'] = (total_conversions / total_clicks.replace(0, float('nan'))).fillna(0) * 100.0

        # Time series aggregations
        if 'date' in df.columns:
            df_sorted: pd.DataFrame = df.sort_values('date')
            
            if 'spend_inr' in df_sorted.columns:
                graph_data['spend_over_time'] = df_sorted.groupby('date')['spend_inr'].sum()
            
            if 'clicks' in df_sorted.columns:
                graph_data['clicks_over_time'] = df_sorted.groupby('date')['clicks'].sum()
            
            if 'conversions' in df_sorted.columns:
                graph_data['conversions_over_time'] = df_sorted.groupby('date')['conversions'].sum()
            
            if 'clicks' in df_sorted.columns and 'impressions' in df_sorted.columns:
                daily_clicks: pd.Series = df_sorted.groupby('date')['clicks'].sum()
                daily_impressions: pd.Series = df_sorted.groupby('date')['impressions'].sum()
                graph_data['ctr_over_time'] = (daily_clicks / daily_impressions.replace(0, float('nan'))).fillna(0) * 100.0

        # Spend/Conversions Distribution by Objective
        if 'objective' in df.columns:
            if 'spend_inr' in df.columns:
                graph_data['spend_distribution_by_objective'] = df.groupby('objective')['spend_inr'].sum()
            if 'conversions' in df.columns:
                graph_data['conversions_distribution_by_objective'] = df.groupby('objective')['conversions'].sum()

        # Spend vs CTR
        if 'campaign_name' in df.columns and 'spend_inr' in df.columns and 'ctr_pct' in df.columns:
            graph_data['spend_vs_ctr'] = df.groupby('campaign_name').agg({'spend_inr': 'sum', 'ctr_pct': 'median'})

        # Clicks vs Conversions
        if 'campaign_name' in df.columns and 'clicks' in df.columns and 'conversions' in df.columns:
            graph_data['clicks_vs_conversions'] = df.groupby('campaign_name').agg({'clicks': 'sum', 'conversions': 'sum'})

        # Impressions vs Clicks
        if 'campaign_name' in df.columns and 'impressions' in df.columns and 'clicks' in df.columns:
            graph_data['impressions_vs_clicks'] = df.groupby('campaign_name').agg({'impressions': 'sum', 'clicks': 'sum'})

    except Exception as e:
        logger.error("Error encountered in preparing graph data: %s", e)

    return graph_data
