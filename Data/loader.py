"""Data Loading Orchestrator Module.

This module acts as the unified ingestion dispatcher for raw campaign datasets.
It routes incoming files (both filesystem paths and Streamlit uploaded file buffers)
to the appropriate file loader (CSV, PDF, or XLSX/XLS) based on the specified file format extension.
"""

import logging
from typing import Union, BinaryIO, TextIO, Any
import pandas as pd

from Data.csv_loader import load_csv
from Data.pdf_loader import load_pdf
from Data.xlsx_loader import load_xlsx

# Configure module-level logger for file loading orchestration
logger: logging.Logger = logging.getLogger(__name__)


def file_load(
    file_or_path: Union[str, BinaryIO, TextIO, Any],
    file_type: str
) -> pd.DataFrame:
    """Orchestrate data ingestion by dispatching file objects to format-specific loaders.

    Parameters
    ----------
    file_or_path : Union[str, BinaryIO, TextIO, Any]
        Physical file path string or an uploaded file-like binary/text buffer (e.g. Streamlit UploadedFile).
    file_type : str
        The lowercased file name or extension string used to identify the format (e.g. '.csv', 'campaigns.pdf', 'data.xlsx').

    Returns
    -------
    pd.DataFrame
        Extracted raw DataFrame ready for validation and data cleaning.

    Raises
    ------
    ValueError
        If the file type extension is unsupported.
    """
    cleaned_file_type: str = str(file_type).strip().lower()
    source_name: str = getattr(file_or_path, 'name', str(file_or_path))

    logger.info(
        "Initiating file loading dispatcher for source '%s' with detected format type '%s'",
        source_name,
        cleaned_file_type
    )

    # Route CSV files to the dedicated CSV parser
    if cleaned_file_type.endswith("csv"):
        logger.debug("Routing source '%s' to CSV loader module", source_name)
        df: pd.DataFrame = load_csv(file_or_path)
        logger.info(
            "Successfully dispatched and loaded CSV dataset '%s' with shape (%d, %d)",
            source_name,
            len(df),
            len(df.columns)
        )
        return df

    # Route PDF files to the dedicated PDF parser
    elif cleaned_file_type.endswith("pdf"):
        logger.debug("Routing source '%s' to PDF loader module", source_name)
        df: pd.DataFrame = load_pdf(file_or_path)
        logger.info(
            "Successfully dispatched and loaded PDF dataset '%s' with shape (%d, %d)",
            source_name,
            len(df),
            len(df.columns)
        )
        return df

    # Route Excel files (.xlsx, .xls) to the dedicated XLSX parser
    elif cleaned_file_type.endswith("xlsx") or cleaned_file_type.endswith("xls"):
        logger.debug("Routing source '%s' to XLSX loader module", source_name)
        df: pd.DataFrame = load_xlsx(file_or_path)
        logger.info(
            "Successfully dispatched and loaded Excel dataset '%s' with shape (%d, %d)",
            source_name,
            len(df),
            len(df.columns)
        )
        return df

    # Handle unsupported formats
    else:
        error_msg: str = (
            f"Unsupported file format '{file_type}' for source '{source_name}'. "
            "Supported formats are CSV (.csv), PDF (.pdf), and Excel (.xlsx, .xls)."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)