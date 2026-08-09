"""Excel Data Loader Module.

This module provides dedicated XLSX/XLS file loading functionality for raw campaign datasets.
It parses tabular Excel spreadsheets from both local file system paths and Streamlit binary buffers,
incorporating robust error handling, openpyxl engine validation, and structured logging.
"""

import os
import logging
from typing import Union, BinaryIO, Any
import pandas as pd

try:
    import openpyxl
    HAS_OPENPYXL: bool = True
except ImportError:
    openpyxl = None  # type: ignore
    HAS_OPENPYXL: bool = False

# Configure module-level logger for Excel loading operations
logger: logging.Logger = logging.getLogger(__name__)


def load_xlsx(file_or_path: Union[str, BinaryIO, Any]) -> pd.DataFrame:
    """Load an Excel (.xlsx / .xls) spreadsheet file or buffer into a pandas DataFrame.

    Parameters
    ----------
    file_or_path : Union[str, BinaryIO, Any]
        Local file path string or uploaded binary file object (e.g. Streamlit UploadedFile).

    Returns
    -------
    pd.DataFrame
        Extracted raw dataset as a pandas DataFrame.
        Returns an empty DataFrame if extraction fails or file contains no readable data.
    """
    file_identifier: str = getattr(file_or_path, 'name', str(file_or_path))
    logger.info("Executing Excel dataset ingestion for source: '%s'", file_identifier)

    # Validate physical file path existence if input is a path string
    if isinstance(file_or_path, str) and not os.path.exists(file_or_path):
        logger.error("Excel target file path does not exist: '%s'", file_or_path)
        return pd.DataFrame()

    # Check if openpyxl engine is available
    if not HAS_OPENPYXL:
        logger.error(
            "openpyxl package is not installed in the python environment. "
            "Cannot parse Excel file '%s'. Please install openpyxl (`pip install openpyxl`).",
            file_identifier
        )
        return pd.DataFrame()

    try:
        # Read Excel file using pandas read_excel with openpyxl engine
        df: pd.DataFrame = pd.read_excel(file_or_path, engine="openpyxl")

        row_count: int = len(df)
        col_count: int = len(df.columns)

        if row_count == 0:
            logger.warning("Excel file source '%s' yielded an empty DataFrame (0 rows)", file_identifier)
        else:
            logger.info(
                "Excel file source '%s' parsed successfully: %d rows, %d columns",
                file_identifier,
                row_count,
                col_count
            )

        return df

    except FileNotFoundError as fnf_err:
        logger.error("Excel file not found at path: '%s'. Error: %s", file_identifier, fnf_err)
        return pd.DataFrame()

    except ValueError as val_err:
        logger.error("Value/Format error encountered while reading Excel source '%s': %s", file_identifier, val_err)
        return pd.DataFrame()

    except Exception as exc:
        logger.exception("Unexpected error occurred while loading Excel source '%s': %s", file_identifier, exc)
        return pd.DataFrame()