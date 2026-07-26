"""Module for validating business logic rules and consistency of metrics.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_business_logic(df: pd.DataFrame) -> dict:
    """Validate that records conform to business logic rules.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with canonical column names.

    Returns
    -------
    dict
        Business logic validation report. Contains details of invalid row indexes per rule
        and an overall 'is_valid' status.
    """
    logger.info("Starting business logic validation")
    
    report = {
        'impressions_less_than_reach': [],
        'clicks_greater_than_impressions': [],
        'conversions_greater_than_clicks': [],
        'landing_page_views_greater_than_clicks': [],
        'negative_values': {},
        'ctr_pct_excessive': [],
        'is_valid': True
    }

    # 1. Impressions vs Reach
    if 'impressions' in df.columns and 'reach' in df.columns:
        imp = pd.to_numeric(df['impressions'], errors='coerce').fillna(0)
        rch = pd.to_numeric(df['reach'], errors='coerce').fillna(0)
        invalid_idx = df[imp < rch].index.tolist()
        if invalid_idx:
            report['impressions_less_than_reach'] = invalid_idx
            report['is_valid'] = False
            logger.warning("Business logic violation: reach > impressions in %d rows", len(invalid_idx))

    # 2. Clicks vs Impressions
    if 'clicks' in df.columns and 'impressions' in df.columns:
        clk = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)
        imp = pd.to_numeric(df['impressions'], errors='coerce').fillna(0)
        invalid_idx = df[clk > imp].index.tolist()
        if invalid_idx:
            report['clicks_greater_than_impressions'] = invalid_idx
            report['is_valid'] = False
            logger.warning("Business logic violation: clicks > impressions in %d rows", len(invalid_idx))

    # 3. Conversions vs Clicks
    if 'conversions' in df.columns and 'clicks' in df.columns:
        cnv = pd.to_numeric(df['conversions'], errors='coerce').fillna(0)
        clk = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)
        invalid_idx = df[cnv > clk].index.tolist()
        if invalid_idx:
            report['conversions_greater_than_clicks'] = invalid_idx
            report['is_valid'] = False
            logger.warning("Business logic violation: conversions > clicks in %d rows", len(invalid_idx))

    # 4. Landing Page Views vs Clicks
    if 'landing_page_views' in df.columns and 'clicks' in df.columns:
        lpv = pd.to_numeric(df['landing_page_views'], errors='coerce').fillna(0)
        clk = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)
        invalid_idx = df[lpv > clk].index.tolist()
        if invalid_idx:
            report['landing_page_views_greater_than_clicks'] = invalid_idx
            report['is_valid'] = False
            logger.warning("Business logic violation: landing_page_views > clicks in %d rows", len(invalid_idx))

    # 5. Negative values
    negative_fields = ['spend_inr', 'budget_inr', 'clicks', 'impressions', 'conversions', 'reach']
    for field in negative_fields:
        if field in df.columns:
            val = pd.to_numeric(df[field], errors='coerce').fillna(0)
            invalid_idx = df[val < 0].index.tolist()
            if invalid_idx:
                report['negative_values'][field] = invalid_idx
                report['is_valid'] = False
                logger.warning("Business logic violation: negative value in '%s' in %d rows", field, len(invalid_idx))

    # 6. CTR percentage bounds
    if 'ctr_pct' in df.columns:
        ctr = pd.to_numeric(df['ctr_pct'], errors='coerce').fillna(0)
        max_val = ctr.max() if not ctr.empty else 0.0
        limit = 100.0 if max_val > 1.0 else 1.0
        invalid_idx = df[ctr > limit].index.tolist()
        if invalid_idx:
            report['ctr_pct_excessive'] = invalid_idx
            report['is_valid'] = False
            logger.warning("Business logic violation: ctr_pct > %s in %d rows", limit, len(invalid_idx))

    return report
