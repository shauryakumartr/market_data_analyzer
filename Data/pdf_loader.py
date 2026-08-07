"""PDF Table Data Extraction Module.

This module provides table extraction functionality from PDF documents containing marketing
campaign data using pdfplumber. It converts tabular structures across multi-page PDF documents
into a unified raw pandas DataFrame.
"""

import os
import sys
import logging
from typing import Union, BinaryIO, List, Optional, Any, Sequence
import pandas as pd
try:
    import pdfplumber as plumber
    HAS_PDFPLUMBER: bool = True
except ImportError:
    plumber = None  # type: ignore
    HAS_PDFPLUMBER: bool = False

# Configure module-level logger for PDF parsing operations
logger: logging.Logger = logging.getLogger(__name__)


def load_pdf(file_or_path: Union[str, BinaryIO, Any]) -> pd.DataFrame:
    """Extract tabular data from a PDF document or uploaded file buffer into a DataFrame.

    Parameters
    ----------
    file_or_path : Union[str, BinaryIO, Any]
        Local file path string or uploaded binary file object (e.g. Streamlit UploadedFile).

    Returns
    -------
    pd.DataFrame
        Extracted tabular data compiled into a pandas DataFrame.
        Returns an empty DataFrame if extraction yields no tabular records.
    """
    file_identifier: str = getattr(file_or_path, 'name', str(file_or_path))
    logger.info("Executing PDF table extraction for source: '%s'", file_identifier)

    if not HAS_PDFPLUMBER:
        logger.error(
            "pdfplumber package is not installed in the python environment. "
            "Cannot parse PDF file '%s'. Please install pdfplumber (`pip install pdfplumber`).",
            file_identifier
        )
        return pd.DataFrame()

    # Validate physical path existence if input is a file path string
    if isinstance(file_or_path, str) and not os.path.exists(file_or_path):
        logger.error("PDF target file path does not exist: '%s'", file_or_path)
        return pd.DataFrame()

    df_list: List[pd.DataFrame] = []
    empty_pages: List[int] = []
    header: Optional[Sequence[str]] = None

    try:
        # Open PDF stream using pdfplumber (supports file paths and file-like binary buffers)
        with plumber.open(file_or_path) as pdf_doc:
            total_pages: int = len(pdf_doc.pages)

            if total_pages == 0:
                logger.warning("PDF document '%s' contains no pages (0 pages detected)", file_identifier)
                return pd.DataFrame()

            logger.info("Opened PDF '%s' with %d pages for table parsing", file_identifier, total_pages)

            # Iterate page by page
            for page_no, page in enumerate(pdf_doc.pages, start=1):
                table: Optional[List[List[Optional[str]]]] = page.extract_table()

                # Skip pages without extractable tables
                if not table or len(table) < 1:
                    empty_pages.append(page_no)
                    logger.debug("Page %d of '%s' contained no tabular content", page_no, file_identifier)
                    continue

                # Establish header from the first encountered table
                if header is None:
                    header = table[0]
                    data_rows: List[List[Optional[str]]] = table[1:]
                    logger.info("Established table header from Page 1: %s", header)
                    if data_rows:
                        df_list.append(pd.DataFrame(data_rows, columns=header))
                else:
                    # Check if subsequent page repeats the header row
                    if table[0] == header:
                        data_rows = table[1:]
                    else:
                        data_rows = table[:]

                    if data_rows:
                        df_list.append(pd.DataFrame(data_rows, columns=header))
                    else:
                        logger.debug("Page %d of '%s' contained only header row without data rows", page_no, file_identifier)

            if empty_pages:
                logger.info(
                    "PDF extraction completed for '%s'. Pages without tables: %s",
                    file_identifier,
                    empty_pages
                )

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        lineno: int = exc_tb.tb_lineno if exc_tb else -1
        logger.error(
            "Error on line %d during PDF extraction for '%s': %s",
            lineno,
            file_identifier,
            exc
        )
        logger.exception("Traceback details for PDF extraction failure:")

    # Concatenate all page DataFrames into a unified dataset
    if df_list:
        combined_df: pd.DataFrame = pd.concat(df_list, ignore_index=True)
        logger.info(
            "PDF extraction successful for '%s': compiled %d rows and %d columns",
            file_identifier,
            len(combined_df),
            len(combined_df.columns)
        )
        return combined_df
    else:
        logger.warning("No tabular data could be extracted from PDF source: '%s'", file_identifier)
        return pd.DataFrame()
