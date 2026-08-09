"""Module for campaign objective performance analysis.

Aggregates metrics across marketing campaign objectives (e.g. Traffic, Conversions, Brand Awareness),
evaluates budget allocation shares vs conversion yields, and ranks marketing goals.
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

# Module-level logger for campaign objective analytics
logger: logging.Logger = logging.getLogger(__name__)


def analyze_objectives(df: pd.DataFrame, account_kpis: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Perform objective breakdowns and performance scoring.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.
    account_kpis : Optional[Dict[str, float]], optional
        Account KPIs.

    Returns
    -------
    Dict[str, Any]
        Objective metrics report containing objective_metrics and key best/worst objective targets.
    """
    logger.info("Executing campaign objective analysis across %d records", len(df))

    if account_kpis is None:
        account_kpis = {}

    if df.empty or 'objective' not in df.columns:
        logger.warning("Empty DataFrame or missing objective column in analyze_objectives")
        return {
            'objective_metrics': {},
            'best_objective': None,
            'worst_objective': None,
            'best_objective_by_ctr': None,
            'best_objective_by_conversions': None,
            'best_objective_by_roas': None,
            'most_budget_allocation_objective': None
        }

    agg_dict: Dict[str, str] = {}
    for col in ['spend_inr', 'budget_inr', 'impressions', 'clicks', 'conversions', 'reach', 'landing_page_views', 'add_to_cart', 'purchases']:
        if col in df.columns:
            agg_dict[col] = 'sum'

    grouped: pd.DataFrame = df.groupby('objective').agg(agg_dict)

    for col in ['spend_inr', 'budget_inr', 'impressions', 'clicks', 'conversions', 'reach', 'landing_page_views', 'add_to_cart', 'purchases']:
        if col not in grouped.columns:
            grouped[col] = 0.0

    if 'roas' in df.columns:
        temp: pd.DataFrame = df.copy()
        temp['revenue'] = temp['roas'] * temp['spend_inr']
        grouped['revenue'] = temp.groupby('objective')['revenue'].sum()
    else:
        grouped['revenue'] = 0.0

    grouped['ctr'] = (grouped['clicks'] / grouped['impressions'] * 100.0).fillna(0.0)
    grouped['cpc'] = (grouped['spend_inr'] / grouped['clicks']).fillna(0.0)
    grouped['cpm'] = (grouped['spend_inr'] / grouped['impressions'] * 1000.0).fillna(0.0)
    grouped['roas'] = (grouped['revenue'] / grouped['spend_inr']).fillna(0.0)
    grouped['conversion_rate'] = (grouped['conversions'] / grouped['clicks'] * 100.0).fillna(0.0)
    grouped['cost_per_conversion'] = (grouped['spend_inr'] / grouped['conversions']).fillna(0.0)

    total_budget: float = float(df['budget_inr'].sum()) if 'budget_inr' in df.columns else 0.0
    total_spend: float = float(df['spend_inr'].sum()) if 'spend_inr' in df.columns else 0.0
    total_conversions: float = float(df['conversions'].sum()) if 'conversions' in df.columns else 0.0

    grouped['spend_share'] = (grouped['spend_inr'] / total_spend * 100.0).fillna(0.0) if total_spend > 0 else 0.0
    grouped['conversion_share'] = (grouped['conversions'] / total_conversions * 100.0).fillna(0.0) if total_conversions > 0 else 0.0
    grouped['budget_allocation_pct'] = (grouped['budget_inr'] / total_budget * 100.0).fillna(0.0) if total_budget > 0 else 0.0

    grouped = add_performance_scores(grouped)

    classes: List[str] = []
    efficiencies: List[str] = []
    for idx, row in grouped.iterrows():
        classes.append(classify_performance_majority(row, account_kpis))
        efficiencies.append(classify_budget_efficiency(float(row['spend_share']), float(row['conversion_share'])))

    grouped['performance_class'] = classes
    grouped['budget_efficiency'] = efficiencies

    logger.info("Campaign objective analysis completed successfully")

    return {
        'objective_metrics': grouped.to_dict(orient='index'),
        'best_objective': str(grouped['performance_score'].idxmax()) if not grouped.empty else None,
        'worst_objective': str(grouped['performance_score'].idxmin()) if not grouped.empty else None,
        'best_objective_by_ctr': str(grouped['ctr'].idxmax()) if not grouped.empty else None,
        'best_objective_by_conversions': str(grouped['conversions'].idxmax()) if not grouped.empty else None,
        'best_objective_by_roas': str(grouped['roas'].idxmax()) if not grouped.empty else None,
        'most_budget_allocation_objective': str(grouped['spend_inr'].idxmax()) if not grouped.empty else None
    }
