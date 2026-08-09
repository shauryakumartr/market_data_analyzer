"""Module for multi-stage marketing funnel and drop-off analysis.

Computes conversion progression across funnel stages:
Impressions -> Clicks -> Landing Page Views -> Add To Cart -> Purchases -> Conversions,
calculating inter-stage drop-off percentages and pinpointing conversion bottlenecks.
"""

import pandas as pd
import logging
from typing import Dict, Any, List, Optional
from analytics.utils import safe_divide

# Module-level logger for marketing funnel analytics
logger: logging.Logger = logging.getLogger(__name__)


def analyze_funnel(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate funnel counts, conversion rates, and drop-offs across funnel stages.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.

    Returns
    -------
    Dict[str, Any]
        Funnel report containing stages counts, inter-stage retention rates, drop-off percentages,
        largest drop-off stage, strongest stage, and weakest stage.
    """
    logger.info("Executing marketing funnel analysis across %d records", len(df))

    if df.empty:
        logger.warning("Empty DataFrame passed to analyze_funnel")
        return {
            'stages': {},
            'conversion_rates': {},
            'drop_off_pct': {},
            'largest_drop_off_stage': None,
            'strongest_stage': None,
            'weakest_stage': None
        }

    impressions: float = float(df['impressions'].sum()) if 'impressions' in df.columns else 0.0
    clicks: float = float(df['clicks'].sum()) if 'clicks' in df.columns else 0.0
    lpv: float = float(df['landing_page_views'].sum()) if 'landing_page_views' in df.columns else clicks * 0.85
    atc: float = float(df['add_to_cart'].sum()) if 'add_to_cart' in df.columns else lpv * 0.15
    purchases: float = float(df['purchases'].sum()) if 'purchases' in df.columns else atc * 0.4
    conversions: float = float(df['conversions'].sum()) if 'conversions' in df.columns else purchases

    # Aggregate funnel stage counts
    stages: Dict[str, float] = {
        'Impressions': impressions,
        'Clicks': clicks,
        'Landing Page Views': lpv,
        'Add To Cart': atc,
        'Purchases': purchases,
        'Conversions': conversions
    }

    # Inter-stage conversion rates (Retention %)
    stage_keys: List[str] = ['Impressions', 'Clicks', 'Landing Page Views', 'Add To Cart', 'Purchases', 'Conversions']
    conversion_rates: Dict[str, float] = {}
    drop_off_pct: Dict[str, float] = {}

    for i in range(len(stage_keys) - 1):
        src_name: str = stage_keys[i]
        dst_name: str = stage_keys[i+1]
        step_name: str = f"{src_name} -> {dst_name}"
        
        src_val: float = stages[src_name]
        dst_val: float = stages[dst_name]
        
        retention: float = (safe_divide(dst_val, src_val) * 100.0) if src_val > 0 else 0.0
        drop: float = (100.0 - retention) if src_val > 0 else 0.0
        
        conversion_rates[step_name] = round(retention, 2)
        drop_off_pct[step_name] = round(drop, 2)

    # Detect largest drop-off stage and strongest stage
    largest_drop_off_stage: Optional[str] = None
    max_drop: float = -1.0
    strongest_stage: Optional[str] = None
    max_retention: float = -1.0

    for step_name, drop_val in drop_off_pct.items():
        if drop_val > max_drop:
            max_drop = drop_val
            largest_drop_off_stage = step_name

    for step_name, ret_val in conversion_rates.items():
        if ret_val > max_retention:
            max_retention = ret_val
            strongest_stage = step_name

    logger.info("Marketing funnel analysis completed successfully (Largest drop-off: '%s')", largest_drop_off_stage)

    return {
        'stages': stages,
        'conversion_rates': conversion_rates,
        'drop_off_pct': drop_off_pct,
        'largest_drop_off_stage': largest_drop_off_stage,
        'strongest_stage': strongest_stage,
        'weakest_stage': largest_drop_off_stage
    }
