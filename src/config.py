# src/config.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Central configuration file for the Krishi Market Advisor pipeline.
#   All settings are defined here so that the rest of the code never has
#   hardcoded values. Changing a setting only requires editing this one file.
#
# USAGE:
#   from src.config import Config
#   url = Config.BASE_URL
# ─────────────────────────────────────────────────────────────────────────────

import os
from pathlib import Path
from dotenv import load_dotenv

# ─── Project Root ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from the .env file in the project root.
load_dotenv(PROJECT_ROOT / ".env", override=True)


class Config:
    """
    All configuration values for the pipeline are stored as class attributes.
    No instances are needed — access them directly as Config.ATTRIBUTE_NAME.
    """

    # ── API Settings ──────────────────────────────────────────────────────────
    # The base URL for the Open Government Data (OGD) platform API.
    # Source: https://data.gov.in
    BASE_URL: str = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    # The unique resource identifier for the Agmarknet daily mandi price dataset.
    # Dataset: "Current Daily Price of Various Commodities from Various Markets (Mandi)"
    RESOURCE_ID: str = "9ef84268-d588-465a-a308-a864a43d0070"

    # Your personal API key from data.gov.in.
    # This is loaded from the .env file (DATA_GOV_IN_API_KEY=your_key_here).
    # To get your free API key, register at: https://data.gov.in/user/register
    API_KEY: str = os.getenv("DATA_GOV_IN_API_KEY", "")

    # Google Gemini API key for Phase 4 AI market explanations
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


    # ── Data Filter Settings ──────────────────────────────────────────────────
    # We only want records from Karnataka.
    TARGET_STATE: str = "Karnataka"

    # The format the API should return data in.
    # Options: "json", "csv", "xml". We use JSON for reliable parsing.
    API_FORMAT: str = "json"

    # ── Pagination Settings ───────────────────────────────────────────────────
    # How many records to request per API call.
    # The OGD API supports up to 1000 records per page.
    PAGE_LIMIT: int = 1000

    # Maximum total records to download (safety cap to avoid infinite loops).
    # Set to a large number to download all available records.
    MAX_TOTAL_RECORDS: int = 100_000

    # ── Retry Settings ────────────────────────────────────────────────────────
    # How many times to retry a failed API request before giving up.
    MAX_RETRIES: int = 3

    # Seconds to wait between retries (increases with each attempt).
    RETRY_DELAY_SECONDS: int = 5

    # Timeout in seconds for each API request.
    # Tuple: (connect_timeout, read_timeout) — fail fast if server is unresponsive
    REQUEST_TIMEOUT: tuple = (10, 20)

    # ── Agmarknet 2.0 API (Fallback) ────────────────────────────────────────────
    # If data.gov.in API is unresponsive, fall back to the Agmarknet 2.0
    # internal REST API (discovered from the React app JS bundle).
    # This API powers the official agmarknet.gov.in portal directly.
    AGMARKNET_API_BASE: str = "https://api.agmarknet.gov.in/v1"

    # Endpoint for commodity+market daily report filtered by state
    AGMARKNET_DAILY_ENDPOINT: str = "/prices-and-arrivals/commodity-market/daily-report-state"

    # Endpoint to get the list of all states with their IDs
    AGMARKNET_STATES_ENDPOINT: str = "/location/state"

    # Karnataka's state ID in the Agmarknet 2.0 system (discovered via API)
    KARNATAKA_STATE_ID: int = 16

    # Browser-like headers to send with Agmarknet 2.0 API requests
    AGMARKNET_HEADERS: dict = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://agmarknet.gov.in/",
        "Origin": "https://agmarknet.gov.in",
    }

    # Timeout for Agmarknet 2.0 API (connect, read)
    AGMARKNET_TIMEOUT: tuple = (10, 30)

    # ── Directory Paths ───────────────────────────────────────────────────────
    # Where cleaned CSV files are saved (e.g., data/2026-07-16.csv)
    DATA_DIR: Path = PROJECT_ROOT / "data"

    # Where application log files are saved
    LOG_DIR: Path = PROJECT_ROOT / "logs"

    # ── Logging Settings ──────────────────────────────────────────────────────
    # Name of the log file inside the logs/ folder
    LOG_FILENAME: str = "krishi_pipeline.log"

    # Maximum size of one log file (in bytes). 5 MB = 5 * 1024 * 1024
    LOG_MAX_BYTES: int = 5 * 1024 * 1024

    # How many old log files to keep before deleting them
    LOG_BACKUP_COUNT: int = 3

    # ── Data Validation ───────────────────────────────────────────────────────
    # The columns that MUST exist in the downloaded data for it to be valid.
    # These match the Agmarknet 2.0 API flattened structure.
    REQUIRED_COLUMNS: list = [
        "state",
        "market",
        "commodity",
        "variety",
        "min_price",
        "max_price",
        "modal_price",
        "arrival_date",
    ]


    # ── Column Mapping ────────────────────────────────────────────────────────
    # Maps raw API column names → clean, standardized column names.
    # The OGD API may return differently capitalised or formatted names.
    COLUMN_RENAME_MAP: dict = {
        "State": "state",
        "District": "district",
        "Market": "market",
        "Commodity": "commodity",
        "Variety": "variety",
        "Min Price (Rs./Quintal)": "min_price",
        "Max Price (Rs./Quintal)": "max_price",
        "Modal Price (Rs./Quintal)": "modal_price",
        "Arrival Date": "arrival_date",
        # Also handle lowercase versions from the API
        "state": "state",
        "district": "district",
        "market": "market",
        "commodity": "commodity",
        "variety": "variety",
        "min_price": "min_price",
        "max_price": "max_price",
        "modal_price": "modal_price",
        "arrival_date": "arrival_date",
    }
