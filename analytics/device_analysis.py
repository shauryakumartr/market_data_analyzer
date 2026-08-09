"""Module for device performance analysis.

Aggregates metrics across device hardware types (Mobile, Desktop, Tablet, TV),
evaluates relative performance scores, efficiency shares, and identifies optimal device targeting.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from analytics.utils import (
    add_performance_scores,
    classify_performance_majority,
    classify_budget_efficiency
)

# Module-level logger for device performance analytics
logger: logging.Logger = logging.getLogger(__name__)


def analyze_devices(df: pd.DataFrame, account_kpis: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Perform device performance breakdown.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.
    account_kpis : Optional[Dict[str, float]], optional
        Account KPIs for benchmark evaluation.

    Returns
    -------
    Dict[str, Any]
        Device report containing metrics dictionary and best/worst performing devices.
    """
    logger.info("Executing device performance analysis across %d records", len(df))

    if account_kpis is None:
        account_kpis = {}

    if df.empty or 'device' not in df.columns:
        logger.warning("Empty DataFrame or missing device column in analyze_devices")
        return {
            'device_metrics': {},
            'best_device': None,
            'worst_device': None,
            'most_cost_efficient_device': None,
            'highest_converting_device': None,
            'highest_roas_device': None
        }

    agg_dict: Dict[str, str] = {}
    for col in ['spend_inr', 'budget_inr', 'impressions', 'clicks', 'conversions', 'reach', 'landing_page_views', 'add_to_cart', 'purchases']:
        if col in df.columns:
            agg_dict[col] = 'sum'

    grouped: pd.DataFrame = df.groupby('device').agg(agg_dict)

    for col in ['spend_inr', 'budget_inr', 'impressions', 'clicks', 'conversions', 'reach', 'landing_page_views', 'add_to_cart', 'purchases']:
        if col not in grouped.columns:
            grouped[col] = 0.0

    if 'roas' in df.columns:
        temp: pd.DataFrame = df.copy()
        temp['revenue'] = temp['roas'] * temp['spend_inr']
        grouped['revenue'] = temp.groupby('device')['revenue'].sum()
    else:
        grouped['revenue'] = 0.0

    grouped['ctr'] = (grouped['clicks'] / grouped['impressions'] * 100.0).fillna(0.0)
    grouped['cpc'] = (grouped['spend_inr'] / grouped['clicks']).fillna(0.0)
    grouped['cpm'] = (grouped['spend_inr'] / grouped['impressions'] * 1000.0).fillna(0.0)
    grouped['roas'] = (grouped['revenue'] / grouped['spend_inr']).fillna(0.0)
    grouped['conversion_rate'] = (grouped['conversions'] / grouped['clicks'] * 100.0).fillna(0.0)
    grouped['cost_per_conversion'] = (grouped['spend_inr'] / grouped['conversions']).fillna(0.0)

    total_spend: float = float(df['spend_inr'].sum()) if 'spend_inr' in df.columns else 0.0
    total_conversions: float = float(df['conversions'].sum()) if 'conversions' in df.columns else 0.0

    grouped['spend_share'] = (grouped['spend_inr'] / total_spend * 100.0).fillna(0.0) if total_spend > 0 else 0.0
    grouped['conversion_share'] = (grouped['conversions'] / total_conversions * 100.0).fillna(0.0) if total_conversions > 0 else 0.0

    grouped = add_performance_scores(grouped)

    classes: List[str] = []
    efficiencies: List[str] = []
    for idx, row in grouped.iterrows():
        classes.append(classify_performance_majority(row, account_kpis))
        efficiencies.append(classify_budget_efficiency(float(row['spend_share']), float(row['conversion_share'])))

    grouped['performance_class'] = classes
    grouped['budget_efficiency'] = efficiencies

    best_device: Optional[str] = str(grouped['performance_score'].idxmax()) if not grouped.empty else None
    worst_device: Optional[str] = str(grouped['performance_score'].idxmin()) if not grouped.empty else None

    logger.info("Device performance analysis completed successfully")

    return {
        'device_metrics': grouped.to_dict(orient='index'),
        'best_device': best_device,
        'worst_device': worst_device,
        'most_cost_efficient_device': str(grouped['cpc'].replace(0, np.nan).idxmin()) if not grouped.empty else None,
        'highest_converting_device': str(grouped['conversion_rate'].idxmax()) if not grouped.empty else None,
        'highest_roas_device': str(grouped['roas'].idxmax()) if not grouped.empty else None
    }
