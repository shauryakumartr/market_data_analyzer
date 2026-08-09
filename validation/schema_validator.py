"""Schema validation module for verifying the presence of required and optional columns.

Evaluates DataFrame columns against mandatory, optional, and derived column sets
defined in platform settings to generate a schema compliance report.
"""

import pandas as pd
import logging
from typing import Dict, Any, Set
from config.settings import MANDATORY_COLUMNS, OPTIONAL_COLUMNS, DERIVED_COLUMNS

# Module-level logger for schema validation operations
logger: logging.Logger = logging.getLogger(__name__)


def validate_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate that the DataFrame contains required columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.

    Returns
    -------
    Dict[str, Any]
        Schema validation report detailing available/missing mandatory, optional, and derived fields.
    """
    logger.info("Starting schema validation on dataset with %d total columns", len(df.columns))
    columns: Set[str] = set(df.columns)
    
    missing_mandatory: Set[str] = MANDATORY_COLUMNS - columns
    available_mandatory: Set[str] = MANDATORY_COLUMNS.intersection(columns)
    
    missing_optional: Set[str] = OPTIONAL_COLUMNS - columns
    available_optional: Set[str] = OPTIONAL_COLUMNS.intersection(columns)
    
    missing_derived: Set[str] = DERIVED_COLUMNS - columns
    available_derived: Set[str] = DERIVED_COLUMNS.intersection(columns)

    if missing_mandatory:
        logger.warning("Missing mandatory columns detected: %s", missing_mandatory)
    if missing_optional:
        logger.warning("Missing optional columns detected: %s", missing_optional)

    is_valid: bool = (len(missing_mandatory) == 0)

    return {
        'available_mandatory': available_mandatory,
        'missing_mandatory': missing_mandatory,
        'available_optional': available_optional,
        'missing_optional': missing_optional,
        'available_derived': available_derived,
        'missing_derived': missing_derived,
        'is_valid': is_valid
    }
