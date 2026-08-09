"""Module for validating duplicate rows across the entire dataset.

Identifies completely duplicated rows and returns index references and duplicate row subsets.
"""

import pandas as pd
import logging
from typing import Dict, Any, List

# Module-level logger for duplicate row validation operations
logger: logging.Logger = logging.getLogger(__name__)


def validate_duplicate_rows(df: pd.DataFrame) -> Dict[str, Any]:
    """Find rows that are completely identical to another row.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.

    Returns
    -------
    Dict[str, Any]
        Duplicate row validation report containing:
        - 'duplicate_row_count': int
        - 'duplicate_row_indexes': List[int]
        - 'duplicate_rows_data': pd.DataFrame
        - 'is_valid': bool (Always True, duplicates generate non-blocking warnings)
    """
    logger.info("Executing duplicate row validation across %d rows", len(df))
    
    # Identify completely duplicated rows (excluding first occurrence)
    duplicates_mask: pd.Series = df.duplicated(keep='first')
    duplicate_indexes: List[int] = df[duplicates_mask].index.tolist()
    duplicate_rows_df: pd.DataFrame = df[duplicates_mask]
    duplicate_count: int = len(duplicate_indexes)

    if duplicate_count > 0:
        logger.warning("Detected %d completely duplicated rows in dataset", duplicate_count)

    return {
        'duplicate_row_count': duplicate_count,
        'duplicate_row_indexes': duplicate_indexes,
        'duplicate_rows_data': duplicate_rows_df,
        'is_valid': True
    }
