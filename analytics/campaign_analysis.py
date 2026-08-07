"""Module for campaign-specific analysis and performance classification.
"""

import pandas as pd
import numpy as np
import logging
from typing import Any
from analytics.utils import (
    safe_divide,
    add_performance_scores,
    classify_performance_majority,
    classify_budget_efficiency,
    classify_opportunity,
    classify_risk
)

logger = logging.getLogger(__name__)

def analyze_campaigns(df: pd.DataFrame, account_kpis: dict = None) -> dict[str, Any]:
    """Perform comprehensive marketing analyst analysis on campaigns.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.
    account_kpis : dict, optional
        Global account KPIs for relative comparison.

    Returns
    -------
    dict[str, Any]
        Campaign analysis results.
    """
    logger.info("Executing comprehensive campaign-level analysis")

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
    agg_dict = {
        'spend_inr': 'sum',
        'budget_inr': 'sum',
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum',
        'reach': 'sum'
    }

    # Optional columns aggregation if present
    for col in ['landing_page_views', 'add_to_cart', 'purchases']:
        if col in df.columns:
            agg_dict[col] = 'sum'

    grouped = df.groupby('campaign_name').agg(agg_dict)

    # Add missing optional columns if not present
    for col in ['landing_page_views', 'add_to_cart', 'purchases']:
        if col not in grouped.columns:
            grouped[col] = 0.0

    # Calculate ROAS revenue
    if 'roas' in df.columns:
        temp_df = df.copy()
        temp_df['revenue'] = temp_df['roas'] * temp_df['spend_inr']
        grouped['revenue'] = temp_df.groupby('campaign_name')['revenue'].sum()
    else:
        grouped['revenue'] = 0.0

    # Derived rates
    grouped['ctr'] = (grouped['clicks'] / grouped['impressions'] * 100.0).fillna(0.0)
    grouped['cpc'] = (grouped['spend_inr'] / grouped['clicks']).fillna(0.0)
    grouped['cpm'] = (grouped['spend_inr'] / grouped['impressions'] * 1000.0).fillna(0.0)
    grouped['roas'] = (grouped['revenue'] / grouped['spend_inr']).fillna(0.0)
    grouped['conversion_rate'] = (grouped['conversions'] / grouped['clicks'] * 100.0).fillna(0.0)
    grouped['cost_per_conversion'] = (grouped['spend_inr'] / grouped['conversions']).fillna(0.0)

    # Share calculations
    total_spend = grouped['spend_inr'].sum()
    total_conversions = grouped['conversions'].sum()

    grouped['spend_share'] = (grouped['spend_inr'] / total_spend * 100.0).fillna(0.0) if total_spend > 0 else 0.0
    grouped['conversion_share'] = (grouped['conversions'] / total_conversions * 100.0).fillna(0.0) if total_conversions > 0 else 0.0

    # Add performance score & tier
    grouped = add_performance_scores(grouped)

    # Compute Quartiles across campaigns
    quartiles = {}
    for metric in ['spend_inr', 'ctr', 'cpc', 'cpm', 'conversion_rate', 'cost_per_conversion', 'roas', 'performance_score']:
        if metric in grouped.columns and len(grouped) > 0:
            s = pd.to_numeric(grouped[metric], errors='coerce').fillna(0.0)
            quartiles[metric] = {
                'mean': float(s.mean()),
                'median': float(s.median()),
                'q1': float(s.quantile(0.25)),
                'q3': float(s.quantile(0.75))
            }

    # Classifications per campaign
    efficiency = {}
    opportunity = {}
    risk = {}
    majority_classifications = {}

    high_performers = []
    low_performers = []
    average_performers = []

    for name, row in grouped.iterrows():
        # Budget Efficiency
        eff = classify_budget_efficiency(row['spend_share'], row['conversion_share'])
        efficiency[name] = {
            'status': eff,
            'spend_share': float(row['spend_share']),
            'conversion_share': float(row['conversion_share'])
        }

        # Opportunity & Risk
        opportunity[name] = classify_opportunity(row, account_kpis)
        risk[name] = classify_risk(row, account_kpis)

        # Performance majority classification
        cls = classify_performance_majority(row, account_kpis)
        majority_classifications[name] = cls

        if cls == "High Performer":
            high_performers.append(name)
        elif cls == "Low Performer":
            low_performers.append(name)
        else:
            average_performers.append(name)

    # Fallback to prevent empty High/Low performer lists if rules are too strict
    if not high_performers and not grouped.empty:
        # Take top 25% by performance score or highest score campaign
        top_by_score = grouped.sort_values(by='performance_score', ascending=False).head(max(1, len(grouped) // 4))
        high_performers = list(top_by_score.index)

    if not low_performers and not grouped.empty:
        bot_by_score = grouped.sort_values(by='performance_score', ascending=True).head(max(1, len(grouped) // 4))
        low_performers = [c for c in list(bot_by_score.index) if c not in high_performers]

    # Store classifications back into grouped dataframe columns
    grouped['performance_class'] = [majority_classifications.get(n, 'Average Performer') for n in grouped.index]
    grouped['budget_efficiency'] = [efficiency.get(n, {}).get('status', 'Balanced') for n in grouped.index]
    grouped['opportunity_tier'] = [opportunity.get(n, 'Low Opportunity') for n in grouped.index]
    grouped['risk_tier'] = [risk.get(n, 'Low Risk') for n in grouped.index]

    # Top 5 and Bottom 5 Rankings
    top_5_score = list(grouped.sort_values(by='performance_score', ascending=False).head(5).index)
    bot_5_score = list(grouped.sort_values(by='performance_score', ascending=True).head(5).index)

    top_5_roas = list(grouped.sort_values(by='roas', ascending=False).head(5).index)
    bot_5_roas = list(grouped.sort_values(by='roas', ascending=True).head(5).index)

    top_5_cvr = list(grouped.sort_values(by='conversion_rate', ascending=False).head(5).index)
    bot_5_cvr = list(grouped.sort_values(by='conversion_rate', ascending=True).head(5).index)

    top_campaigns = {
        'highest_score': {'name': top_5_score[0] if top_5_score else None, 'value': float(grouped.loc[top_5_score[0], 'performance_score']) if top_5_score else 0.0},
        'highest_ctr': {'name': grouped['ctr'].idxmax() if not grouped.empty else None, 'value': float(grouped['ctr'].max()) if not grouped.empty else 0.0},
        'highest_roas': {'name': top_5_roas[0] if top_5_roas else None, 'value': float(grouped.loc[top_5_roas[0], 'roas']) if top_5_roas else 0.0},
        'highest_spend': {'name': grouped['spend_inr'].idxmax() if not grouped.empty else None, 'value': float(grouped['spend_inr'].max()) if not grouped.empty else 0.0},
        'highest_conversion_rate': {'name': top_5_cvr[0] if top_5_cvr else None, 'value': float(grouped.loc[top_5_cvr[0], 'conversion_rate']) if top_5_cvr else 0.0}
    }

    bottom_campaigns = {
        'lowest_score': {'name': bot_5_score[0] if bot_5_score else None, 'value': float(grouped.loc[bot_5_score[0], 'performance_score']) if bot_5_score else 0.0},
        'lowest_ctr': {'name': grouped['ctr'].idxmin() if not grouped.empty else None, 'value': float(grouped['ctr'].min()) if not grouped.empty else 0.0},
        'lowest_spend': {'name': grouped['spend_inr'].idxmin() if not grouped.empty else None, 'value': float(grouped['spend_inr'].min()) if not grouped.empty else 0.0}
    }

    rankings = {
        'top_5_score': top_5_score,
        'bot_5_score': bot_5_score,
        'top_5_roas': top_5_roas,
        'bot_5_roas': bot_5_roas,
        'top_5_cvr': top_5_cvr,
        'bot_5_cvr': bot_5_cvr
    }

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
