"""Duplicate mapping validation module.

Validates that no two raw columns in user mapping are assigned to the same canonical database field.
"""

import pandas as pd
import logging
from typing import Dict, Any, Optional, List, Set

# Module-level logger for mapping duplicate validation operations
logger: logging.Logger = logging.getLogger(__name__)


def validate_no_duplicate_mappings(column_mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """Check that no two columns are mapped to the same canonical name.

    Ignores columns mapped to None, 'Ignore Column', or 'Custom Column'.

    Parameters
    ----------
    column_mapping : Dict[str, Optional[str]]
        The user-confirmed column mapping dictionary.

    Returns
    -------
    Dict[str, Any]
        Duplicate mapping validation report detailing validity and any duplicated canonical fields.
    """
    logger.info("Executing duplicate mapping validation across %d mapped headers", len(column_mapping))
    ignore: Set[Optional[str]] = {None, "Ignore Column", "Custom Column"}
    mapped_canonical: List[str] = []
    
    for original_col, canonical_col in column_mapping.items():
        if canonical_col not in ignore and canonical_col is not None:
            mapped_canonical.append(canonical_col)

    mapped_series: pd.Series = pd.Series(mapped_canonical)
    duplicates: List[str] = mapped_series[mapped_series.duplicated()].unique().tolist()
    
    is_valid: bool = (len(duplicates) == 0)
    if not is_valid:
        logger.warning("Duplicate column mappings detected for canonical targets: %s", duplicates)

    return {
        'is_valid': is_valid,
        'duplicate_mappings': duplicates
    }
