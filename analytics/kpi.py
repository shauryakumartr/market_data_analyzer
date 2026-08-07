"""Module for calculating account-level KPIs.
"""

import pandas as pd
import logging
from analytics.utils import (
    safe_divide,
    calculate_ctr,
    calculate_cpc,
    calculate_cpm,
    calculate_roas,
    calculate_conversion_rate
)

logger = logging.getLogger(__name__)

def calculate_account_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Calculate the global account-level KPIs.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.

    Returns
    -------
    dict[str, float]
        Flat dictionary of account-level KPIs.
    """
    logger.info("Calculating account-level KPIs")

    if df.empty:
        logger.warning("Empty DataFrame passed to calculate_account_kpis")
        return {
            'spend': 0.0,
            'budget': 0.0,
            'reach': 0.0,
            'impressions': 0.0,
            'clicks': 0.0,
            'ctr': 0.0,
            'cpc': 0.0,
            'cpm': 0.0,
            'conversions': 0.0,
            'conversion_rate': 0.0,
            'roas': 0.0,
            'frequency': 0.0,
            'avg_daily_spend': 0.0,
            'avg_cpc': 0.0,
            'avg_cpm': 0.0
        }

    # Sums of base columns
    total_spend = float(df['spend_inr'].sum()) if 'spend_inr' in df.columns else 0.0
    total_budget = float(df['budget_inr'].sum()) if 'budget_inr' in df.columns else 0.0
    total_reach = float(df['reach'].sum()) if 'reach' in df.columns else 0.0
    total_impressions = float(df['impressions'].sum()) if 'impressions' in df.columns else 0.0
    total_clicks = float(df['clicks'].sum()) if 'clicks' in df.columns else 0.0
    total_conversions = float(df['conversions'].sum()) if 'conversions' in df.columns else 0.0

    # Calculated metrics
    ctr = calculate_ctr(total_clicks, total_impressions)
    cpc = calculate_cpc(total_spend, total_clicks)
    cpm = calculate_cpm(total_spend, total_impressions)
    conversion_rate = calculate_conversion_rate(total_conversions, total_clicks)

    # Frequency = Impressions / Reach
    frequency = safe_divide(total_impressions, total_reach, default=1.0)

    # Average Daily Spend = Spend / Unique Days
    num_days = 1
    if 'date' in df.columns:
        unique_days = df['date'].nunique()
        if unique_days > 0:
            num_days = unique_days
    avg_daily_spend = safe_divide(total_spend, float(num_days))

    # ROAS Calculation (weighted by spend or direct revenue estimation)
    # Revenue = ROAS * Spend for each row. Total Revenue = sum(ROAS * Spend)
    # Total ROAS = Total Revenue / Total Spend
    total_revenue = 0.0
    if 'roas' in df.columns and 'spend_inr' in df.columns:
        # Avoid NaN multiplication
        valid_rows = df[['roas', 'spend_inr']].dropna()
        total_revenue = float((valid_rows['roas'] * valid_rows['spend_inr']).sum())
    
    roas = calculate_roas(total_revenue, total_spend)

    # Averages (Average CPC/CPM might be calculated similarly or identically to CPC/CPM at account level)
    # To follow instructions exactly: CPC/CPM is for the account, and we also supply avg_cpc/avg_cpm
    avg_cpc = cpc
    avg_cpm = cpm

    kpis = {
        'spend': total_spend,
        'budget': total_budget,
        'reach': total_reach,
        'impressions': total_impressions,
        'clicks': total_clicks,
        'ctr': ctr,
        'cpc': cpc,
        'cpm': cpm,
        'conversions': total_conversions,
        'conversion_rate': conversion_rate,
        'roas': roas,
        'frequency': frequency,
        'avg_daily_spend': avg_daily_spend,
        'avg_cpc': avg_cpc,
        'avg_cpm': avg_cpm
    }

    logger.info("Account KPIs calculation complete")
    return kpis
