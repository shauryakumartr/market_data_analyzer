"""Data filtering module to select segments or date ranges of campaign data.
"""

import pandas as pd
import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def filter_data(
    df: pd.DataFrame,
    campaign_objective: str = "All",
    devices: Optional[list[str]] = None,
    genders: Optional[list[str]] = None,
    age_groups: Optional[list[str]] = None,
    campaign_names: Optional[list[str]] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Apply user-selected filters to the campaign DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign data.
    campaign_objective : str
        Campaign objective to filter by. "All" means no filter.
    devices, genders, age_groups, campaign_names : list[str] or None
        Multi-select filter values. None or empty list means no filter.
    start_date, end_date : datetime.date or None
        Date range boundaries. None means no date filter.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame copy.
    """
    logger.info("Applying filters. Original row count: %d", len(df))
    filtered_df = df.copy()

    # Filter by Campaign Objective
    if campaign_objective != "All":
        filtered_df = filtered_df[filtered_df['objective'] == campaign_objective]

    # Filter by Device
    if devices:
        filtered_df = filtered_df[filtered_df['device'].isin(devices)]

    # Filter by Gender
    if genders:
        filtered_df = filtered_df[filtered_df['gender'].isin(genders)]

    # Filter by Age Group
    if age_groups:
        filtered_df = filtered_df[filtered_df['age_group'].isin(age_groups)]

    # Filter by Campaign Name
    if campaign_names:
        filtered_df = filtered_df[filtered_df['campaign_name'].isin(campaign_names)]

    # Filter by Date Range
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]

    logger.info("Filtering complete. Resulting row count: %d", len(filtered_df))
    return filtered_df
