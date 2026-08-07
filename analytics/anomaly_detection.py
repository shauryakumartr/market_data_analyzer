"""Module for comprehensive statistical and business logic anomaly detection.
"""

import pandas as pd
import numpy as np
import logging
from typing import Any

logger = logging.getLogger(__name__)

def detect_anomalies(df: pd.DataFrame) -> dict[str, Any]:
    """Inspect campaign dataset for performance anomalies across Spend, CTR, CPC, CPM, CVR, ROAS, Delivery, and Funnel.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.

    Returns
    -------
    dict[str, Any]
        Dictionary containing critical, warnings, minor lists, categories dict, and index_map.
    """
    logger.info("Executing comprehensive statistical anomaly detection")

    critical = []
    warnings = []
    minor = []

    categories = {
        'spend': [],
        'ctr': [],
        'cpc': [],
        'cpm': [],
        'conversion_rate': [],
        'roas': [],
        'conversions': [],
        'efficiency': [],
        'delivery': [],
        'funnel': [],
        'outliers': []
    }

    if df.empty:
        return {
            'critical': critical,
            'warnings': warnings,
            'minor': minor,
            'categories': categories,
            'index_map': {
                'Spend greater than budget': pd.Index([]),
                'Conversion without clicks': pd.Index([]),
                'Missing campaign name': pd.Index([]),
                'Missing spend inr': pd.Index([]),
                'Missing impressions': pd.Index([])
            }
        }

    # Helper for upper/lower IQR bounds
    def get_bounds(series: pd.Series):
        s = pd.to_numeric(series, errors='coerce').dropna()
        if len(s) < 3:
            return s.mean() - 2*s.std(), s.mean() + 2*s.std()
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        return q1 - 1.5 * iqr, q3 + 1.5 * iqr

    # Gather metrics bounds
    spend_low, spend_high = get_bounds(df['spend_inr']) if 'spend_inr' in df.columns else (0, 0)
    ctr_low, ctr_high = get_bounds(df['ctr_pct']) if 'ctr_pct' in df.columns else (0, 0)
    cpc_low, cpc_high = get_bounds(df['cpc_inr']) if 'cpc_inr' in df.columns else (0, 0)
    cvr_low, cvr_high = get_bounds(df['conversion_rate_pct']) if 'conversion_rate_pct' in df.columns else (0, 0)

    cpm_series = (df['spend_inr'] / df['impressions'] * 1000.0).fillna(0.0) if 'spend_inr' in df.columns and 'impressions' in df.columns else pd.Series(0.0, index=df.index)
    cpm_low, cpm_high = get_bounds(cpm_series)

    roas_low, roas_high = get_bounds(df['roas']) if 'roas' in df.columns else (0, 0)

    mean_ctr = df['ctr_pct'].mean() if 'ctr_pct' in df.columns else 0.0
    mean_cvr = df['conversion_rate_pct'].mean() if 'conversion_rate_pct' in df.columns else 0.0
    mean_spend = df['spend_inr'].mean() if 'spend_inr' in df.columns else 0.0

    total_spend = df['spend_inr'].sum() if 'spend_inr' in df.columns else 0.0
    total_conversions = df['conversions'].sum() if 'conversions' in df.columns else 0.0

    # Legacy index arrays
    spend_exceeded_idx = []
    conv_without_clicks_idx = []
    missing_campaign_idx = []
    missing_spend_idx = []
    missing_impressions_idx = []

    for idx, row in df.iterrows():
        name = row.get('campaign_name', 'Unknown')
        date_str = str(row.get('date', 'N/A'))
        spend = float(row.get('spend_inr', 0.0))
        budget = float(row.get('budget_inr', 0.0))
        clicks = float(row.get('clicks', 0.0))
        impressions = float(row.get('impressions', 0.0))
        reach = float(row.get('reach', 0.0))
        conversions = float(row.get('conversions', 0.0))
        ctr = float(row.get('ctr_pct', 0.0))
        cpc = float(row.get('cpc_inr', 0.0))
        cpm = float(cpm_series.loc[idx]) if idx in cpm_series.index else 0.0
        roas = float(row.get('roas', 0.0)) if 'roas' in row else 0.0
        frequency = float(row.get('frequency', 0.0)) if 'frequency' in row else 1.0

        lpv = float(row.get('landing_page_views', clicks * 0.85))
        atc = float(row.get('add_to_cart', lpv * 0.15))
        purchases = float(row.get('purchases', atc * 0.4))

        spend_sh = (spend / total_spend * 100.0) if total_spend > 0 else 0.0
        conv_sh = (conversions / total_conversions * 100.0) if total_conversions > 0 else 0.0
        cvr = (conversions / clicks * 100.0) if clicks > 0 else 0.0

        # Legacy index checks
        if name == 'Unknown':
            missing_campaign_idx.append(int(idx))
        if spend == 0:
            missing_spend_idx.append(int(idx))
        if impressions == 0:
            missing_impressions_idx.append(int(idx))
        if budget > 0 and spend > budget:
            spend_exceeded_idx.append(int(idx))
        if conversions > 0 and clicks == 0:
            conv_without_clicks_idx.append(int(idx))

        # Helper to log item
        def add_item(severity, cat, issue, details):
            item = {'row_index': int(idx), 'campaign_name': name, 'date': date_str, 'issue': issue, 'details': details}
            if severity == 'critical': critical.append(item)
            elif severity == 'warning': warnings.append(item)
            else: minor.append(item)
            if cat in categories: categories[cat].append(item)

        # 1. SPEND ANOMALIES
        if budget > 0 and spend > budget:
            add_item('critical', 'spend', 'Budget Exceeded', f"Spent ₹{spend:,.2f} on a budget of ₹{budget:,.2f}.")
        if spend > (mean_spend * 3.0) and spend > 2000:
            add_item('critical', 'spend', 'Spend Spike', f"Spent ₹{spend:,.2f} (3x higher than average ₹{mean_spend:,.2f}).")
        elif spend == 0:
            add_item('minor', 'spend', 'Zero Spend', "Campaign active with 0 spend.")

        # 2. CTR ANOMALIES
        if impressions > 500 and clicks == 0:
            add_item('critical', 'ctr', 'Zero CTR / CTR Collapse', f"Received {int(impressions):,} impressions but 0 clicks.")
        elif impressions > 100 and ctr < 0.2:
            add_item('warning', 'ctr', 'Extremely Low CTR', f"CTR is {ctr:.2f}% (well below healthy threshold).")
        elif ctr > 15.0 and impressions > 100:
            add_item('minor', 'ctr', 'Extremely High CTR', f"CTR reached {ctr:.2f}% (unusually high).")

        # 3. CPC & CPM ANOMALIES
        if cpc > cpc_high and cpc > 50.0:
            add_item('warning', 'cpc', 'CPC Spike', f"CPC spiked to ₹{cpc:.2f} (upper bound: ₹{cpc_high:.2f}).")
        if cpm > cpm_high and cpm > 200.0:
            add_item('warning', 'cpm', 'CPM Spike', f"CPM reached ₹{cpm:.2f} (upper bound: ₹{cpm_high:.2f}).")

        # 4. CONVERSION RATE & ROAS ANOMALIES
        if spend > 1500.0 and conversions == 0:
            add_item('critical', 'efficiency', 'High Spend + Zero Conversions', f"Spent ₹{spend:,.2f} with 0 conversions.")
        if roas_low > 0 and roas < roas_low and spend > 500:
            add_item('critical', 'roas', 'ROAS Collapse', f"ROAS dropped to {roas:.2f} (below acceptable threshold {roas_low:.2f}).")

        # 5. DELIVERY & FREQUENCY ANOMALIES
        if impressions == 0:
            add_item('minor', 'delivery', 'Zero Impressions', "Campaign registered 0 impressions.")
        if reach == 0 and impressions > 0:
            add_item('minor', 'delivery', 'Zero Reach', "Impressions logged with zero reach.")
        if frequency > 4.0:
            add_item('minor', 'delivery', 'Frequency Too High (Ad Fatigue)', f"Frequency reached {frequency:.2f}. Users seeing ads too often.")

        # 6. FUNNEL ANOMALIES
        if clicks > 50 and lpv < (clicks * 0.4):
            add_item('warning', 'funnel', 'High Clicks + Low Landing Page Views', f"{int(clicks)} clicks but only {int(lpv)} views. Slow site load potential.")
        if ctr > (mean_ctr + 1.0) and cvr < 0.5 and clicks > 50:
            add_item('minor', 'funnel', 'High CTR + Low Conversion Rate', f"High interest ({ctr:.2f}% CTR) but low landing page conversions ({cvr:.2f}% CVR).")

    return {
        'critical': critical,
        'warnings': warnings,
        'minor': minor,
        'categories': categories,
        'index_map': {
            'Spend greater than budget': pd.Index(spend_exceeded_idx),
            'Conversion without clicks': pd.Index(conv_without_clicks_idx),
            'Missing campaign name': pd.Index(missing_campaign_idx),
            'Missing spend inr': pd.Index(missing_spend_idx),
            'Missing impressions': pd.Index(missing_impressions_idx)
        }
    }
