"""Module for validating user-uploaded derived metrics against system-calculated values.

Performs row-by-row comparisons of uploaded CTR, CPC, and CVR values against system recalculations,
flagging relative discrepancies that exceed specified tolerance thresholds.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List

# Module-level logger for derived metric validation operations
logger: logging.Logger = logging.getLogger(__name__)


def validate_derived_metrics(df: pd.DataFrame, relative_tolerance: float = 0.01) -> Dict[str, Any]:
    """Compare user-uploaded derived metrics to system-calculated values.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with canonical column names.
    relative_tolerance : float, default=0.01
        Maximum allowed difference (1%) before flagging a discrepancy warning.

    Returns
    -------
    Dict[str, Any]
        Derived metric validation report containing:
        - 'discrepancies': Dict[str, List[Dict[str, Any]]] (discrepant records per metric)
        - 'has_discrepancies': bool
        - 'is_valid': bool (Always True, discrepancies produce warnings rather than fatal errors)
    """
    logger.info("Executing derived metrics validation with relative tolerance = %.2f%%", relative_tolerance * 100.0)
    discrepancies: Dict[str, List[Dict[str, Any]]] = {
        'ctr': [],
        'cpc': [],
        'cvr': []
    }

    # 1. CTR Comparison
    if 'ctr_pct' in df.columns and 'clicks' in df.columns and 'impressions' in df.columns:
        ctr_series: pd.Series = pd.to_numeric(df['ctr_pct'], errors='coerce')
        clicks_series: pd.Series = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)
        impressions_series: pd.Series = pd.to_numeric(df['impressions'], errors='coerce').fillna(0)
        
        max_ctr: float = float(ctr_series.max()) if not ctr_series.empty else 0.0
        user_factor: float = 100.0 if (pd.notna(max_ctr) and max_ctr <= 1.0) else 1.0
        
        for idx, row in df.iterrows():
            clicks: float = float(clicks_series.loc[idx]) if idx in clicks_series else 0.0
            impressions: float = float(impressions_series.loc[idx]) if idx in impressions_series else 0.0
            raw_ctr: Any = ctr_series.loc[idx] if idx in ctr_series else 0.0
            uploaded_ctr: float = float(raw_ctr) * user_factor if pd.notna(raw_ctr) else 0.0
            
            derived_ctr: float = (clicks / impressions * 100.0) if impressions > 0 else 0.0
            
            abs_diff: float = abs(uploaded_ctr - derived_ctr)
            rel_diff: float = (abs_diff / derived_ctr) if derived_ctr > 0 else abs_diff
                
            if abs_diff > 0.05 and rel_diff > relative_tolerance:
                discrepancies['ctr'].append({
                    'row_index': int(idx),
                    'campaign_name': str(row.get('campaign_name', 'Unknown')),
                    'uploaded': round(float(raw_ctr), 4) if pd.notna(raw_ctr) else 0.0,
                    'derived': round(derived_ctr / user_factor, 4),
                    'diff_pct': round(rel_diff * 100, 2)
                })

    # 2. CPC Comparison
    if 'cpc_inr' in df.columns and 'spend_inr' in df.columns and 'clicks' in df.columns:
        cpc_series: pd.Series = pd.to_numeric(df['cpc_inr'], errors='coerce')
        spend_series: pd.Series = pd.to_numeric(df['spend_inr'], errors='coerce').fillna(0)
        clicks_series: pd.Series = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)

        for idx, row in df.iterrows():
            clicks: float = float(clicks_series.loc[idx]) if idx in clicks_series else 0.0
            spend: float = float(spend_series.loc[idx]) if idx in spend_series else 0.0
            raw_cpc: Any = cpc_series.loc[idx] if idx in cpc_series else 0.0
            uploaded_cpc: float = float(raw_cpc) if pd.notna(raw_cpc) else 0.0
            
            derived_cpc: float = (spend / clicks) if clicks > 0 else 0.0
            
            abs_diff: float = abs(uploaded_cpc - derived_cpc)
            rel_diff: float = (abs_diff / derived_cpc) if derived_cpc > 0 else abs_diff
                
            if abs_diff > 1.0 and rel_diff > relative_tolerance:
                discrepancies['cpc'].append({
                    'row_index': int(idx),
                    'campaign_name': str(row.get('campaign_name', 'Unknown')),
                    'uploaded': round(uploaded_cpc, 2),
                    'derived': round(derived_cpc, 2),
                    'diff_pct': round(rel_diff * 100, 2)
                })

    # 3. Conversion Rate Comparison
    if 'conversion_rate_pct' in df.columns and 'conversions' in df.columns and 'clicks' in df.columns:
        cvr_series: pd.Series = pd.to_numeric(df['conversion_rate_pct'], errors='coerce')
        conv_series: pd.Series = pd.to_numeric(df['conversions'], errors='coerce').fillna(0)
        clicks_series: pd.Series = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)

        max_cvr: float = float(cvr_series.max()) if not cvr_series.empty else 0.0
        user_factor: float = 100.0 if (pd.notna(max_cvr) and max_cvr <= 1.0) else 1.0

        for idx, row in df.iterrows():
            clicks: float = float(clicks_series.loc[idx]) if idx in clicks_series else 0.0
            conversions: float = float(conv_series.loc[idx]) if idx in conv_series else 0.0
            raw_cvr: Any = cvr_series.loc[idx] if idx in cvr_series else 0.0
            uploaded_cvr: float = float(raw_cvr) * user_factor if pd.notna(raw_cvr) else 0.0
            
            derived_cvr: float = (conversions / clicks * 100.0) if clicks > 0 else 0.0
            
            abs_diff: float = abs(uploaded_cvr - derived_cvr)
            rel_diff: float = (abs_diff / derived_cvr) if derived_cvr > 0 else abs_diff
                
            if abs_diff > 0.05 and rel_diff > relative_tolerance:
                discrepancies['cvr'].append({
                    'row_index': int(idx),
                    'campaign_name': str(row.get('campaign_name', 'Unknown')),
                    'uploaded': round(float(raw_cvr), 4) if pd.notna(raw_cvr) else 0.0,
                    'derived': round(derived_cvr / user_factor, 4),
                    'diff_pct': round(rel_diff * 100, 2)
                })

    has_discrepancy: bool = any(len(v) > 0 for v in discrepancies.values())
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
