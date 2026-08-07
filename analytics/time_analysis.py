"""Module for time-based trends and growth analysis.
"""

import pandas as pd
import logging
from typing import Any

logger = logging.getLogger(__name__)

def _aggregate_time(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """Group and aggregate by time periods ('D', 'W', 'M').
    """
    temp_df = df.copy()
    temp_df['date'] = pd.to_datetime(temp_df['date'])
    
    if period == 'W':
        groupby_series = temp_df['date'].dt.to_period('W').dt.start_time
    elif period == 'M':
        groupby_series = temp_df['date'].dt.to_period('M').dt.start_time
    else:
        groupby_series = temp_df['date']

    grouped = temp_df.groupby(groupby_series).agg({
        'spend_inr': 'sum',
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum',
        'reach': 'sum'
    })

    if 'roas' in temp_df.columns:
        temp_df['revenue'] = temp_df['roas'] * temp_df['spend_inr']
        grouped['revenue'] = temp_df.groupby(groupby_series)['revenue'].sum()
        grouped['roas'] = (grouped['revenue'] / grouped['spend_inr']).fillna(0.0)
    else:
        grouped['roas'] = 0.0

    grouped['ctr'] = (grouped['clicks'] / grouped['impressions'] * 100.0).fillna(0.0)
    grouped['cpc'] = (grouped['spend_inr'] / grouped['clicks']).fillna(0.0)
    grouped['cpm'] = (grouped['spend_inr'] / grouped['impressions'] * 1000.0).fillna(0.0)
    grouped['conversion_rate'] = (grouped['conversions'] / grouped['clicks'] * 100.0).fillna(0.0)

    # Convert index back to string dates for simple JSON serialization
    grouped.index = grouped.index.map(lambda x: x.strftime('%Y-%m-%d'))
    return grouped

def analyze_time(df: pd.DataFrame) -> dict[str, Any]:
    """Analyze campaign performance over time (daily, weekly, monthly).

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.

    Returns
    -------
    dict[str, Any]
        Time series analysis results mapping containing daily, weekly, and monthly data.
    """
    logger.info("Starting time-series analysis")

    if df.empty or 'date' not in df.columns:
        logger.warning("Empty DataFrame or missing date column in analyze_time")
        return {
            'daily': {},
            'weekly': {},
            'monthly': {},
            'growth_rates': {},
            'trend_directions': {}
        }

    try:
        daily_df = _aggregate_time(df, 'D')
        weekly_df = _aggregate_time(df, 'W')
        monthly_df = _aggregate_time(df, 'M')
    except Exception as e:
        logger.error("Error aggregating time series: %s", e)
        return {
            'daily': {},
            'weekly': {},
            'monthly': {},
            'growth_rates': {},
            'trend_directions': {}
        }

    # Calculate growth rates and trend directions (e.g. comparing last period to previous)
    growth_rates = {}
    trend_directions = {}

    for name, trend_df in [('daily', daily_df), ('weekly', weekly_df), ('monthly', monthly_df)]:
        if len(trend_df) >= 2:
            last_row = trend_df.iloc[-1]
            prev_row = trend_df.iloc[-2]
            
            # Spend growth
            spend_growth = ((last_row['spend_inr'] - prev_row['spend_inr']) / prev_row['spend_inr'] * 100.0) if prev_row['spend_inr'] > 0 else 0.0
            # CTR growth
            ctr_growth = last_row['ctr'] - prev_row['ctr']
            # Conversions growth
            conv_growth = ((last_row['conversions'] - prev_row['conversions']) / prev_row['conversions'] * 100.0) if prev_row['conversions'] > 0 else 0.0
            
            growth_rates[name] = {
                'spend_growth_pct': float(spend_growth),
                'ctr_growth_diff': float(ctr_growth),
                'conversions_growth_pct': float(conv_growth)
            }

            trend_directions[name] = {
                'spend': 'up' if spend_growth > 0 else 'down' if spend_growth < 0 else 'flat',
                'ctr': 'up' if ctr_growth > 0 else 'down' if ctr_growth < 0 else 'flat',
                'conversions': 'up' if conv_growth > 0 else 'down' if conv_growth < 0 else 'flat'
            }
        else:
            growth_rates[name] = {'spend_growth_pct': 0.0, 'ctr_growth_diff': 0.0, 'conversions_growth_pct': 0.0}
            trend_directions[name] = {'spend': 'flat', 'ctr': 'flat', 'conversions': 'flat'}

    return {
        'daily': daily_df.to_dict(orient='index'),
        'weekly': weekly_df.to_dict(orient='index'),
        'monthly': monthly_df.to_dict(orient='index'),
        'growth_rates': growth_rates,
        'trend_directions': trend_directions
    }
