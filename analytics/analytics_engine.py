"""Main orchestrator for running the campaign analytics pipeline.
"""

import pandas as pd
import logging
from typing import Any

from analytics.kpi import calculate_account_kpis
from analytics.campaign_analysis import analyze_campaigns
from analytics.audience_analysis import analyze_audience
from analytics.device_analysis import analyze_devices
from analytics.objective_analysis import analyze_objectives
from analytics.time_analysis import analyze_time
from analytics.funnel_analysis import analyze_funnel
from analytics.anomaly_detection import detect_anomalies
from insights.insight_engine import generate_business_insights
from insights.recommendation_engine import generate_action_recommendations

logger: logging.Logger = logging.getLogger(__name__)


def run_analytics_pipeline(
    df: pd.DataFrame,
    metric_choice: str = "Calculated Metrics (Recommended)"
) -> dict[str, Any]:
    """Orchestrate and execute the complete analytics pipeline against the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign DataFrame.
    metric_choice : str, optional
        Derived metric calculation source ("Calculated Metrics (Recommended)" or "Uploaded Metrics").

    Returns
    -------
    dict[str, Any]
        Combined analytics report containing all sub-reports.
    """
    logger.info("Executing main analytics orchestrator pipeline with metric_choice='%s'", metric_choice)
    df_analytics: pd.DataFrame = df.copy()

    # Derived metrics selection logic handled inside analytics module
    if metric_choice == "Calculated Metrics (Recommended)":
        if 'clicks' in df_analytics.columns and 'impressions' in df_analytics.columns:
            df_analytics['ctr_pct'] = (df_analytics['clicks'] / df_analytics['impressions'].replace(0, float('nan'))).fillna(0.0) * 100.0
        else:
            df_analytics['ctr_pct'] = 0.0

        if 'spend_inr' in df_analytics.columns and 'clicks' in df_analytics.columns:
            df_analytics['cpc_inr'] = (df_analytics['spend_inr'] / df_analytics['clicks'].replace(0, float('nan'))).fillna(0.0)
        else:
            df_analytics['cpc_inr'] = 0.0

        if 'conversions' in df_analytics.columns and 'clicks' in df_analytics.columns:
            df_analytics['conversion_rate_pct'] = (df_analytics['conversions'] / df_analytics['clicks'].replace(0, float('nan'))).fillna(0.0) * 100.0
        else:
            df_analytics['conversion_rate_pct'] = 0.0
    else:
        # Normalize uploaded percentage columns (0-1) for system consistency if > 1.0
        for pct_col in ['ctr_pct', 'conversion_rate_pct']:
            if pct_col in df_analytics.columns:
                max_val = df_analytics[pct_col].max()
                if max_val > 1.0:
                    df_analytics[pct_col] = df_analytics[pct_col] / 100.0

    # 1. Account KPIs
    kpi_report: dict[str, float] = calculate_account_kpis(df_analytics)

    # 2. Entity Analyses (passing account_kpis for relative comparisons)
    campaign_report: dict[str, Any] = analyze_campaigns(df_analytics, kpi_report)
    audience_report: dict[str, Any] = analyze_audience(df_analytics, kpi_report)
    device_report: dict[str, Any] = analyze_devices(df_analytics, kpi_report)
    objective_report: dict[str, Any] = analyze_objectives(df_analytics, kpi_report)
    time_report: dict[str, Any] = analyze_time(df_analytics)
    funnel_report: dict[str, Any] = analyze_funnel(df_analytics)

    # Compile raw analytics data
    raw_analytics: dict[str, Any] = {
        'kpis': kpi_report,
        'campaigns': campaign_report,
        'audience': audience_report,
        'devices': device_report,
        'objectives': objective_report,
        'time': time_report,
        'funnel': funnel_report
    }

    # 3. Anomaly Detection
    anomaly_report: dict[str, Any] = detect_anomalies(df_analytics)
    raw_analytics['anomalies'] = anomaly_report

    # 4. Insight Engine (Facts with business meaning only, NO recommendations, NO AI)
    insights_report: dict[str, Any] = generate_business_insights(raw_analytics)

    # 5. Recommendation Engine (Deterministic recommendations categorized by priority)
    recommendation_report: dict[str, Any] = generate_action_recommendations(
        insights=insights_report,
        anomalies=anomaly_report,
        analytics=raw_analytics
    )

    logger.info("Analytics pipeline execution complete successfully")

    return {
        'kpis': kpi_report,
        'campaigns': campaign_report,
        'audience': audience_report,
        'devices': device_report,
        'objectives': objective_report,
        'time': time_report,
        'funnel': funnel_report,
        'anomalies': anomaly_report,
        'insights': insights_report,
        'recommendations': recommendation_report
    }
