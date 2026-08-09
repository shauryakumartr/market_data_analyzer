"""Module for campaign-specific analysis and performance classification.

Aggregates performance metrics at the individual campaign level, evaluates relative performance scores,
determines performance tiers (High, Average, Low performers), computes budget efficiency ratios, and ranks campaigns.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from analytics.utils import (
    safe_divide,
    add_performance_scores,
    classify_performance_majority,
    classify_budget_efficiency,
    classify_opportunity,
    classify_risk
)

# Module-level logger for campaign-level analytics
logger: logging.Logger = logging.getLogger(__name__)


def analyze_campaigns(df: pd.DataFrame, account_kpis: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Perform comprehensive marketing analyst analysis on campaigns.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.
    account_kpis : Optional[Dict[str, float]], optional
        Global account KPIs for relative comparison benchmarks.

    Returns
    -------
    Dict[str, Any]
        Campaign analysis results containing metrics dictionary, rankings, top/bottom performers,
        quartiles, and efficiency status.
    """
    logger.info("Executing comprehensive campaign-level analysis across %d records", len(df))

    if account_kpis is None:
        account_kpis = {}

    if df.empty or 'campaign_name' not in df.columns:
        logger.warning("Empty DataFrame or missing campaign_name column in analyze_campaigns")
        return {
            'campaign_metrics': {},
            'top_campaigns': {},
            'bottom_campaigns': {},
            'high_performers': [],
            'low_performers': [],
            'average_performers': [],
            'rankings': {},
            'efficiency': {},
            'quartiles': {}
        }

    # Base aggregations per campaign
    agg_dict: Dict[str, str] = {}
    for col in ['spend_inr', 'budget_inr', 'impressions', 'clicks', 'conversions', 'reach', 'landing_page_views', 'add_to_cart', 'purchases']:
        if col in df.columns:
            agg_dict[col] = 'sum'

    grouped: pd.DataFrame = df.groupby('campaign_name').agg(agg_dict)

    # Add missing columns if not present
    for col in ['spend_inr', 'budget_inr', 'impressions', 'clicks', 'conversions', 'reach', 'landing_page_views', 'add_to_cart', 'purchases']:
        if col not in grouped.columns:
            grouped[col] = 0.0

    # Calculate ROAS revenue
    if 'roas' in df.columns:
        temp_df: pd.DataFrame = df.copy()
        temp_df['revenue'] = temp_df['roas'] * temp_df['spend_inr']
        grouped['revenue'] = temp_df.groupby('campaign_name')['revenue'].sum()
    else:
        grouped['revenue'] = 0.0

    total_account_spend: float = float(account_kpis.get('spend', grouped['spend_inr'].sum()))
    total_account_conv: float = float(account_kpis.get('conversions', grouped['conversions'].sum()))

    # Calculate derived rate metrics per campaign
    grouped['ctr'] = (grouped['clicks'] / grouped['impressions'] * 100.0).fillna(0.0)
    grouped['cpc'] = (grouped['spend_inr'] / grouped['clicks']).fillna(0.0)
    grouped['cpm'] = (grouped['spend_inr'] / grouped['impressions'] * 1000.0).fillna(0.0)
    grouped['conversion_rate'] = (grouped['conversions'] / grouped['clicks'] * 100.0).fillna(0.0)
    grouped['cost_per_conversion'] = (grouped['spend_inr'] / grouped['conversions']).fillna(0.0)
    grouped['roas'] = (grouped['revenue'] / grouped['spend_inr']).fillna(0.0)
    grouped['spend_share'] = (grouped['spend_inr'] / total_account_spend * 100.0).fillna(0.0) if total_account_spend > 0 else 0.0
    grouped['conversion_share'] = (grouped['conversions'] / total_account_conv * 100.0).fillna(0.0) if total_account_conv > 0 else 0.0

    # Performance Scoring (0-100)
    grouped = add_performance_scores(grouped)

    # Performance Classification & Quartiles
    high_performers: List[str] = []
    low_performers: List[str] = []
    average_performers: List[str] = []
    efficiency: Dict[str, Dict[str, Any]] = {}
    opportunity: Dict[str, str] = {}
    risk: Dict[str, str] = {}

    for name, row in grouped.iterrows():
        tier: str = classify_performance_majority(row, account_kpis)
        eff_status: str = classify_budget_efficiency(float(row['spend_share']), float(row['conversion_share']))
        opp_tier: str = classify_opportunity(row, account_kpis)
        rsk_tier: str = classify_risk(row, account_kpis)

        if tier == "High Performer":
            high_performers.append(str(name))
        elif tier == "Low Performer":
            low_performers.append(str(name))
        else:
            average_performers.append(str(name))

        efficiency[str(name)] = {
            'status': eff_status,
            'spend_share': float(row['spend_share']),
            'conversion_share': float(row['conversion_share'])
        }
        opportunity[str(name)] = opp_tier
        risk[str(name)] = rsk_tier

    # Fallback to top 25% by performance score if majority classification returns empty
    if not high_performers and not grouped.empty:
        q75: float = float(grouped['performance_score'].quantile(0.75))
        high_performers = list(grouped[grouped['performance_score'] >= q75].index)

    if not low_performers and not grouped.empty:
        q25: float = float(grouped['performance_score'].quantile(0.25))
        low_performers = list(grouped[grouped['performance_score'] <= q25].index)

    quartiles: Dict[str, Any] = {
        'score_q25': float(grouped['performance_score'].quantile(0.25)) if not grouped.empty else 0.0,
        'score_q50': float(grouped['performance_score'].median()) if not grouped.empty else 0.0,
        'score_q75': float(grouped['performance_score'].quantile(0.75)) if not grouped.empty else 0.0,
        'ctr_median': float(grouped['ctr'].median()) if not grouped.empty else 0.0,
        'cpc_median': float(grouped['cpc'].median()) if not grouped.empty else 0.0,
        'roas_median': float(grouped['roas'].median()) if not grouped.empty else 0.0
    }

    grouped['performance_majority'] = [
        "High Performer" if n in high_performers else ("Low Performer" if n in low_performers else "Average Performer")
        for n in grouped.index
    ]
    grouped['budget_efficiency'] = [efficiency.get(str(n), {}).get('status', 'Balanced') for n in grouped.index]
    grouped['opportunity_tier'] = [opportunity.get(str(n), 'Low Opportunity') for n in grouped.index]
    grouped['risk_tier'] = [risk.get(str(n), 'Low Risk') for n in grouped.index]

    # Top 5 and Bottom 5 Rankings
    top_5_score: List[str] = list(grouped.sort_values(by='performance_score', ascending=False).head(5).index)
    bot_5_score: List[str] = list(grouped.sort_values(by='performance_score', ascending=True).head(5).index)

    top_5_roas: List[str] = list(grouped.sort_values(by='roas', ascending=False).head(5).index)
    bot_5_roas: List[str] = list(grouped.sort_values(by='roas', ascending=True).head(5).index)

    top_5_cvr: List[str] = list(grouped.sort_values(by='conversion_rate', ascending=False).head(5).index)
    bot_5_cvr: List[str] = list(grouped.sort_values(by='conversion_rate', ascending=True).head(5).index)

    top_campaigns: Dict[str, Any] = {
        'highest_score': {'name': top_5_score[0] if top_5_score else None, 'value': float(grouped.loc[top_5_score[0], 'performance_score']) if top_5_score else 0.0},
        'highest_ctr': {'name': str(grouped['ctr'].idxmax()) if not grouped.empty else None, 'value': float(grouped['ctr'].max()) if not grouped.empty else 0.0},
        'highest_roas': {'name': top_5_roas[0] if top_5_roas else None, 'value': float(grouped.loc[top_5_roas[0], 'roas']) if top_5_roas else 0.0},
        'highest_spend': {'name': str(grouped['spend_inr'].idxmax()) if not grouped.empty else None, 'value': float(grouped['spend_inr'].max()) if not grouped.empty else 0.0},
        'highest_conversion_rate': {'name': top_5_cvr[0] if top_5_cvr else None, 'value': float(grouped.loc[top_5_cvr[0], 'conversion_rate']) if top_5_cvr else 0.0}
    }

    bottom_campaigns: Dict[str, Any] = {
        'lowest_score': {'name': bot_5_score[0] if bot_5_score else None, 'value': float(grouped.loc[bot_5_score[0], 'performance_score']) if bot_5_score else 0.0},
        'lowest_ctr': {'name': str(grouped['ctr'].idxmin()) if not grouped.empty else None, 'value': float(grouped['ctr'].min()) if not grouped.empty else 0.0},
        'lowest_spend': {'name': str(grouped['spend_inr'].idxmin()) if not grouped.empty else None, 'value': float(grouped['spend_inr'].min()) if not grouped.empty else 0.0}
    }

    rankings: Dict[str, List[str]] = {
        'top_5_score': top_5_score,
        'bot_5_score': bot_5_score,
        'top_5_roas': top_5_roas,
        'bot_5_roas': bot_5_roas,
        'top_5_cvr': top_5_cvr,
        'bot_5_cvr': bot_5_cvr
    }

    logger.info("Campaign-level analysis completed successfully (%d high, %d low performers)", len(high_performers), len(low_performers))

    return {
        'campaign_metrics': grouped.to_dict(orient='index'),
        'top_campaigns': top_campaigns,
        'bottom_campaigns': bottom_campaigns,
        'high_performers': high_performers,
        'low_performers': low_performers,
        'average_performers': average_performers,
        'rankings': rankings,
        'efficiency': efficiency,
        'quartiles': quartiles
    }
