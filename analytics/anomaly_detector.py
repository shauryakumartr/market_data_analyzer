"""Module for detecting business logic anomalies in marketing data.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def detect_anomalies(df: pd.DataFrame) -> dict[str, pd.Index]:
    """Detect business-logic anomalies in the campaign data.

    Parameters
    ----------
    df : pd.DataFrame
        Campaign DataFrame.

    Returns
    -------
    dict[str, pd.Index]
        Mapping of anomaly type to index of affected rows.
    """
    logger.info("Detecting data anomalies")
    anomalies = {
        'Spend greater than budget': pd.Index([]),
        'Conversion without clicks': pd.Index([]),
        'Missing campaign name': pd.Index([]),
        'Missing spend inr': pd.Index([]),
        'Missing impressions': pd.Index([]),
    }

    if df.empty:
        return anomalies

    try:
        # 1. Spend greater than budget
        if 'spend_inr' in df.columns and 'budget_inr' in df.columns:
            anomalies['Spend greater than budget'] = df[df['spend_inr'] > df['budget_inr']].index

        # 2. Conversions without clicks
        if 'conversions' in df.columns and 'clicks' in df.columns:
            anomalies['Conversion without clicks'] = df[(df['conversions'] > 0) & (df['clicks'] == 0)].index

        # 3. Missing campaign name
        if 'campaign_name' in df.columns:
            anomalies['Missing campaign name'] = df[df['campaign_name'] == 'Unknown'].index

        # 4. Missing spend inr
        if 'spend_inr' in df.columns:
            anomalies['Missing spend inr'] = df[df['spend_inr'] == 0].index

        # 5. Missing impressions
        if 'impressions' in df.columns:
            anomalies['Missing impressions'] = df[df['impressions'] == 0].index

        # Log findings
        for k, idx in anomalies.items():
            if len(idx) > 0:
                logger.warning("Detected %d instances of anomaly: %s", len(idx), k)

    except Exception as e:
        logger.error("Error encountered in anomaly detection: %s", e)

    return anomalies
