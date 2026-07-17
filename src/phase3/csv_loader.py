# src/phase3/csv_loader.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Automatically scan the data/ directory, sort historical CSVs chronologically,
#   and identify the latest and previous CSV files for analysis.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from pathlib import Path
import pandas as pd
from src.config import Config

logger = logging.getLogger("krishi")


def scan_data_directory(data_dir: Path = None) -> list:
    """
    Scan the data directory for daily CSV files and sort them chronologically by filename.

    Args:
        data_dir (Path, optional): Directory to scan. Defaults to Config.DATA_DIR.

    Returns:
        list[Path]: Chronologically sorted list of CSV file paths.
    """
    if data_dir is None:
        data_dir = Config.DATA_DIR

    logger.info(f"Scanning data directory for historical CSV files: {data_dir}...")

    if not data_dir.exists():
        logger.warning(f"Data directory does not exist: {data_dir}")
        return []

    # Gather all *.csv files, ignore any non-csv files or folder templates (like .gitkeep)
    csv_files = [f for f in data_dir.glob("*.csv") if f.is_file()]

    # Sort files chronologically by their filenames (e.g. YYYY-MM-DD.csv)
    csv_files.sort(key=lambda x: x.name)

    logger.info(f"Detected {len(csv_files)} historical CSV file(s).")
    for f in csv_files:
        logger.debug(f"Found CSV: {f.name}")

    return csv_files


def load_csv_data(file_path: Path) -> pd.DataFrame:
    """
    Load data from a single CSV file.

    Args:
        file_path (Path): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    logger.info(f"Loading data from: {file_path.name}")
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        logger.error(f"Failed to load CSV file {file_path.name}: {e}")
        raise e
