"""Module for cleaning and standardizing canonicalized campaign data.

Executes data type coercion, string cleaning, integer-to-float conversions,
and percentage normalization prior to any metric calculations or validation.
"""

import pandas as pd
import numpy as np
import logging
import re
from datetime import datetime

logger: logging.Logger = logging.getLogger(__name__)

INTEGER_COUNT_COLUMNS: list[str] = [
    'impressions',
    'clicks',
    'conversions',
    'reach',
    'landing_page_views',
    'add_to_cart',
    'purchases',
]

NUMERIC_CURRENCY_COLUMNS: list[str] = [
    'spend_inr',
    'budget_inr',
    'cpc_inr',
    'cpm_inr',
    'cost_per_conversion_inr',
    'roas',
    'frequency',
]

PERCENTAGE_COLUMNS: list[str] = [
    'ctr_pct',
    'conversion_rate_pct',
]

STRING_CATEGORICAL_COLUMNS: list[str] = [
    'campaign_name',
    'platform',
    'ad_set_name',
    'objective',
    'result_type',
    'region',
    'age_group',
    'gender',
    'device',
    'creative_format',
    'cta',
]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the canonical campaign DataFrame.

    Operations performed prior to any metric calculations:
    - Strip header whitespace
    - Coerce date strings/timestamps to datetime.date objects
    - Clean currency symbols (₹, $, €), commas, and percentage signs (%) from string representations
    - Convert integer count columns (str -> int64 -> float64) to prevent data type errors
    - Convert currency/float columns to float64
    - Normalize percentage columns cleanly
    - Fill missing categorical fields with 'Unknown' and missing numerical fields with 0.0
    - Remove duplicate rows

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with canonical column names.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame copy ready for validation and analytics calculations.
    """
    logger.info("Initiating data cleaning pipeline. Initial dataset shape: (%d, %d)", len(df), len(df.columns))
    cleaned_df: pd.DataFrame = df.copy()

    # 1. Strip column header whitespace
    cleaned_df.columns = cleaned_df.columns.astype(str).str.strip()

    # 2. Flexible Date Parsing
    if 'date' in cleaned_df.columns:
        cleaned_df['date'] = pd.to_datetime(cleaned_df['date'], errors='coerce').dt.date

    # 3. Clean and coerce Integer Count Columns (str -> int -> float)
    for col in INTEGER_COUNT_COLUMNS:
        if col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                # Strip non-numeric characters except digits
                cleaned_df[col] = (
                    cleaned_df[col]
                    .astype(str)
                    .str.replace(r'[^\d.]', '', regex=True)
                    .str.strip()
                )
            # Convert to numeric, replace NaNs with 0, cast to int64 then float64
            numeric_series = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0)
            cleaned_df[col] = numeric_series.astype('int64').astype('float64')

    # 4. Clean and coerce Currency / Floating Point Columns
    for col in NUMERIC_CURRENCY_COLUMNS:
        if col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = (
                    cleaned_df[col]
                    .astype(str)
                    .str.replace(r'[₹$,€]', '', regex=True)
                    .str.strip()
                )
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0.0).astype('float64')

    # 5. Clean and normalize Percentage Columns (e.g. '5.2%', '0.052')
    for col in PERCENTAGE_COLUMNS:
        if col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = (
                    cleaned_df[col]
                    .astype(str)
                    .str.replace(r'[%]', '', regex=True)
                    .str.strip()
                )
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0.0).astype('float64')

    # 6. Clean Categorical String Columns
    for col in STRING_CATEGORICAL_COLUMNS:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            cleaned_df[col] = cleaned_df[col].replace(['nan', 'None', 'NaN', ''], np.nan).fillna('Unknown')

    # 7. Remove duplicate rows
    row_count_before: int = len(cleaned_df)
    cleaned_df.drop_duplicates(inplace=True)
    duplicate_rows_removed: int = row_count_before - len(cleaned_df)
    if duplicate_rows_removed > 0:
        logger.warning("Removed %d duplicate rows during data cleaning", duplicate_rows_removed)

    logger.info("Data cleaning completed successfully. Final dataset shape: (%d, %d)", len(cleaned_df), len(cleaned_df.columns))
    return cleaned_df
