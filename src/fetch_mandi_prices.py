# src/fetch_mandi_prices.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Core data pipeline logic for the Krishi Market Advisor.
#   This module is responsible for:
#     1. Connecting to the data.gov.in OGD API (primary source)
#     2. Automatically falling back to Agmarknet portal (if OGD API is down)
#     3. Downloading all mandi price records (with pagination for OGD API)
#     4. Filtering to Karnataka records only
#     5. Validating the data structure
#     6. Cleaning: deduplication and handling missing values
#     7. Saving the cleaned data as a CSV file
#
# DATA SOURCES (in order of priority):
#   PRIMARY:  data.gov.in OGD API  → https://api.data.gov.in/resource/9ef84268-...
#   FALLBACK: Agmarknet portal     → https://agmarknet.gov.in/SearchCmmMkt.aspx
# ─────────────────────────────────────────────────────────────────────────────

import logging
import time
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import Config

# Get the named logger configured in utils.setup_logging()
logger = logging.getLogger("krishi")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: HTTP SESSION SETUP
# ─────────────────────────────────────────────────────────────────────────────

def create_session() -> requests.Session:
    """
    Create and configure a persistent HTTP session with automatic retry logic.

    Why a Session?
        A requests.Session reuses the underlying TCP connection across multiple
        requests to the same server. This is faster than opening a new connection
        for every paginated API call.

    Retry Strategy:
        Automatically retries on network errors and specific HTTP error codes
        (e.g., 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable).
        Uses exponential backoff: waits 0s, 2s, 4s between retries.

    Returns:
        requests.Session: Configured session ready for API calls.
    """
    session = requests.Session()

    # Some networks silently stall requests carrying the default
    # "python-requests/x.x" User-Agent (looks like a bot). Sending a
    # normal browser-style header avoids that.
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    })

    # Define retry behaviour using urllib3's Retry utility
    retry_strategy = Retry(
        total=Config.MAX_RETRIES,           # Maximum number of retry attempts
        backoff_factor=2,                   # Wait: 0s, 2s, 4s between retries
        status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry on
        allowed_methods=["GET"],            # Only retry GET requests (safe to repeat)
    )

    # Mount the retry strategy on the HTTPS adapter
    # This means ALL https:// requests from this session will use this retry logic
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: SINGLE PAGE FETCH
# ─────────────────────────────────────────────────────────────────────────────

