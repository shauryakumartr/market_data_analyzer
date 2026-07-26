"""Module for validating duplicate rows across the entire dataset.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_duplicate_rows(df: pd.DataFrame) -> dict:
    """Find rows that are completely identical to another row.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.

    Returns
    -------
    dict
        Duplicate row validation report containing:
        - 'duplicate_row_count': int
        - 'duplicate_row_indexes': list[int]
        - 'is_valid': bool (Always True, duplicates do not block execution but generate warnings)
    """
    logger.info("Starting duplicate row validation")
    
    # Identify completely duplicated rows (excluding first occurrence)
    duplicates_mask = df.duplicated(keep='first')
    duplicate_indexes = df[duplicates_mask].index.tolist()
    duplicate_rows_df = df[duplicates_mask]
    duplicate_count = len(duplicate_indexes)

    if duplicate_count > 0:
        logger.warning("Detected %d completely duplicated rows in dataset", duplicate_count)

    return {
        'duplicate_row_count': duplicate_count,
        'duplicate_row_indexes': duplicate_indexes,
        'duplicate_rows_data': duplicate_rows_df,
        'is_valid': True
    }
