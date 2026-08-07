"""Module for device performance analysis.
"""

import pandas as pd
import numpy as np
import logging
from typing import Any
from analytics.utils import (
    add_performance_scores,
    classify_performance_majority,
    classify_budget_efficiency
)

logger = logging.getLogger(__name__)

def analyze_devices(df: pd.DataFrame, account_kpis: dict = None) -> dict[str, Any]:
    """Perform device performance breakdown.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.
    account_kpis : dict, optional
        Account KPIs.

    Returns
    -------
    dict[str, Any]
        Device report.
    """
    logger.info("Executing device performance analysis")

    if account_kpis is None:
        account_kpis = {}

    if df.empty or 'device' not in df.columns:
        logger.warning("Empty DataFrame or missing device column in analyze_devices")
        return {
            'device_metrics': {},
            'best_device': None,
            'worst_device': None
        }

    agg_dict = {
        'spend_inr': 'sum',
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum',
        'reach': 'sum'
    }

    for col in ['landing_page_views', 'add_to_cart', 'purchases']:
        if col in df.columns:
            agg_dict[col] = 'sum'

    grouped = df.groupby('device').agg(agg_dict)

    for col in ['landing_page_views', 'add_to_cart', 'purchases']:
        if col not in grouped.columns:
            grouped[col] = 0.0

    if 'roas' in df.columns:
        temp = df.copy()
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

    total_spend = df['spend_inr'].sum()
    total_conversions = df['conversions'].sum()

    grouped['spend_share'] = (grouped['spend_inr'] / total_spend * 100.0).fillna(0.0) if total_spend > 0 else 0.0
    grouped['conversion_share'] = (grouped['conversions'] / total_conversions * 100.0).fillna(0.0) if total_conversions > 0 else 0.0

    grouped = add_performance_scores(grouped)

    classes = []
    efficiencies = []
    for idx, row in grouped.iterrows():
        classes.append(classify_performance_majority(row, account_kpis))
        efficiencies.append(classify_budget_efficiency(row['spend_share'], row['conversion_share']))

    grouped['performance_class'] = classes
    grouped['budget_efficiency'] = efficiencies

    best_device = grouped['performance_score'].idxmax() if not grouped.empty else None
    worst_device = grouped['performance_score'].idxmin() if not grouped.empty else None

    return {
        'device_metrics': grouped.to_dict(orient='index'),
        'best_device': best_device,
        'worst_device': worst_device,
        'most_cost_efficient_device': grouped['cpc'].replace(0, np.nan).idxmin() if not grouped.empty else None,
        'highest_converting_device': grouped['conversion_rate'].idxmax() if not grouped.empty else None,
        'highest_roas_device': grouped['roas'].idxmax() if not grouped.empty else None
    }
