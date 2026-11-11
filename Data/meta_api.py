"""Meta Graph API Data Ingestion Module.

Fetches campaign insights from the Meta (Facebook) Graph API and normalises
the response into the platform's canonical DataFrame schema so it can flow
directly into the cleaning, validation, analytics, and AI pipelines without
any downstream changes.

Canonical mandatory columns produced:
    spend_inr, clicks, impressions, date

Canonical optional columns produced (when available from Meta):
    campaign_name, objective, reach, conversions,
    age_group, gender, device, ctr, cpc, cpm
"""

import json
import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

logger: logging.Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_GRAPH_API_VERSION: str = "v20.0"
_BASE_URL: str = f"https://graph.facebook.com/{_GRAPH_API_VERSION}"
_REQUEST_TIMEOUT: int = 30  # seconds per individual HTTP call

# Meta field names that map to conversion events we care about
_CONVERSION_ACTION_TYPES: frozenset = frozenset(
    {
        "purchase",
        "offsite_conversion.fb_pixel_purchase",
        "lead",
        "offsite_conversion.fb_pixel_lead",
        "complete_registration",
        "offsite_conversion.fb_pixel_complete_registration",
        "omni_purchase",
        "omni_complete_registration",
    }
)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _sanitize_account_id(ad_account_id: str) -> str:
    """Ensure the account ID is prefixed with ``act_``.

    Parameters
    ----------
    ad_account_id : str
        Raw account ID supplied by the user (e.g. ``"123456789"`` or
        ``"act_123456789"``).

    Returns
    -------
    str
        Properly formatted account ID (e.g. ``"act_123456789"``).

    Raises
    ------
    ValueError
        If ``ad_account_id`` is empty or contains only whitespace.
    """
    cleaned: str = ad_account_id.strip()
    if not cleaned:
        raise ValueError("Ad Account ID must not be empty.")
    if cleaned.lstrip("-").isdigit():
        cleaned = f"act_{cleaned}"
    if not cleaned.startswith("act_"):
        # Accept formats like "act_123" directly; flag anything else as-is
        logger.warning(
            "Account ID '%s' does not start with 'act_' and is not purely numeric. "
            "Sending as-is — the API will reject it if malformed.",
            cleaned,
        )
    logger.debug("Sanitized account ID: %s", cleaned)
    return cleaned


def _extract_conversions(actions_list: Any) -> int:
    """Parse Meta's nested ``actions`` field to extract total conversion count.

    Meta returns conversion events as a list of dicts:
    ``[{"action_type": "purchase", "value": "3"}, ...]``.

    Parameters
    ----------
    actions_list : Any
        The raw value of the ``actions`` field from a Meta API row. May be
        ``None``, an empty list, or a list of action dicts.

    Returns
    -------
    int
        Sum of values across all matching conversion action types. Returns
        ``0`` if no matching actions exist or the input is falsy.
    """
    if not actions_list or not isinstance(actions_list, list):
        return 0

    total: int = 0
    for action in actions_list:
        if not isinstance(action, dict):
            continue
        action_type: str = action.get("action_type", "")
        if action_type in _CONVERSION_ACTION_TYPES:
            try:
                total += int(float(action.get("value", "0")))
            except (ValueError, TypeError):
                logger.warning(
                    "Could not parse conversion value '%s' for action_type '%s'. Skipping.",
                    action.get("value"),
                    action_type,
                )
    return total


def _build_params(
    access_token: str,
    date_preset: str,
    start_date: Optional[str],
    end_date: Optional[str],
    include_demographics: bool,
) -> Dict[str, Any]:
    """Construct the base query parameters for the Meta Insights API call.

    Parameters
    ----------
    access_token : str
        Valid Meta User Access Token with ``ads_read`` permission.
    date_preset : str
        One of ``last_7d``, ``last_14d``, ``last_30d``, ``last_90d``,
        ``maximum``.
    start_date : Optional[str]
        Start date in ``YYYY-MM-DD`` format. Overrides ``date_preset`` when
        provided alongside ``end_date``.
    end_date : Optional[str]
        End date in ``YYYY-MM-DD`` format.
    include_demographics : bool
        When ``True``, adds ``age,gender`` breakdowns.

    Returns
    -------
    Dict[str, Any]
        Parameter dict ready to pass to ``requests.get``.
    """
    params: Dict[str, Any] = {
        "access_token": access_token,
        "level": "campaign",
        "time_increment": "1",
        "fields": (
            "campaign_name,objective,spend,impressions,clicks,"
            "reach,actions,ctr,cpc,cpm,date_start"
        ),
        "limit": 500,
    }

    if include_demographics:
        params["breakdowns"] = "age,gender"

    if start_date and end_date:
        params["time_range"] = json.dumps(
            {"since": start_date, "until": end_date}
        )
        logger.debug(
            "Using custom date range: %s to %s", start_date, end_date
        )
    else:
        params["date_preset"] = date_preset
        logger.debug("Using date preset: %s", date_preset)

    return params


