"""Structural validation module for integrity checks like row counts and completeness.

Inspects DataFrame shape, row count thresholds, and null completeness across mandatory and optional fields.
"""

import pandas as pd
import logging
from typing import Dict, Any, List

# Module-level logger for structural validation operations
logger: logging.Logger = logging.getLogger(__name__)


def validate_structure(df: pd.DataFrame, schema_report: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the structural integrity of the DataFrame.

    Checks:
    - DataFrame is non-empty
    - Minimum row count threshold (>= 10 rows recommended)
    - Mandatory columns contain non-null entries (not all-null)
    - Identifies empty optional columns

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.
    schema_report : Dict[str, Any]
        Output report from schema_validator detailing available column sets.

    Returns
    -------
    Dict[str, Any]
        Structural validation report dictionary.
    """
    logger.info("Executing structural validation on dataset containing %d rows", len(df))
    report: Dict[str, Any] = {
        'is_empty': False,
        'low_row_count': False,
        'empty_mandatory_columns': [],
        'empty_optional_columns': [],
        'is_valid': True
    }

    if df.empty:
        report['is_empty'] = True
        report['is_valid'] = False
        logger.warning("Structural validation failed: DataFrame is completely empty (0 rows)")
        return report

    row_count: int = len(df.index)
    if row_count < 10:
        report['low_row_count'] = True
        logger.warning("Low row count warning: DataFrame has fewer than 10 rows (%d rows)", row_count)

    # Mandatory Columns Validator
    empty_mandatory: List[str] = []
    for col in schema_report.get('available_mandatory', []):
        if col in df.columns and df[col].isna().all():
            empty_mandatory.append(col)
            report['is_valid'] = False
            logger.warning("Mandatory column '%s' is completely empty (100%% null)", col)
    report['empty_mandatory_columns'] = empty_mandatory

    # Optional Columns Validator
    empty_optional: List[str] = []
    for col in schema_report.get('available_optional', []):
        if col in df.columns and df[col].isna().all():
            empty_optional.append(col)
            logger.warning("Optional column '%s' is completely empty (100%% null)", col)
    report['empty_optional_columns'] = empty_optional

    return report
