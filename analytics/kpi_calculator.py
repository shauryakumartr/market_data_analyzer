"""Module for calculating primary campaign KPIs.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def calculate_basic_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Calculate top-level campaign KPIs from the filtered dataset.

    KPIs calculated:
    - total_spend
    - total_impressions
    - total_clicks
    - total_conversions
    - total_reach
    - avg_ctr
    - avg_cpc
    - avg_cpm
    - avg_conversion_rate

    Parameters
    ----------
    df : pd.DataFrame
        Filtered campaign DataFrame.

    Returns
    -------
    dict[str, float]
        KPI mapping of name to numeric value.
    """
    logger.info("Calculating basic KPIs")
    
    total_spend = float(df['spend_inr'].sum()) if 'spend_inr' in df.columns else 0.0
    total_budget=float(df['budget_inr'].sum()) if 'budget_inr' in df.columns else 0.0
    total_impressions = float(df['impressions'].sum()) if 'impressions' in df.columns else 0.0
    total_clicks = float(df['clicks'].sum()) if 'clicks' in df.columns else 0.0
    total_conversions = float(df['conversions'].sum()) if 'conversions' in df.columns else 0.0
    total_reach = float(df['reach'].sum()) if 'reach' in df.columns else 0.0

    avg_ctr = (total_clicks / total_impressions) * 100.0 if total_impressions > 0 else 0.0
    avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0.0
    avg_cpm = (total_spend / total_impressions) * 1000.0 if total_impressions > 0 else 0.0
    avg_conversion_rate = (total_conversions / total_clicks) * 100.0 if total_clicks > 0 else 0.0
    kpis = {
        'total_spend': total_spend,
        'total_budget' : total_budget,
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_conversions': total_conversions,
        'total_reach': total_reach,
        'avg_ctr': avg_ctr,
        'avg_cpc': avg_cpc,
        'avg_cpm': avg_cpm,
        'avg_conversion_rate': avg_conversion_rate,
    }
    
    logger.info("KPI calculations completed successfully")
    return kpis
