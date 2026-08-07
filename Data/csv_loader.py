"""CSV Data Loader Module.

This module provides dedicated CSV loading functionality for raw campaign datasets.
It handles file reading from both local file system paths and Streamlit file buffer streams,
incorporating robust error handling and structured logging.
"""

import logging
from typing import Union, BinaryIO, TextIO, Any
import pandas as pd

# Configure module-level logger for CSV loading operations
logger: logging.Logger = logging.getLogger(__name__)


def load_csv(file_or_path: Union[str, BinaryIO, TextIO, Any]) -> pd.DataFrame:
    """Load a CSV file or file-like buffer into a pandas DataFrame.

    Parameters
    ----------
    file_or_path : Union[str, BinaryIO, TextIO, Any]
        File path string or uploaded file buffer (e.g., Streamlit UploadedFile).

    Returns
    -------
    pd.DataFrame
        Extracted raw dataset as a DataFrame. Returns an empty DataFrame if reading fails.

    Raises
    ------
    Exception
        Re-raises critical file parsing errors after logging structured error details.
    """
    file_identifier: str = getattr(file_or_path, 'name', str(file_or_path))
    logger.info("Executing CSV ingestion for file source: '%s'", file_identifier)

    try:
        # Read CSV file using pandas
        df: pd.DataFrame = pd.read_csv(file_or_path)

        # Log dataframe shape details
        row_count: int = len(df)
        col_count: int = len(df.columns)

        if row_count == 0:
            logger.warning("CSV file source '%s' yielded an empty DataFrame (0 rows)", file_identifier)
        else:
            logger.info(
                "CSV file source '%s' parsed successfully: %d rows, %d columns",
                file_identifier,
                row_count,
                col_count
            )

        return df

    except FileNotFoundError as fnf_err:
        logger.error("CSV file not found at path: '%s'. Error: %s", file_identifier, fnf_err)
        raise fnf_err

    except pd.errors.EmptyDataError as empty_err:
        logger.error("CSV file source '%s' is empty or contains no readable data. Error: %s", file_identifier, empty_err)
        return pd.DataFrame()

    except pd.errors.ParserError as parse_err:
        logger.error("Parsing error encountered while reading CSV source '%s': %s", file_identifier, parse_err)
        raise parse_err

    except Exception as exc:
        logger.exception("Unexpected error occurred while loading CSV source '%s': %s", file_identifier, exc)
        raise exc
