# src/utils.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Utility / helper functions used across the pipeline.
#   These are generic tools — they do NOT contain any business logic
#   (that lives in fetch_mandi_prices.py).
#
# CONTAINS:
#   - setup_logging()      : Configure file + console logging
#   - ensure_directories() : Create data/ and logs/ folders if missing
#   - get_today_filepath() : Build today's dated CSV path
#   - print_summary()      : Print the formatted terminal summary box
# ─────────────────────────────────────────────────────────────────────────────

import logging
import logging.handlers
from datetime import date
from pathlib import Path

from src.config import Config


def setup_logging() -> logging.Logger:
    """
    Configure the application logger.

    Sets up TWO log handlers:
      1. Rotating file handler → writes logs to logs/krishi_pipeline.log
         (automatically starts a new file when it exceeds LOG_MAX_BYTES)
      2. Console (stream) handler → prints INFO-level+ messages to the terminal

    Returns:
        logging.Logger: The configured logger named 'krishi'.
    """
    # Create a named logger. Using a name (instead of root logger)
    # keeps our logs separate from library logs (e.g., requests, urllib3).
    logger = logging.getLogger("krishi")
    logger.setLevel(logging.DEBUG)  # Capture everything at DEBUG and above

    # Avoid adding duplicate handlers if this function is called more than once
    if logger.handlers:
        return logger

    # ── Log Format ────────────────────────────────────────────────────────────
    # Example output: 2026-07-16 15:30:00 | INFO     | Fetching page 1...
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Handler 1: Rotating File ───────────────────────────────────────────────
    # Writes detailed DEBUG-level logs to the log file.
    log_filepath = Config.LOG_DIR / Config.LOG_FILENAME
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_filepath,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # ── Handler 2: Console (Terminal) ─────────────────────────────────────────
    # Prints only INFO-level and above to the terminal (not cluttered with DEBUG).
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Attach both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def ensure_directories() -> None:
    """
    Create the required project directories if they do not already exist.

    Creates:
        - data/   → where daily CSV files are saved
        - logs/   → where log files are written

    Uses exist_ok=True so it never raises an error if they already exist.
    """
    Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    Config.LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_today_filepath() -> Path:
    """
    Build the full file path for today's output CSV file.

    The file is named using today's date in YYYY-MM-DD format.
    Example: data/2026-07-16.csv

    Returns:
        Path: Full path object pointing to today's CSV file.
    """
    # date.today() returns the current date. isoformat() gives "YYYY-MM-DD".
    today_str = date.today().isoformat()
    return Config.DATA_DIR / f"{today_str}.csv"


def print_summary(
    records_downloaded: int,
    karnataka_records: int,
    output_filepath: Path,
    success: bool = True,
) -> None:
    """
    Print a formatted summary box to the terminal at the end of the pipeline.

    Args:
        records_downloaded (int): Total number of records fetched from the API.
        karnataka_records (int): Number of records after Karnataka filtering.
        output_filepath (Path): Path where the CSV was saved.
        success (bool): Whether the pipeline completed without errors.
    """
    # Build the status line based on success or failure
    status_line = "Completed Successfully" if success else "Completed With Errors"

    # Print the formatted summary box
    print()
    print("------------------------------------")
    print("  Karnataka Mandi Price Collector   ")
    print("------------------------------------")
    print()
    print("  Connection Successful")
    print()
    print(f"  Records Downloaded  : {records_downloaded:,}")
    print(f"  Karnataka Records   : {karnataka_records:,}")
    print()
    print(f"  File Saved:")
    print(f"  {output_filepath}")
    print()
    print(f"  {status_line}")
    print()
    print("------------------------------------")
    print()
