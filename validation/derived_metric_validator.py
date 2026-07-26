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
        ctr_series = pd.to_numeric(df['ctr_pct'], errors='coerce')
        clicks_series = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)
        impressions_series = pd.to_numeric(df['impressions'], errors='coerce').fillna(0)
        
        max_ctr = ctr_series.max() if not ctr_series.empty else 0.0
        user_factor = 100.0 if (pd.notna(max_ctr) and max_ctr <= 1.0) else 1.0
        
        for idx, row in df.iterrows():
            clicks = float(clicks_series.loc[idx]) if idx in clicks_series else 0.0
            impressions = float(impressions_series.loc[idx]) if idx in impressions_series else 0.0
            raw_ctr = ctr_series.loc[idx] if idx in ctr_series else 0.0
            uploaded_ctr = float(raw_ctr) * user_factor if pd.notna(raw_ctr) else 0.0
            
            derived_ctr = (clicks / impressions * 100.0) if impressions > 0 else 0.0
            
            abs_diff = abs(uploaded_ctr - derived_ctr)
            rel_diff = (abs_diff / derived_ctr) if derived_ctr > 0 else abs_diff
                
            if abs_diff > 0.05 and rel_diff > relative_tolerance:
                discrepancies['ctr'].append({
                    'row_index': int(idx),
                    'campaign_name': row.get('campaign_name', 'Unknown'),
                    'uploaded': round(float(raw_ctr), 4) if pd.notna(raw_ctr) else 0.0,
                    'derived': round(derived_ctr / user_factor, 4),
                    'diff_pct': round(rel_diff * 100, 2)
                })

    # 2. CPC Comparison
    if 'cpc_inr' in df.columns and 'spend_inr' in df.columns and 'clicks' in df.columns:
        cpc_series = pd.to_numeric(df['cpc_inr'], errors='coerce')
        spend_series = pd.to_numeric(df['spend_inr'], errors='coerce').fillna(0)
        clicks_series = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)

        for idx, row in df.iterrows():
            clicks = float(clicks_series.loc[idx]) if idx in clicks_series else 0.0
            spend = float(spend_series.loc[idx]) if idx in spend_series else 0.0
            raw_cpc = cpc_series.loc[idx] if idx in cpc_series else 0.0
            uploaded_cpc = float(raw_cpc) if pd.notna(raw_cpc) else 0.0
            
            derived_cpc = (spend / clicks) if clicks > 0 else 0.0
            
            abs_diff = abs(uploaded_cpc - derived_cpc)
            rel_diff = (abs_diff / derived_cpc) if derived_cpc > 0 else abs_diff
                
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
        cvr_series = pd.to_numeric(df['conversion_rate_pct'], errors='coerce')
        conv_series = pd.to_numeric(df['conversions'], errors='coerce').fillna(0)
        clicks_series = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)

        max_cvr = cvr_series.max() if not cvr_series.empty else 0.0
        user_factor = 100.0 if (pd.notna(max_cvr) and max_cvr <= 1.0) else 1.0

        for idx, row in df.iterrows():
            clicks = float(clicks_series.loc[idx]) if idx in clicks_series else 0.0
            conversions = float(conv_series.loc[idx]) if idx in conv_series else 0.0
            raw_cvr = cvr_series.loc[idx] if idx in cvr_series else 0.0
            uploaded_cvr = float(raw_cvr) * user_factor if pd.notna(raw_cvr) else 0.0
            
            derived_cvr = (conversions / clicks * 100.0) if clicks > 0 else 0.0
            
            abs_diff = abs(uploaded_cvr - derived_cvr)
            rel_diff = (abs_diff / derived_cvr) if derived_cvr > 0 else abs_diff
                
            if abs_diff > 0.05 and rel_diff > relative_tolerance:
                discrepancies['cvr'].append({
                    'row_index': int(idx),
                    'campaign_name': row.get('campaign_name', 'Unknown'),
                    'uploaded': round(float(raw_cvr), 4) if pd.notna(raw_cvr) else 0.0,
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
