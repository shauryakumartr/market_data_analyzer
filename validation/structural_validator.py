"""Structural validation module for integrity checks like row counts and completeness.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_structure(df: pd.DataFrame, schema_report: dict) -> dict:
    """Validate the structural integrity of the DataFrame.

    Checks:
    - DataFrame is not empty
    - Minimum row count (>= 10)
    - Mandatory columns contain data (not all-null)

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.
    schema_report : dict
        Output from schema_validator.

    Returns
    -------
    dict
        Structural validation report.
    """
    logger.info("Starting structural validation")
    report = {
        'is_empty': False,
        'low_row_count': False,
        'empty_mandatory_columns': [],
        'empty_optional_columns': [],
        'is_valid': True
    }

    if df.empty:
        report['is_empty'] = True
        report['is_valid'] = False
        logger.warning("DataFrame is empty")
        return report

    if len(df.index) < 10:
        report['low_row_count'] = True
        logger.warning("DataFrame has less than 10 rows (%d rows)", len(df.index))

    # Mandatory Columns Validator
    for col in schema_report.get('available_mandatory', []):
        if col in df.columns and df[col].isna().all():
            report['empty_mandatory_columns'].append(col)
            report['is_valid'] = False
            logger.warning("Mandatory column '%s' is completely empty (all nulls)", col)

    # Optional Columns Validator
    for col in schema_report.get('available_optional', []):
        if col in df.columns and df[col].isna().all():
            report['empty_optional_columns'].append(col)
            logger.warning("Optional column '%s' is completely empty (all nulls)", col)

    return report
