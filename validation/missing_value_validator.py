"""Module for validating missing data within canonical campaign columns.

Calculates missing value percentages per column, flags empty columns and row indices exceeding
missing data thresholds, and validates complete data presence in mandatory fields.
"""

import pandas as pd
import logging
from typing import Dict, Any, List
from config.settings import MANDATORY_COLUMNS

# Module-level logger for missing value validation operations
logger: logging.Logger = logging.getLogger(__name__)


def validate_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Check columns and rows for missing data.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with canonical column names.

    Returns
    -------
    Dict[str, Any]
        Missing value validation report containing:
        - 'missing_pct_per_column': Dict[str, float]
        - 'completely_empty_columns': List[str]
        - 'rows_excessive_missing_idx': List[int]
        - 'missing_mandatory_columns': List[str]
        - 'is_valid': bool (False if any mandatory columns have missing values)
    """
    logger.info("Executing missing value validation across %d rows and %d columns", len(df), len(df.columns))
    
    # Calculate missing percentage per column
    missing_pct: Dict[str, float] = (df.isna().sum() / len(df) * 100.0).to_dict() if len(df) > 0 else {}
    
    # Find completely empty columns
    empty_cols: List[str] = [col for col, pct in missing_pct.items() if pct == 100.0]
    
    # Find rows with excessive missing values (> 50% of columns)
    threshold: float = len(df.columns) / 2.0
    excessive_missing_rows: List[int] = df[df.isna().sum(axis=1) > threshold].index.tolist()
    
    # Check if mandatory columns have any missing values
    missing_mandatory: List[str] = []
    for col in MANDATORY_COLUMNS:
        if col in df.columns:
            if df[col].isna().any():
                missing_mandatory.append(col)
        else:
            missing_mandatory.append(col)

    is_valid: bool = (len(missing_mandatory) == 0)

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
