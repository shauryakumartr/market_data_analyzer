"""Main orchestrator for running the campaign analytics pipeline.
"""

import pandas as pd
import logging

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

logger = logging.getLogger(__name__)

def run_analytics_pipeline(df: pd.DataFrame) -> dict:
    """Orchestrate and execute the complete analytics pipeline against the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered campaign DataFrame.

    Returns
    -------
    dict
        Combined analytics report containing all sub-reports.
    """
    logger.info("Executing main analytics orchestrator pipeline")

    # 1. Account KPIs
    kpi_report = calculate_account_kpis(df)

    # 2. Entity Analyses (passing account_kpis for relative comparisons)
    campaign_report = analyze_campaigns(df, kpi_report)
    audience_report = analyze_audience(df, kpi_report)
    device_report = analyze_devices(df, kpi_report)
    objective_report = analyze_objectives(df, kpi_report)
    time_report = analyze_time(df)
    funnel_report = analyze_funnel(df)

    # Compile raw analytics data
    raw_analytics = {
        'kpis': kpi_report,
        'campaigns': campaign_report,
        'audience': audience_report,
        'devices': device_report,
        'objectives': objective_report,
        'time': time_report,
        'funnel': funnel_report
    }

    # 3. Anomaly Detection
    anomaly_report = detect_anomalies(df)
    raw_analytics['anomalies'] = anomaly_report

    # 4. Insight Engine (Facts with business meaning only, NO recommendations, NO AI)
    insights_report = generate_business_insights(raw_analytics)

    # 5. Recommendation Engine (Deterministic recommendations categorized by priority)
    recommendation_report = generate_action_recommendations(
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
