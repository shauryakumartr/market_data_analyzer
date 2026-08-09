"""Module for calculating account-level KPIs.

Aggregates global account metrics including total spend, budget, impressions, clicks, conversions,
calculated CTR, CPC, CPM, CVR, ROAS, frequency, and average daily spend.
"""

import pandas as pd
import logging
from typing import Dict

from analytics.utils import (
    safe_divide,
    calculate_ctr,
    calculate_cpc,
    calculate_cpm,
    calculate_roas,
    calculate_conversion_rate
)

# Module-level logger for account KPI calculations
logger: logging.Logger = logging.getLogger(__name__)


def calculate_account_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate global account-level KPIs.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.

    Returns
    -------
    Dict[str, float]
        Flat dictionary of global account-level KPI metrics.
    """
    logger.info("Executing account-level KPI calculations across %d records", len(df))

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
    total_spend: float = float(df['spend_inr'].sum()) if 'spend_inr' in df.columns else 0.0
    total_budget: float = float(df['budget_inr'].sum()) if 'budget_inr' in df.columns else 0.0
    total_reach: float = float(df['reach'].sum()) if 'reach' in df.columns else 0.0
    total_impressions: float = float(df['impressions'].sum()) if 'impressions' in df.columns else 0.0
    total_clicks: float = float(df['clicks'].sum()) if 'clicks' in df.columns else 0.0
    total_conversions: float = float(df['conversions'].sum()) if 'conversions' in df.columns else 0.0

    # Calculated metrics
    ctr: float = calculate_ctr(total_clicks, total_impressions)
    cpc: float = calculate_cpc(total_spend, total_clicks)
    cpm: float = calculate_cpm(total_spend, total_impressions)
    conversion_rate: float = calculate_conversion_rate(total_conversions, total_clicks)

    # Frequency = Impressions / Reach
    frequency: float = safe_divide(total_impressions, total_reach, default=1.0)

    # Average Daily Spend = Spend / Unique Days
    num_days: int = 1
    if 'date' in df.columns:
        unique_days: int = int(df['date'].nunique())
        if unique_days > 0:
            num_days = unique_days
    avg_daily_spend: float = safe_divide(total_spend, float(num_days))

    # ROAS Calculation (weighted by spend)
    total_revenue: float = 0.0
    if 'roas' in df.columns and 'spend_inr' in df.columns:
        valid_rows: pd.DataFrame = df[['roas', 'spend_inr']].dropna()
        total_revenue = float((valid_rows['roas'] * valid_rows['spend_inr']).sum())
    
    roas: float = calculate_roas(total_revenue, total_spend)

    avg_cpc: float = cpc
    avg_cpm: float = cpm

    kpis: Dict[str, float] = {
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

    logger.info("Account KPIs calculation completed successfully")
    return kpis
