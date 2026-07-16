"""Module for cleaning and standardizing canonicalized campaign data.
"""

import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the campaign DataFrame.

    Operations performed:
    - Strip whitespace from column headers
    - Parse date column to datetime.date
    - Remove duplicate rows
    - Remove rows with future dates
    - Remove rows with logically impossible values (e.g. negative spend, clicks > impressions)
    - Convert integer columns to float64 for consistency
    - Fill missing campaign names with 'Unknown'
    - Fill missing numeric values with 0

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with canonical column names.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame copy.
    """
    logger.info("Cleaning campaign data. Rows before: %d", len(df))
    cleaned_df = df.copy()

    # Strip column names
    cleaned_df.columns = cleaned_df.columns.str.strip()

    # Parse date column
    if 'date' in cleaned_df.columns:
        cleaned_df['date'] = pd.to_datetime(cleaned_df['date'], format='%Y-%m-%d', errors='coerce').dt.date

    # Drop duplicate rows
    row_count_before = len(cleaned_df)
    cleaned_df.drop_duplicates(inplace=True)
    duplicate_rows_removed = row_count_before - len(cleaned_df)
    if duplicate_rows_removed > 0:
        logger.warning("Removed %d duplicate rows during cleaning", duplicate_rows_removed)

    # Filter out future dates
    if 'date' in cleaned_df.columns:
        today = datetime.today().date()
        future_date_filter = cleaned_df['date'].apply(lambda x: pd.to_datetime(x).date() if pd.notna(x) else None) > today
        future_rows_count = future_date_filter.sum()
        if future_rows_count > 0:
            logger.warning("Filtering out %d rows with future dates", future_rows_count)
            cleaned_df = cleaned_df[~future_date_filter]

    # Filter out logically impossible numeric values
    numeric_checks = []
    
    # 1. Negative values check
    for col in ['spend_inr', 'budget_inr', 'clicks', 'impressions', 'conversions', 'reach']:
        if col in cleaned_df.columns:
            numeric_checks.append(cleaned_df[col] < 0)

    # 2. Clicks > Impressions
    if 'clicks' in cleaned_df.columns and 'impressions' in cleaned_df.columns:
        numeric_checks.append(cleaned_df['clicks'] > cleaned_df['impressions'])

    # 3. Conversions > Clicks
    if 'conversions' in cleaned_df.columns and 'clicks' in cleaned_df.columns:
        numeric_checks.append(cleaned_df['conversions'] > cleaned_df['clicks'])

    # 4. Reach > Impressions
    if 'reach' in cleaned_df.columns and 'impressions' in cleaned_df.columns:
        numeric_checks.append(cleaned_df['reach'] > cleaned_df['impressions'])

    if numeric_checks:
        impossible_filter = pd.concat(numeric_checks, axis=1).any(axis=1)
        impossible_rows_count = impossible_filter.sum()
        if impossible_rows_count > 0:
            logger.warning("Filtering out %d rows with impossible numeric relationships", impossible_rows_count)
            cleaned_df = cleaned_df[~impossible_filter]

    # Fill missing values
    if 'campaign_name' in cleaned_df.columns:
        cleaned_df['campaign_name'] = cleaned_df['campaign_name'].fillna('Unknown')
    
    for col in ['spend_inr', 'impressions', 'budget_inr', 'clicks', 'conversions', 'reach']:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].fillna(0)

    # Standardize data types
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == "int64":
            cleaned_df[col] = cleaned_df[col].astype("float64")

    logger.info("Cleaning complete. Rows after: %d", len(cleaned_df))
    return cleaned_df
