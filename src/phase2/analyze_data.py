# src/phase2/analyze_data.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Orchestrator for the Krishi Market Advisor Phase 2: Data Reliability
#   & Pilot Selection.
#   Merges all collected historical CSV files, performs analysis, selects the
#   pilot crop and pilot markets, saves reports/configs, and prints the summary.
#
# HOW TO RUN:
#   python src/phase2/analyze_data.py
# ─────────────────────────────────────────────────────────────────────────────

import sys
import logging
from pathlib import Path
import pandas as pd

# Add the project root to path if needed (to support running from root)
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import Config
from src.utils import setup_logging, ensure_directories
from src.phase2.commodity_analyzer import analyze_commodities
from src.phase2.mandi_analyzer import analyze_mandis
from src.phase2.pilot_selector import select_pilot
from src.phase2.report_generator import generate_reports

# Ensure standard output supports UTF-8 characters (e.g. emoji, currency symbols)
sys.stdout.reconfigure(encoding='utf-8')

logger = logging.getLogger("krishi")


def normalize_date(date_str: str) -> str:
    """
    Convert any recognized format (YYYY-MM-DD or DD/MM/YYYY) into YYYY-MM-DD.
    """
    date_str = str(date_str).strip()
    if not date_str or date_str.lower() == 'nan':
        return date_str

    # Already YYYY-MM-DD
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str

    # DD/MM/YYYY -> YYYY-MM-DD
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3 and len(parts[2]) == 4:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    return date_str


def run_analysis_pipeline() -> None:
    """
    Perform the complete Phase 2 analysis workflow:
      1. Merge all daily mandi price CSV files inside the data/ folder.
      2. Extract temporal parameters (date range, total days).
      3. Run mandi reliability and missing day calculations.
      4. Run commodity stats calculations (record counts, completeness).
      5. Rank commodities and select the optimal pilot crop and markets.
      6. Output results to the terminal and generate reports/configs.
    """
    # ── Stage 1: Setup & Data Loading ─────────────────────────────────────────
    ensure_directories()
    setup_logging()

    logger.info("=" * 60)
    logger.info("Krishi Market Advisor — Phase 2 Analysis Pipeline Starting")
    logger.info("=" * 60)

    # Find all CSV files inside data directory
    data_dir = Config.DATA_DIR
    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        logger.error(
            f"No mandi price CSV data files found inside: {data_dir}. "
            "Please run Phase 1 data collection first to gather data."
        )
        sys.exit(1)

    # ── Stage 2: Merge CSV Files ─────────────────────────────────────────────
    logger.info(f"Merging {len(csv_files)} CSV files from {data_dir}...")
    dataframes = []
    
    for f in csv_files:
        try:
            temp_df = pd.read_csv(f)
            if not temp_df.empty:
                dataframes.append(temp_df)
        except Exception as e:
            logger.warning(f"Failed to read file {f.name}: {e}")

    if not dataframes:
        logger.error("No valid non-empty data files could be loaded.")
        sys.exit(1)

    merged_df = pd.concat(dataframes, ignore_index=True)
    total_records = len(merged_df)
    total_files = len(csv_files)

    logger.info(f"Merged successfully. Total Records: {total_records:,}")

    # ── Stage 3: Temporal Analysis Window ─────────────────────────────────────
    # Make sure we have the date column and standardise it
    if "arrival_date" not in merged_df.columns:
        logger.error("Data error: merged dataset is missing 'arrival_date' column.")
        sys.exit(1)

    # Standardize dates using the normalize_date helper before converting to datetime
    merged_df["arrival_date"] = merged_df["arrival_date"].astype(str).apply(normalize_date)

    # Standardize dates for min/max calculation
    # We parse and sort to find the correct chronological start and end dates
    #
    # IMPORTANT FIX: the raw arrival_date column mixes formats across
    # different collaborators' pipelines -- some rows are "YYYY-MM-DD",
    # others are "DD/MM/YYYY". Letting pandas auto-detect this (the
    # default dayfirst=False) silently mis-parses or drops the
    # DD/MM/YYYY rows as NaT, which shrank a real 3-day window down to
    # 2 days and produced an impossible "150% reporting consistency".
    # Normalizing every date string to YYYY-MM-DD first, before parsing,
    # avoids the ambiguity entirely.
    def _normalize_date_string(date_str):
        if pd.isna(date_str):
            return date_str
        date_str = str(date_str).strip()
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3 and len(parts[2]) == 4:
                day, month, year = parts
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return date_str

    normalized_dates = merged_df["arrival_date"].apply(_normalize_date_string)
    dates_series = pd.to_datetime(normalized_dates, format="%Y-%m-%d", errors="coerce").dropna()
    
    if dates_series.empty:
        # Fallback to simple string min/max if parsing fails completely
        start_date = str(merged_df["arrival_date"].min())
        end_date = str(merged_df["arrival_date"].max())
        total_days = merged_df["arrival_date"].nunique()
    else:
        start_date = dates_series.min().strftime("%Y-%m-%d")
        end_date = dates_series.max().strftime("%Y-%m-%d")
        total_days = (dates_series.max() - dates_series.min()).days + 1
        # If min and max are the same, total days is 1
        if total_days <= 0:
            total_days = 1

    date_range_str = f"{start_date} to {end_date}"

    # ── Stage 4: Run Analyzers ───────────────────────────────────────────────
    # A. Mandi analyzer
    mandi_reliability_df = analyze_mandis(merged_df, start_date, end_date)

    # B. Commodity analyzer
    commodity_analysis_df = analyze_commodities(merged_df, total_days)

    # C. Pilot selector
    pilot_crop, pilot_markets, scored_commodities, reason = select_pilot(
        commodity_analysis_df,
        mandi_reliability_df,
        merged_df,
        top_n_markets=3
    )

    if not pilot_crop:
        logger.error("Pilot selection failed due to lack of commodity data.")
        sys.exit(1)

    # ── Stage 5: Generate Files ──────────────────────────────────────────────
    report_content = generate_reports(
        scored_commodities=scored_commodities,
        mandi_reliability=mandi_reliability_df,
        pilot_crop=pilot_crop,
        pilot_markets=pilot_markets,
        selection_reason=reason,
        total_files=total_files,
        total_records=total_records,
        start_date=start_date,
        end_date=end_date
    )

    # ── Stage 6: Format & Print the Required Terminal Summary ─────────────────
    print()
    print(report_content)
    print()


if __name__ == "__main__":
    run_analysis_pipeline()