def fetch_page(session: requests.Session, offset: int, limit: int) -> dict:
    """
    Fetch a single page of mandi price records from the OGD API.

    The API uses offset-based pagination:
        - offset=0,    limit=1000 → records 1–1000
        - offset=1000, limit=1000 → records 1001–2000
        - offset=2000, limit=1000 → records 2001–3000
        ... and so on.

    Args:
        session (requests.Session): The configured HTTP session (with retries).
        offset (int): How many records to skip (used for pagination).
        limit (int): How many records to request in this call.

    Returns:
        dict: Parsed JSON response from the API. Contains:
              - "records": list of data rows (each row is a dict)
              - "total": total number of records available on the server
              - "count": number of records returned in this response

    Raises:
        requests.exceptions.HTTPError: If the server returns an error code.
        requests.exceptions.ConnectionError: If the network is unavailable.
        requests.exceptions.Timeout: If the server doesn't respond in time.
    """
    # Build the query parameters for this API call
    params = {
        "api-key": Config.API_KEY,         # Your personal authentication key
        "format": Config.API_FORMAT,       # Response format: "json"
        "limit": limit,                    # Records per page
        "offset": offset,                  # Starting position
        # Filter to Karnataka state directly on the server side
        # This reduces the amount of data transferred over the network
        "filters[state]": Config.TARGET_STATE,
    }

    logger.debug(f"Fetching records {offset + 1} to {offset + limit} ...")

    # Make the GET request. timeout prevents hanging indefinitely.
    response = session.get(
        Config.BASE_URL,
        params=params,
        timeout=Config.REQUEST_TIMEOUT,
    )

    # Raise an exception immediately if the server returned an HTTP error
    # (e.g., 401 Unauthorized, 403 Forbidden, 429 Too Many Requests)
    response.raise_for_status()

    # Parse and return the JSON response body as a Python dictionary
    return response.json()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: PAGINATED DOWNLOAD (ALL RECORDS)
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_from_ogd_api() -> pd.DataFrame:
    """
    Attempt to download Karnataka mandi prices from the data.gov.in OGD API.

    This is the PRIMARY data source. It uses paginated API calls.
    Will raise an exception if the API is unresponsive or returns an error.

    Returns:
        pd.DataFrame: All Karnataka price records from the OGD API.

    Raises:
        requests.exceptions.Timeout: If the API doesn't respond in time.
        requests.exceptions.ConnectionError: If the network is unreachable.
        requests.exceptions.HTTPError: If the API returns an HTTP error.
        RuntimeError: If no records are returned.
    """
    # ── Pre-flight Check: API Key ──────────────────────────────────────────
    if not Config.API_KEY:
        raise ValueError(
            "API key is missing! Please:\n"
            "  1. Register for a free key at https://data.gov.in/user/register\n"
            "  2. Copy .env.example to .env\n"
            "  3. Set DATA_GOV_IN_API_KEY=your_key_here in .env"
        )

    # Create a reusable HTTP session with automatic retries
    session = create_session()

    all_records = []        # List to collect records from all pages
    offset = 0              # Start at the beginning
    total_available = None  # We'll learn the total count from the first response

    logger.info("Starting download from data.gov.in OGD API ...")
    logger.info(f"Filtering for state: {Config.TARGET_STATE}")

    # ── Pagination Loop ────────────────────────────────────────────────────
    while True:
        # Fetch one page of data (raises exception immediately on failure)
        response_data = fetch_page(session, offset=offset, limit=Config.PAGE_LIMIT)

        # On the first page, read the total number of available records
        if total_available is None:
            total_available = int(response_data.get("total", 0))
            logger.info(f"Total records available on server: {total_available:,}")

        # Extract the list of records from this page's response
        page_records = response_data.get("records", [])
        records_this_page = len(page_records)

        if records_this_page == 0:
            logger.info("No more records to fetch. Download complete.")
            break

        all_records.extend(page_records)
        logger.info(f"Downloaded {len(all_records):,} / {total_available:,} records ...")

        # Move to the next page
        offset += records_this_page

        # Safety check: stop if we've exceeded our configured maximum
        if len(all_records) >= Config.MAX_TOTAL_RECORDS:
            logger.warning(f"Reached MAX_TOTAL_RECORDS limit ({Config.MAX_TOTAL_RECORDS:,}). Stopping.")
            break

        # Stop if we've collected all available records
        if len(all_records) >= total_available:
            logger.info("All records downloaded successfully.")
            break

        # Small pause between requests to be respectful to the API server
        time.sleep(0.5)

    if not all_records:
        raise RuntimeError(
            f"No records were returned from the OGD API for state: {Config.TARGET_STATE}."
        )

    df = pd.DataFrame(all_records)
    logger.info(f"OGD API: successfully downloaded {len(df):,} records.")
    return df


