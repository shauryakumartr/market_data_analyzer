"""Data loading module to read raw campaign datasets.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def load_csv(file_or_path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame.

    Parameters
    ----------
    file_or_path : str or file-like
        Path to CSV file or an uploaded file-like object from Streamlit.

    Returns
    -------
    pd.DataFrame
        Loaded raw DataFrame.
    """
    logger.info("Loading CSV file")
    df = pd.read_csv(file_or_path)
    logger.info("CSV loaded successfully with %d rows and %d columns", len(df), len(df.columns))
    return df
