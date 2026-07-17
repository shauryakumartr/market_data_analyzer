"""Schema validation module for verifying the presence of required and optional columns.
"""

import pandas as pd
import logging
from config.settings import MANDATORY_COLUMNS, OPTIONAL_COLUMNS, DERIVED_COLUMNS

logger = logging.getLogger(__name__)

def validate_schema(df: pd.DataFrame) -> dict:
    """Validate that the DataFrame contains required columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.

    Returns
    -------
    dict
        Schema validation report.
    """
    logger.info("Starting schema validation")
    columns = set(df.columns)
    
    missing_mandatory = MANDATORY_COLUMNS - columns
    available_mandatory = MANDATORY_COLUMNS.intersection(columns)
    
    missing_optional = OPTIONAL_COLUMNS - columns
    available_optional = OPTIONAL_COLUMNS.intersection(columns)
    
    missing_derived = DERIVED_COLUMNS - columns
    available_derived = DERIVED_COLUMNS.intersection(columns)

    if missing_mandatory:
        logger.warning("Missing mandatory columns found: %s", missing_mandatory)
    if missing_optional:
        logger.warning("Missing optional columns found: %s", missing_optional)

    is_valid = (len(missing_mandatory) == 0)

    return {
        'available_mandatory': available_mandatory,
        'missing_mandatory': missing_mandatory,
        'available_optional': available_optional,
        'missing_optional': missing_optional,
        'available_derived': available_derived,
        'missing_derived': missing_derived,
        'is_valid': is_valid
    }
