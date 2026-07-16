"""Main orchestrator for data validation pipelines.
"""

import pandas as pd
import logging
from validation.schema_validator import validate_schema
from validation.structural_validator import validate_structure

logger = logging.getLogger(__name__)

def run_validation(df: pd.DataFrame) -> dict:
    """Run the full validation pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.

    Returns
    -------
    dict
        Combined validation report.
    """
    logger.info("Starting combined validation pipeline")
    
    schema_report = validate_schema(df)
    struct_report = validate_structure(df, schema_report)
    
    is_valid = schema_report['is_valid'] and struct_report['is_valid']
    
    logger.info("Combined validation pipeline completed. Combined Validity: %s", is_valid)
    
    return {
        'schema': schema_report,
        'structure': struct_report,
        'is_valid': is_valid
    }
