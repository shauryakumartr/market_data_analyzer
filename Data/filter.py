"""Data filtering module to select segments or date ranges of campaign data.

Provides fast multi-dimensional indexing and filtering operations across
campaign dimensions (objective, device, demographic segments, campaign names, and date ranges).
"""

import pandas as pd
import datetime
import logging
from typing import Optional, List

# Module-level logger for filtering operations
logger: logging.Logger = logging.getLogger(__name__)


def filter_data(
    df: pd.DataFrame,
    campaign_objective: str = "All",
    devices: Optional[List[str]] = None,
    genders: Optional[List[str]] = None,
    age_groups: Optional[List[str]] = None,
    campaign_names: Optional[List[str]] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Apply user-selected filters to the campaign DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned campaign data.
    campaign_objective : str, default="All"
        Campaign objective to filter by. "All" disables objective filtering.
    devices : Optional[List[str]], optional
        Multi-select device values. None or empty list disables device filtering.
    genders : Optional[List[str]], optional
        Multi-select gender values. None or empty list disables gender filtering.
    age_groups : Optional[List[str]], optional
        Multi-select age group values. None or empty list disables age group filtering.
    campaign_names : Optional[List[str]], optional
        Multi-select campaign names. None or empty list disables campaign name filtering.
    start_date : Optional[datetime.date], optional
        Inclusive lower date boundary. None disables lower date boundary filtering.
    end_date : Optional[datetime.date], optional
        Inclusive upper date boundary. None disables upper date boundary filtering.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame copy.
    """
    initial_count: int = len(df)
    logger.info("Applying multi-dimensional dataset filters. Initial row count: %d", initial_count)
    filtered_df: pd.DataFrame = df.copy()

    # Filter by Campaign Objective
    if campaign_objective != "All" and 'objective' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['objective'] == campaign_objective]

    # Filter by Device
    if devices and 'device' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['device'].isin(devices)]

    # Filter by Gender
    if genders and 'gender' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['gender'].isin(genders)]

    # Filter by Age Group
    if age_groups and 'age_group' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['age_group'].isin(age_groups)]

    # Filter by Campaign Name
    if campaign_names and 'campaign_name' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['campaign_name'].isin(campaign_names)]

    # Filter by Date Range
    if start_date and end_date and 'date' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]

    final_count: int = len(filtered_df)
    logger.info("Filtering complete. Resulting row count: %d (Filtered out %d rows)", final_count, initial_count - final_count)
    return filtered_df
