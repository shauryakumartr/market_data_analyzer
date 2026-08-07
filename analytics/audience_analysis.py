"""Module for demographic audience analysis.
"""

import pandas as pd
import numpy as np
import logging
from typing import Any
from analytics.utils import (
    safe_divide,
    add_performance_scores,
    classify_performance_majority,
    classify_budget_efficiency
)

logger = logging.getLogger(__name__)

def _aggregate_audience(df: pd.DataFrame, group_col: str, account_kpis: dict) -> pd.DataFrame:
    """Helper to aggregate metric by audience group column and score it.
    """
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

    grouped = df.groupby(group_col).agg(agg_dict)

    for col in ['landing_page_views', 'add_to_cart', 'purchases']:
        if col not in grouped.columns:
            grouped[col] = 0.0

    if 'roas' in df.columns:
        temp = df.copy()
        temp['revenue'] = temp['roas'] * temp['spend_inr']
        grouped['revenue'] = temp.groupby(group_col)['revenue'].sum()
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

    # Add classifications
    classes = []
    efficiencies = []
    for idx, row in grouped.iterrows():
        classes.append(classify_performance_majority(row, account_kpis))
        efficiencies.append(classify_budget_efficiency(row['spend_share'], row['conversion_share']))

    grouped['performance_class'] = classes
    grouped['budget_efficiency'] = efficiencies

    return grouped

def analyze_audience(df: pd.DataFrame, account_kpis: dict = None) -> dict[str, Any]:
    """Perform demographic audience analysis.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.
    account_kpis : dict, optional
        Global account KPIs.

    Returns
    -------
    dict[str, Any]
        Demographic report.
    """
    logger.info("Executing audience demographic analysis")

    if account_kpis is None:
        account_kpis = {}

    if df.empty:
        logger.warning("Empty DataFrame passed to analyze_audience")
        return {
            'gender_analysis': {},
            'age_analysis': {},
            'best_audience': {},
            'worst_audience': {}
        }

    gender_df = pd.DataFrame()
    age_df = pd.DataFrame()

    if 'gender' in df.columns:
        gender_df = _aggregate_audience(df, 'gender', account_kpis)

    if 'age_group' in df.columns:
        age_df = _aggregate_audience(df, 'age_group', account_kpis)

    best_audience = {
        'highest_roas_age': age_df['roas'].idxmax() if not age_df.empty else None,
        'highest_cvr_age': age_df['conversion_rate'].idxmax() if not age_df.empty else None,
        'highest_ctr_age': age_df['ctr'].idxmax() if not age_df.empty else None,
        'lowest_cpc_age': age_df['cpc'].replace(0, np.nan).idxmin() if not age_df.empty else None,
        'highest_roas_gender': gender_df['roas'].idxmax() if not gender_df.empty else None,
        'highest_cvr_gender': gender_df['conversion_rate'].idxmax() if not gender_df.empty else None,
        'highest_ctr_gender': gender_df['ctr'].idxmax() if not gender_df.empty else None,
        'lowest_cpc_gender': gender_df['cpc'].replace(0, np.nan).idxmin() if not gender_df.empty else None
    }

    worst_audience = {
        'lowest_roas_age': age_df['roas'].idxmin() if not age_df.empty else None,
        'lowest_cvr_age': age_df['conversion_rate'].idxmin() if not age_df.empty else None,
        'lowest_roas_gender': gender_df['roas'].idxmin() if not gender_df.empty else None,
        'lowest_cvr_gender': gender_df['conversion_rate'].idxmin() if not gender_df.empty else None
    }

    return {
        'gender_analysis': gender_df.to_dict(orient='index') if not gender_df.empty else {},
        'age_analysis': age_df.to_dict(orient='index') if not age_df.empty else {},
        'best_audience': best_audience,
        'worst_audience': worst_audience
    }
