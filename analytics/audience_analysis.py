"""Module for demographic audience analysis.

Aggregates campaign metrics across demographic dimensions (gender and age group),
computes efficiency shares, scores demographic segments, and identifies best/worst audience segments.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from analytics.utils import (
    safe_divide,
    add_performance_scores,
    classify_performance_majority,
    classify_budget_efficiency
)

# Module-level logger for demographic audience analytics
logger: logging.Logger = logging.getLogger(__name__)


def _aggregate_audience(df: pd.DataFrame, group_col: str, account_kpis: Dict[str, float]) -> pd.DataFrame:
    """Helper function to aggregate metrics by audience group column and compute performance scores.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.
    group_col : str
        Demographic column name ('gender' or 'age_group').
    account_kpis : Dict[str, float]
        Global account KPIs for relative comparison.

    Returns
    -------
    pd.DataFrame
        Aggregated demographic segment DataFrame.
    """
    agg_dict: Dict[str, str] = {}
    for col in ['spend_inr', 'budget_inr', 'impressions', 'clicks', 'conversions', 'reach', 'landing_page_views', 'add_to_cart', 'purchases']:
        if col in df.columns:
            agg_dict[col] = 'sum'

    grouped: pd.DataFrame = df.groupby(group_col).agg(agg_dict)

    for col in ['spend_inr', 'budget_inr', 'impressions', 'clicks', 'conversions', 'reach', 'landing_page_views', 'add_to_cart', 'purchases']:
        if col not in grouped.columns:
            grouped[col] = 0.0

    if 'roas' in df.columns:
        temp: pd.DataFrame = df.copy()
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

    total_spend: float = float(df['spend_inr'].sum()) if 'spend_inr' in df.columns else 0.0
    total_conversions: float = float(df['conversions'].sum()) if 'conversions' in df.columns else 0.0

    grouped['spend_share'] = (grouped['spend_inr'] / total_spend * 100.0).fillna(0.0) if total_spend > 0 else 0.0
    grouped['conversion_share'] = (grouped['conversions'] / total_conversions * 100.0).fillna(0.0) if total_conversions > 0 else 0.0

    grouped = add_performance_scores(grouped)

    # Add classifications
    classes: List[str] = []
    efficiencies: List[str] = []
    for idx, row in grouped.iterrows():
        classes.append(classify_performance_majority(row, account_kpis))
        efficiencies.append(classify_budget_efficiency(float(row['spend_share']), float(row['conversion_share'])))

    grouped['performance_class'] = classes
    grouped['budget_efficiency'] = efficiencies

    return grouped


def analyze_audience(df: pd.DataFrame, account_kpis: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Perform demographic audience analysis.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.
    account_kpis : Optional[Dict[str, float]], optional
        Global account KPIs.

    Returns
    -------
    Dict[str, Any]
        Demographic report dictionary containing gender_analysis, age_analysis, best_audience, and worst_audience.
    """
    logger.info("Executing audience demographic analysis across %d records", len(df))

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

    gender_df: pd.DataFrame = pd.DataFrame()
    age_df: pd.DataFrame = pd.DataFrame()

    if 'gender' in df.columns:
        gender_df = _aggregate_audience(df, 'gender', account_kpis)

    if 'age_group' in df.columns:
        age_df = _aggregate_audience(df, 'age_group', account_kpis)

    best_audience: Dict[str, Any] = {
        'highest_roas_age': str(age_df['roas'].idxmax()) if not age_df.empty else None,
        'highest_cvr_age': str(age_df['conversion_rate'].idxmax()) if not age_df.empty else None,
        'highest_ctr_age': str(age_df['ctr'].idxmax()) if not age_df.empty else None,
        'lowest_cpc_age': str(age_df['cpc'].replace(0, np.nan).idxmin()) if not age_df.empty else None,
        'highest_roas_gender': str(gender_df['roas'].idxmax()) if not gender_df.empty else None,
        'highest_cvr_gender': str(gender_df['conversion_rate'].idxmax()) if not gender_df.empty else None,
        'highest_ctr_gender': str(gender_df['ctr'].idxmax()) if not gender_df.empty else None,
        'lowest_cpc_gender': str(gender_df['cpc'].replace(0, np.nan).idxmin()) if not gender_df.empty else None
    }

    worst_audience: Dict[str, Any] = {
        'lowest_roas_age': str(age_df['roas'].idxmin()) if not age_df.empty else None,
        'lowest_cvr_age': str(age_df['conversion_rate'].idxmin()) if not age_df.empty else None,
        'lowest_roas_gender': str(gender_df['roas'].idxmin()) if not gender_df.empty else None,
        'lowest_cvr_gender': str(gender_df['conversion_rate'].idxmin()) if not gender_df.empty else None
    }

    logger.info("Audience demographic analysis completed successfully")

    return {
        'gender_analysis': gender_df.to_dict(orient='index') if not gender_df.empty else {},
        'age_analysis': age_df.to_dict(orient='index') if not age_df.empty else {},
        'best_audience': best_audience,
        'worst_audience': worst_audience
    }
