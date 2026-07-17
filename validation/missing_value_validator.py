"""Module for validating missing data within canonical campaign columns.
"""

import pandas as pd
import logging
from config.settings import MANDATORY_COLUMNS

logger = logging.getLogger(__name__)

def validate_missing_values(df: pd.DataFrame) -> dict:
    """Check columns and rows for missing data.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with canonical column names.

    Returns
    -------
    dict
        Missing value validation report containing:
        - 'missing_pct_per_column': dict[str, float]
        - 'completely_empty_columns': list[str]
        - 'rows_excessive_missing_idx': list[int]
        - 'missing_mandatory_columns': list[str]
        - 'is_valid': bool (False if any mandatory columns have missing values)
    """
    logger.info("Starting missing value validation")
    
    # Calculate missing percentage per column
    missing_pct = (df.isna().sum() / len(df) * 100).to_dict() if len(df) > 0 else {}
    
    # Find completely empty columns
    empty_cols = [col for col, pct in missing_pct.items() if pct == 100.0]
    
    # Find rows with excessive missing values (> 50% of the columns in the dataframe)
    threshold = len(df.columns) / 2.0
    excessive_missing_rows = df[df.isna().sum(axis=1) > threshold].index.tolist()
    
    # Check if mandatory columns have any missing value
    missing_mandatory = []
    for col in MANDATORY_COLUMNS:
        if col in df.columns:
            if df[col].isna().any():
                missing_mandatory.append(col)
        else:
            missing_mandatory.append(col)

    is_valid = len(missing_mandatory) == 0

    if not is_valid:
        logger.warning("Mandatory columns contain missing values: %s", missing_mandatory)
    if empty_cols:
        logger.warning("Completely empty columns detected: %s", empty_cols)
    if excessive_missing_rows:
        logger.warning("Detected %d rows with excessive (>50%%) missing values", len(excessive_missing_rows))

    return {
        'missing_pct_per_column': missing_pct,
        'completely_empty_columns': empty_cols,
        'rows_excessive_missing_idx': excessive_missing_rows,
        'missing_mandatory_columns': missing_mandatory,
        'is_valid': is_valid
    }