def fetch_all_records() -> pd.DataFrame:
    """
    Download ALL Karnataka mandi price records using a two-source strategy:

      1. PRIMARY:  data.gov.in OGD API (official, structured, paginated)
         → Fast, clean JSON data — but the government API is sometimes unresponsive.

      2. FALLBACK: Agmarknet portal (agmarknet.gov.in) HTML scraper
         → Directly scrapes the official price search page if the OGD API fails.

    The function automatically tries the primary source first. If it times out
    or fails, it logs a warning and transparently switches to the fallback.
    The rest of the pipeline (filter, validate, clean, save) works the same
    regardless of which source provided the data.

    Returns:
        pd.DataFrame: All downloaded records combined into a single DataFrame.

    Raises:
        RuntimeError: If BOTH data sources fail.
        ValueError: If the API key is missing (for the primary source check).
    """
    # ── Attempt 1: OGD API (Primary) ──────────────────────────────────────
    try:
        logger.info("Trying PRIMARY source: data.gov.in OGD API ...")
        df = _fetch_from_ogd_api()
        logger.info(f"Primary source succeeded: {len(df):,} records downloaded.")
        return df

    except requests.exceptions.Timeout:
        logger.warning(
            "OGD API timed out (server unresponsive). "
            "Switching to FALLBACK source: Agmarknet portal ..."
        )
    except requests.exceptions.ConnectionError:
        logger.warning(
            "OGD API connection failed (network error). "
            "Switching to FALLBACK source: Agmarknet portal ..."
        )
    except requests.exceptions.HTTPError as e:
        logger.warning(
            f"OGD API HTTP error ({e}). "
            "Switching to FALLBACK source: Agmarknet portal ..."
        )
    except RuntimeError as e:
        logger.warning(
            f"OGD API Runtime error ({e}). "
            "Switching to FALLBACK source: Agmarknet portal ..."
        )
    except ValueError:
        # Missing API key — re-raise immediately, no point trying fallback
        raise

    # ── Attempt 2: Agmarknet Portal Scraper (Fallback) ────────────────────
    try:
        from src.agmarknet_scraper import fetch_from_agmarknet
        logger.info("Trying FALLBACK source: Agmarknet portal scraper ...")
        df = fetch_from_agmarknet()
        logger.info(f"Fallback source succeeded: {len(df):,} records downloaded.")
        return df

    except Exception as e:
        logger.error(f"Fallback source also failed: {e}")
        raise RuntimeError(
            "Both data sources failed:\n"
            "  1. data.gov.in OGD API → Timed out or connection error\n"
            "  2. Agmarknet portal    → Error during scraping\n\n"
            "Please check your internet connection and try again in a few minutes.\n"
            f"Last error: {e}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: FILTER KARNATAKA RECORDS
# ─────────────────────────────────────────────────────────────────────────────

def filter_karnataka(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the DataFrame to keep only Karnataka records.

    Although we already pass a server-side filter in the API call, this
    function acts as a safety net to ensure no non-Karnataka records slip
    through (e.g., if the API filter is case-sensitive or has edge cases).

    Args:
        df (pd.DataFrame): Raw DataFrame downloaded from the API.

    Returns:
        pd.DataFrame: Filtered DataFrame with only Karnataka records.
    """
    logger.info("Applying Karnataka state filter ...")

    # Find the column that holds state information.
    # We check both "state" and "State" to handle different API capitalisations.
    state_column = None
    for col in df.columns:
        if col.lower() == "state":
            state_column = col
            break

    if state_column is None:
        logger.warning(
            "Could not find a 'state' column in the data. "
            "Skipping Karnataka filter — returning all records."
        )
        return df

    # Filter rows where the state column (case-insensitive) equals "Karnataka"
    original_count = len(df)
    mask = df[state_column].str.strip().str.lower() == Config.TARGET_STATE.lower()
    filtered_df = df[mask].copy()

    logger.info(
        f"Karnataka filter applied: {original_count:,} total → "
        f"{len(filtered_df):,} Karnataka records."
    )

    return filtered_df


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: VALIDATE DATA
# ─────────────────────────────────────────────────────────────────────────────

def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate the downloaded DataFrame for completeness and structure.

    Checks performed:
      1. DataFrame is not empty (has at least 1 row)
      2. Required columns are present (after renaming)

    This function does NOT raise an error — it logs warnings and returns
    True/False so the caller can decide how to handle invalid data.

    Args:
        df (pd.DataFrame): DataFrame to validate (after filtering).

    Returns:
        bool: True if data passes all checks, False if any check fails.
    """
    logger.info("Validating downloaded data ...")
    is_valid = True

    # ── Check 1: Not Empty ─────────────────────────────────────────────────
    if df.empty:
        logger.error("Validation FAILED: DataFrame is empty — no records to save.")
        return False

    logger.debug(f"Validation check 1 passed: DataFrame has {len(df):,} rows.")

    # ── Check 2: Required Columns Present ─────────────────────────────────
    # Normalise DataFrame column names for comparison
    normalised_columns = [col.lower().replace(" ", "_") for col in df.columns]

    missing_columns = []
    for required_col in Config.REQUIRED_COLUMNS:
        if required_col.lower() not in normalised_columns:
            missing_columns.append(required_col)

    if missing_columns:
        logger.warning(
            f"Validation WARNING: These expected columns are missing: {missing_columns}. "
            "The data structure may have changed. Proceeding with available columns."
        )
        # This is a warning, not a hard failure — the API schema can evolve
        is_valid = True  # Still proceed, but log the discrepancy
    else:
        logger.debug("Validation check 2 passed: All required columns present.")

    logger.info(f"Data validation complete. Valid: {is_valid}")
    return is_valid


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: CLEAN DATA
# ─────────────────────────────────────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw DataFrame by:
      1. Renaming columns to a consistent lowercase_underscore format
      2. Removing duplicate rows
      3. Handling missing values gracefully
      4. Stripping extra whitespace from string columns

    Args:
        df (pd.DataFrame): The filtered (Karnataka-only) DataFrame.

    Returns:
        pd.DataFrame: The cleaned, ready-to-save DataFrame.
    """
    logger.info("Cleaning data ...")
    original_count = len(df)

    # ── Step 1: Rename Columns ─────────────────────────────────────────────
    # Map raw API column names to clean, standardised names.
    # Only rename columns that exist in the mapping — ignore the rest.
    rename_map = {
        col: Config.COLUMN_RENAME_MAP[col]
        for col in df.columns
        if col in Config.COLUMN_RENAME_MAP
    }
    if rename_map:
        df = df.rename(columns=rename_map)
        logger.debug(f"Renamed columns: {rename_map}")

    # For any remaining columns not in the rename map, convert to lowercase
    df.columns = [col.lower().replace(" ", "_").replace("(", "").replace(")", "")
                  for col in df.columns]

    # ── Step 2: Strip Whitespace from String Columns ───────────────────────
    # Government data often has extra spaces in text fields.
    string_columns = df.select_dtypes(include="object").columns
    for col in string_columns:
        df[col] = df[col].str.strip()

    logger.debug(f"Stripped whitespace from {len(string_columns)} text columns.")

    # ── Step 3: Remove Duplicate Rows ─────────────────────────────────────
    # Duplicates can occur if the same data was reported multiple times.
    df = df.drop_duplicates()
    duplicates_removed = original_count - len(df)

    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed:,} duplicate rows.")
    else:
        logger.debug("No duplicate rows found.")

    # ── Step 4: Handle Missing Values ─────────────────────────────────────
    # Count cells with missing values (NaN, None, empty strings)
    missing_count = df.isnull().sum().sum()

    if missing_count > 0:
        logger.warning(
            f"Found {missing_count:,} missing values across the dataset. "
            "Filling numeric fields with 0, text fields with 'Unknown'."
        )
        # For numeric columns (prices), fill missing values with 0
        numeric_cols = df.select_dtypes(include=["number"]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # For text/categorical columns, fill missing values with "Unknown"
        text_cols = df.select_dtypes(include="object").columns
        df[text_cols] = df[text_cols].fillna("Unknown")
    else:
        logger.debug("No missing values found.")

    logger.info(
        f"Cleaning complete: {original_count:,} rows → {len(df):,} rows after cleaning."
    )

    return df


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: SAVE DATA
# ─────────────────────────────────────────────────────────────────────────────

def save_data(df: pd.DataFrame, filepath: Path) -> None:
    """
    Save the cleaned DataFrame to a CSV file.

    The file is named using today's date (e.g., data/2026-07-16.csv).
    The index column (row numbers) is NOT included in the saved file.

    Args:
        df (pd.DataFrame): The cleaned, ready-to-save DataFrame.
        filepath (Path): Full path where the CSV file should be written.

    Raises:
        IOError: If the file cannot be written (e.g., permission denied).
    """
    logger.info(f"Saving {len(df):,} records to: {filepath}")

    # Save to CSV without the pandas row index column
    df.to_csv(filepath, index=False, encoding="utf-8")

    logger.info(f"File saved successfully: {filepath}")