def _paginate(
    url: str,
    params: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Collect all records across paginated Meta API responses.

    Parameters
    ----------
    url : str
        Initial endpoint URL.
    params : Dict[str, Any]
        Query parameters for the first request. Subsequent pages use the
        ``next`` URL returned by Meta (which already embeds params).

    Returns
    -------
    List[Dict[str, Any]]
        All raw record dicts concatenated across all pages.

    Raises
    ------
    RuntimeError
        If any HTTP request fails or Meta returns an error payload.
    """
    all_records: List[Dict[str, Any]] = []
    current_url: str = url
    current_params: Optional[Dict[str, Any]] = params
    page_num: int = 0

    while current_url:
        page_num += 1
        logger.info("Fetching page %d from Meta API: %s", page_num, current_url)

        try:
            response = requests.get(
                current_url,
                params=current_params,
                timeout=_REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"Meta API request timed out after {_REQUEST_TIMEOUT}s on page {page_num}. "
                "Try a narrower date range or check your network connection."
            )
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                f"Could not reach Meta Graph API: {exc}. "
                "Check your internet connection."
            ) from exc

        # Always try to parse the JSON body first — Meta sends a descriptive
        # error object even on 4xx responses, which is far more useful than the
        # raw HTTP status text that raise_for_status() would give us.
        try:
            payload: Dict[str, Any] = response.json()
        except ValueError:
            # Non-JSON body: fall back to the HTTP status description.
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as exc:
                raise RuntimeError(
                    f"Meta API returned HTTP {response.status_code} "
                    f"with a non-JSON body on page {page_num}: {exc}"
                ) from exc
            # 2xx with no parseable body — treat as empty page and stop.
            break

        # --- Meta API error block (covers 4xx and 5xx with JSON bodies) ---
        if "error" in payload:
            meta_error: Dict[str, Any] = payload["error"]
            msg: str = meta_error.get("message", "Unknown Meta API error")
            code: int = meta_error.get("code", 0)
            subcode: int = meta_error.get("error_subcode", 0)
            http_status: int = response.status_code
            raise RuntimeError(
                f"[HTTP {http_status}] Meta Graph API error "
                f"(code {code}, subcode {subcode}): {msg}"
            )

        # Raise for any unexpected non-2xx that did NOT carry an error body.
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"Meta API returned HTTP {response.status_code} on page {page_num}: {exc}"
            ) from exc

        page_data: List[Dict[str, Any]] = payload.get("data", [])
        all_records.extend(page_data)
        logger.debug("Page %d returned %d records.", page_num, len(page_data))

        # Advance to next page; after the first request params are embedded in the URL
        next_url: Optional[str] = payload.get("paging", {}).get("next")
        current_url = next_url or ""
        current_params = None  # Meta's `next` URL already carries all params

    logger.info(
        "Pagination complete. Total records fetched: %d across %d page(s).",
        len(all_records),
        page_num,
    )
    return all_records


def _normalise_to_canonical(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert raw Meta API records into the platform's canonical DataFrame.

    Parameters
    ----------
    records : List[Dict[str, Any]]
        Raw flattened records from the Meta Insights API.

    Returns
    -------
    pd.DataFrame
        DataFrame with canonical column names and correct dtypes.
        Returns an empty DataFrame if ``records`` is empty.
    """
    if not records:
        logger.warning("No records to normalise — returning empty DataFrame.")
        return pd.DataFrame()

    df: pd.DataFrame = pd.DataFrame(records)
    logger.debug("Raw columns from Meta API: %s", df.columns.tolist())

    # --- Parse conversions from nested `actions` before dropping the column ---
    if "actions" in df.columns:
        df["conversions"] = df["actions"].apply(_extract_conversions)
        df.drop(columns=["actions"], inplace=True)
    else:
        df["conversions"] = 0

    # --- Rename to canonical schema ---
    rename_map: Dict[str, str] = {
        "date_start": "date",
        "spend": "spend_inr",
        "age": "age_group",
        "impression_device": "device",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # --- Enforce mandatory columns with safe defaults ---
    mandatory_numeric: Dict[str, int] = {
        "spend_inr": 0,
        "clicks": 0,
        "impressions": 0,
        "conversions": 0,
        "reach": 0,
    }
    for col, default in mandatory_numeric.items():
        if col not in df.columns:
            logger.warning("Mandatory column '%s' missing from API response — defaulting to %d.", col, default)
            df[col] = default

    if "date" not in df.columns:
        logger.warning("'date' column missing from Meta API response.")

    # --- Coerce numeric types ---
    numeric_cols: List[str] = [
        "spend_inr", "clicks", "impressions", "conversions",
        "reach", "ctr", "cpc", "cpm",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # --- Coerce date column ---
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # --- Coerce integer-safe columns ---
    int_cols: List[str] = ["clicks", "impressions", "conversions", "reach"]
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].astype("Int64")

    logger.info(
        "Normalisation complete. DataFrame shape: %s. Columns: %s",
        df.shape,
        df.columns.tolist(),
    )
    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_meta_insights(
    ad_account_id: str,
    access_token: str,
    date_preset: str = "last_30d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_demographics: bool = True,
) -> pd.DataFrame:
    """Fetch campaign insights from the Meta Graph API.

    Handles account ID sanitization, request construction, full pagination,
    demographic breakdown fallback, nested ``actions`` parsing, and canonical
    column normalisation. The returned DataFrame slots directly into the
    platform's cleaning → validation → analytics → AI pipeline.

    Parameters
    ----------
    ad_account_id : str
        Meta Ad Account ID. Accepts bare numeric IDs (``"123456789"``) or
        pre-formatted IDs (``"act_123456789"``).
    access_token : str
        Meta User Access Token with ``ads_read`` (and optionally
        ``ads_management``) permission.
    date_preset : str, optional
        Preset date range. One of ``"last_7d"``, ``"last_14d"``,
        ``"last_30d"``, ``"last_90d"``, ``"maximum"``.
        Ignored when both ``start_date`` and ``end_date`` are provided.
        Defaults to ``"last_30d"``.
    start_date : Optional[str], optional
        Start date in ``YYYY-MM-DD`` format. Must be paired with ``end_date``.
    end_date : Optional[str], optional
        End date in ``YYYY-MM-DD`` format. Must be paired with ``start_date``.
    include_demographics : bool, optional
        When ``True``, requests ``age`` and ``gender`` breakdowns to populate
        the ``age_group`` and ``gender`` cohort columns. Defaults to ``True``.

    Returns
    -------
    pd.DataFrame
        Canonical DataFrame with normalised column names, coerced dtypes, and
        a ``conversions`` column parsed from Meta's nested ``actions`` list.
        Returns an empty DataFrame if the account has no data for the range.

    Raises
    ------
    ValueError
        If ``ad_account_id`` or ``access_token`` are empty, or if Meta returns
        an API-level error (e.g., expired token, missing permission).
    RuntimeError
        If the HTTP request fails, times out, or the API returns a malformed
        response.
    """
    # --- Input validation ---
    if not access_token or not access_token.strip():
        raise ValueError("access_token must not be empty.")

    formatted_account_id: str = _sanitize_account_id(ad_account_id)
    endpoint: str = f"{_BASE_URL}/{formatted_account_id}/insights"

    logger.info(
        "Initiating Meta Graph API fetch | account=%s | preset=%s | "
        "start=%s | end=%s | demographics=%s",
        formatted_account_id,
        date_preset,
        start_date,
        end_date,
        include_demographics,
    )

    params: Dict[str, Any] = _build_params(
        access_token=access_token.strip(),
        date_preset=date_preset,
        start_date=start_date,
        end_date=end_date,
        include_demographics=include_demographics,
    )

    # --- Primary fetch (with demographics if requested) ---
    records: List[Dict[str, Any]] = []
    _breakdown_error: bool = False
    try:
        records = _paginate(endpoint, params)
    except RuntimeError as exc:
        err_str: str = str(exc)
        # 403 / breakdown-not-permitted errors must trigger the no-demographics
        # fallback rather than surfacing to the user immediately.
        _is_breakdown_issue: bool = (
            "403" in err_str
            or "breakdown" in err_str.lower()
            or "permission" in err_str.lower()
            or "does not support" in err_str.lower()
        )
        if include_demographics and _is_breakdown_issue:
            logger.warning(
                "Demographics breakdown rejected by Meta API (%s). "
                "Retrying without demographic breakdowns.",
                err_str,
            )
            _breakdown_error = True
        else:
            raise
    except Exception as exc:
        logger.exception("Unexpected error during Meta API pagination.")
        raise RuntimeError(f"Unexpected error fetching Meta insights: {exc}") from exc

    # --- Fallback: retry without demographics (error path OR empty-result path) ---
    _needs_fallback: bool = _breakdown_error or (not records and include_demographics)
    if _needs_fallback:
        logger.warning(
            "Retrying Meta API fetch without demographic breakdowns."
        )
        fallback_params: Dict[str, Any] = {
            k: v for k, v in params.items() if k != "breakdowns"
        }
        try:
            records = _paginate(endpoint, fallback_params)
        except Exception as exc:
            logger.error("Fallback fetch (no demographics) also failed: %s", exc)
            raise

    df: pd.DataFrame = _normalise_to_canonical(records)
    return df
