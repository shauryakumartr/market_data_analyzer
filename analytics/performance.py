"""Module for identifying best, worst, and notable performance anomalies in campaigns.
"""

import pandas as pd
import logging
from typing import Any

logger = logging.getLogger(__name__)

def compare_performance(df: pd.DataFrame) -> dict[str, Any]:
    """Identify best, worst, and notable campaign performances.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered campaign DataFrame.

    Returns
    -------
    dict[str, Any]
        Performance comparison results mapping.
    """
    logger.info("Comparing performance across campaigns")
    comparison = {
        'Best CTR': None,
        'Worst CTR': None,
        'Highest conversion campaign': None,
        'Most expensive CPC': None,
        'highest spend': None,
        'Low performing campaigns': pd.Index([]),
        'High performing campaigns': pd.Index([]),
        'Low CTR campaigns': pd.Index([]),
        'Low Landing page conversion campaign': pd.Index([]),
    }

    if df.empty:
        logger.warning("Empty DataFrame passed to compare_performance. Returning default report.")
        return comparison

    try:
        # Best CTR
        if 'ctr_pct' in df.columns:
            comparison['Best CTR'] = df['ctr_pct'].idxmax()
            comparison['Worst CTR'] = df['ctr_pct'].idxmin()

        # Best Conversion Rate
        if 'conversion_rate_pct' in df.columns:
            comparison['Highest conversion campaign'] = df['conversion_rate_pct'].idxmax()

        # Most expensive CPC
        if 'cpc_inr' in df.columns:
            comparison['Most expensive CPC'] = df['cpc_inr'].idxmax()

        # Highest Spend
        if 'spend_inr' in df.columns:
            comparison['highest spend'] = df['spend_inr'].idxmax()

        # Low performing campaigns (above mean spend AND below mean conversion rate)
        if 'spend_inr' in df.columns and 'conversion_rate_pct' in df.columns:
            mean_spend = df['spend_inr'].mean()
            mean_cvr = df['conversion_rate_pct'].mean()
            low_perf_filter = (df['spend_inr'] >= mean_spend) & (df['conversion_rate_pct'] <= mean_cvr)
            comparison['Low performing campaigns'] = df[low_perf_filter].index

            # High performing campaigns (below mean spend AND above mean conversion rate)
            high_perf_filter = (df['spend_inr'] <= mean_spend) & (df['conversion_rate_pct'] >= mean_cvr)
            comparison['High performing campaigns'] = df[high_perf_filter].index

        # Low CTR campaigns (below mean CTR)
        if 'ctr_pct' in df.columns:
            mean_ctr = df['ctr_pct'].mean()
            low_ctr_filter = df['ctr_pct'] <= mean_ctr
            comparison['Low CTR campaigns'] = df[low_ctr_filter].index

        # Low Landing Page Conversions (below mean conversions AND above mean CTR)
        if 'conversions' in df.columns and 'ctr_pct' in df.columns:
            mean_conv = df['conversions'].mean()
            mean_ctr = df['ctr_pct'].mean()
            low_lp_filter = (df['conversions'] <= mean_conv) & (df['ctr_pct'] >= mean_ctr)
            comparison['Low Landing page conversion campaign'] = df[low_lp_filter].index

    except Exception as e:
        logger.error("Error encountered in performance comparison calculations: %s", e)

    return comparison
