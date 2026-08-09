"""Main orchestrator for running all validation pipelines.

Executes schema checks, structural integrity verification, missing value audits,
duplicate row detection, business logic invariants, and derived metric comparisons.
"""

import pandas as pd
import logging
from typing import Dict, Any

from validation.schema_validator import validate_schema
from validation.structural_validator import validate_structure
from validation.missing_value_validator import validate_missing_values
from validation.duplicate_row_validator import validate_duplicate_rows
from validation.business_logic_validator import validate_business_logic
from validation.derived_metric_validator import validate_derived_metrics

# Module-level logger for validation pipeline orchestration
logger: logging.Logger = logging.getLogger(__name__)


def run_validation(df: pd.DataFrame) -> Dict[str, Any]:
    """Run the complete suite of validators against the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame to validate.

    Returns
    -------
    Dict[str, Any]
        Combined validation report containing sub-reports and overall validity flag.
    """
    logger.info("Initiating run_validation orchestrator pipeline across %d records", len(df))

    schema_report: Dict[str, Any] = validate_schema(df)
    
    # Structural validator requires schema report to check empty mandatory/optional cols
    struct_report: Dict[str, Any] = validate_structure(df, schema_report)
    
    missing_report: Dict[str, Any] = validate_missing_values(df)
    duplicate_report: Dict[str, Any] = validate_duplicate_rows(df)
    business_report: Dict[str, Any] = validate_business_logic(df)
    derived_report: Dict[str, Any] = validate_derived_metrics(df)

    # Calculate overall validity status
    # Note: Duplicates and Derived Metrics discrepancy warnings do not fail the run,
    # but missing mandatory values and business logic violations do.
    is_valid: bool = (
        schema_report.get('is_valid', True) and
        struct_report.get('is_valid', True) and
        missing_report.get('is_valid', True) and
        business_report.get('is_valid', True)
    )

    logger.info("Validation pipeline execution complete. Overall Validity: %s", is_valid)

    return {
        'schema': schema_report,
        'structure': struct_report,
        'missing': missing_report,
        'duplicates': duplicate_report,
        'business_logic': business_report,
        'derived_metrics': derived_report,
        'is_valid': is_valid
    }
