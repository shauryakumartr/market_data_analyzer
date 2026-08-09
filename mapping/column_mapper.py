"""Module to map uploaded raw columns to standardized, canonical column names.

Uses alias matching strategies against predefined alias dictionaries in settings
to automatically predict and map raw header columns to canonical database schema keys.
"""

import pandas as pd
import logging
from typing import Dict, Optional, List
from config.settings import COLUMN_ALIASES

# Module-level logger for column mapping prediction
logger: logging.Logger = logging.getLogger(__name__)


def map_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """Map uploaded DataFrame columns to canonical column names.

    Normalizes column headers (lowercasing, stripping whitespace, substituting spaces with underscores)
    and evaluates each against canonical column alias lists.

    Parameters
    ----------
    df : pd.DataFrame
        Raw uploaded DataFrame containing unstandardized headers.

    Returns
    -------
    Dict[str, Optional[str]]
        Mapping dictionary of original column name -> predicted canonical name (or None if unmapped).
    """
    logger.info("Initiating automatic column header mapping prediction across %d columns", len(df.columns))
    mapping: Dict[str, Optional[str]] = {}
    normalized_cols: List[str] = list(df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_"))

    for original_col, normalized_col in zip(df.columns, normalized_cols):
        mapped_target: Optional[str] = None
        for canonical_name, aliases in COLUMN_ALIASES.items():
            if normalized_col in aliases:
                mapped_target = canonical_name
                break

        mapping[original_col] = mapped_target

        if mapped_target is None:
            logger.warning("Unmapped raw column detected: '%s' (Normalized string: '%s')", original_col, normalized_col)
        else:
            logger.info("Successfully matched raw header '%s' -> canonical name '%s'", original_col, mapped_target)

    return mapping
