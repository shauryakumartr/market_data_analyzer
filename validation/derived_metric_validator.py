"""Module for validating user-uploaded derived metrics against system-calculated values.
"""

import pandas as pd
import numpy as np
import logging
from typing import Any

logger = logging.getLogger(__name__)

def validate_derived_metrics(df: pd.DataFrame, relative_tolerance: float = 0.01) -> dict:
    """Compare user-uploaded derived metrics to system-calculated values.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with canonical column names.
    relative_tolerance : float, default 0.01
        Maximum allowed difference (1%) before flagging a discrepancy warning.

    Returns
    -------
    dict
        Derived metric validation report containing:
        - 'discrepancies': dict[str, list[dict[str, Any]]] (discrepant records with keys: 'row_index', 'campaign', 'uploaded', 'derived', 'diff_pct')
        - 'is_valid': bool (Always True, discrepancies are warnings, not fatal errors)
    """
    logger.info("Starting derived metrics validation")
    discrepancies = {
        'ctr': [],
        'cpc': [],
        'cvr': []
    }

    # 1. CTR Comparison
    if 'ctr_pct' in df.columns and 'clicks' in df.columns and 'impressions' in df.columns:
        # Determine if user's ctr_pct is normalized (0-1) or percentage (0-100)
        max_ctr = df['ctr_pct'].max()
        user_factor = 100.0 if max_ctr <= 1.0 else 1.0
        
        for idx, row in df.iterrows():
            clicks = row['clicks']
            impressions = row['impressions']
            uploaded_ctr = row['ctr_pct'] * user_factor if pd.notna(row['ctr_pct']) else 0.0
            
            derived_ctr = (clicks / impressions * 100.0) if impressions > 0 else 0.0
            
            # Check relative and absolute difference
            abs_diff = abs(uploaded_ctr - derived_ctr)
            if derived_ctr > 0:
                rel_diff = abs_diff / derived_ctr
            else:
                rel_diff = abs_diff
                
            if abs_diff > 0.05 and rel_diff > relative_tolerance:
                discrepancies['ctr'].append({
                    'row_index': int(idx),
                    'campaign_name': row.get('campaign_name', 'Unknown'),
                    'uploaded': round(row['ctr_pct'], 4),
                    'derived': round(derived_ctr / user_factor, 4),
                    'diff_pct': round(rel_diff * 100, 2)
                })

    # 2. CPC Comparison
    if 'cpc_inr' in df.columns and 'spend_inr' in df.columns and 'clicks' in df.columns:
        for idx, row in df.iterrows():
            clicks = row['clicks']
            spend = row['spend_inr']
            uploaded_cpc = row['cpc_inr'] if pd.notna(row['cpc_inr']) else 0.0
            
            derived_cpc = (spend / clicks) if clicks > 0 else 0.0
            
            abs_diff = abs(uploaded_cpc - derived_cpc)
            if derived_cpc > 0:
                rel_diff = abs_diff / derived_cpc
            else:
                rel_diff = abs_diff
                
            if abs_diff > 1.0 and rel_diff > relative_tolerance:
                discrepancies['cpc'].append({
                    'row_index': int(idx),
                    'campaign_name': row.get('campaign_name', 'Unknown'),
                    'uploaded': round(uploaded_cpc, 2),
                    'derived': round(derived_cpc, 2),
                    'diff_pct': round(rel_diff * 100, 2)
                })

    # 3. Conversion Rate Comparison
    if 'conversion_rate_pct' in df.columns and 'conversions' in df.columns and 'clicks' in df.columns:
        max_cvr = df['conversion_rate_pct'].max()
        user_factor = 100.0 if max_cvr <= 1.0 else 1.0

        for idx, row in df.iterrows():
            clicks = row['clicks']
            conversions = row['conversions']
            uploaded_cvr = row['conversion_rate_pct'] * user_factor if pd.notna(row['conversion_rate_pct']) else 0.0
            
            derived_cvr = (conversions / clicks * 100.0) if clicks > 0 else 0.0
            
            abs_diff = abs(uploaded_cvr - derived_cvr)
            if derived_cvr > 0:
                rel_diff = abs_diff / derived_cvr
            else:
                rel_diff = abs_diff
                
            if abs_diff > 0.05 and rel_diff > relative_tolerance:
                discrepancies['cvr'].append({
                    'row_index': int(idx),
                    'campaign_name': row.get('campaign_name', 'Unknown'),
                    'uploaded': round(row['conversion_rate_pct'], 4),
                    'derived': round(derived_cvr / user_factor, 4),
                    'diff_pct': round(rel_diff * 100, 2)
                })

    has_discrepancy = any(len(v) > 0 for v in discrepancies.values())
    if has_discrepancy:
        logger.warning(
            "Derived metrics discrepancies detected: ctr=%d, cpc=%d, cvr=%d",
            len(discrepancies['ctr']), len(discrepancies['cpc']), len(discrepancies['cvr'])
        )

    return {
        'discrepancies': discrepancies,
        'has_discrepancies': has_discrepancy,
        'is_valid': True
    }
