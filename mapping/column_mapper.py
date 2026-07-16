"""Module to map uploaded raw columns to standardized, canonical column names.
"""

import pandas as pd
import logging
from config.settings import COLUMN_ALIASES

logger = logging.getLogger(__name__)

def map_columns(df: pd.DataFrame) -> dict[str, str | None]:
    """Map uploaded DataFrame columns to canonical column names.

    Normalizes column names (lowercase, strip, replace spaces with underscores)
    then attempts to match each against known aliases.

    Parameters
    ----------
    df : pd.DataFrame
        Raw uploaded DataFrame.

    Returns
    -------
    dict[str, str | None]
        Mapping from original column name -> canonical name (or None if unrecognized).
    """
    logger.info("Starting column mapping prediction")
    mapping = {}
    normalized_cols = list(df.columns.str.strip().str.lower().str.replace(" ", "_"))

    for original_col, normalized_col in zip(df.columns, normalized_cols):
        mapping[original_col] = None
        for canonical_name, aliases in COLUMN_ALIASES.items():
            if normalized_col in aliases:
                mapping[original_col] = canonical_name
                break

        if mapping[original_col] is None:
            logger.warning("Unmapped raw column found: %s (Normalized as: %s)", original_col, normalized_col)
        else:
            logger.info("Mapped: %s -> %s", original_col, mapping[original_col])

    return mapping
