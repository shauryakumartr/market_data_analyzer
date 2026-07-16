"""Duplicate mapping validation module.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_no_duplicate_mappings(column_mapping: dict[str, str | None]) -> dict:
    """Check that no two columns are mapped to the same canonical name.

    Ignores columns mapped to None, 'Ignore Column', or 'Custom Column'.

    Parameters
    ----------
    column_mapping : dict[str, str | None]
        The user-confirmed column mapping.

    Returns
    -------
    dict
        Duplicate validation report.
    """
    logger.info("Starting duplicate mapping validation")
    ignore = {None, "Ignore Column", "Custom Column"}
    mapped_canonical = []
    
    for original_col, canonical_col in column_mapping.items():
        if canonical_col not in ignore:
            mapped_canonical.append(canonical_col)

    mapped_series = pd.Series(mapped_canonical)
    duplicates = mapped_series[mapped_series.duplicated()].unique().tolist()
    
    is_valid = len(duplicates) == 0
    if not is_valid:
        logger.warning("Duplicate column mappings detected: %s", duplicates)

    return {
        'is_valid': is_valid,
        'duplicate_mappings': duplicates
    }
