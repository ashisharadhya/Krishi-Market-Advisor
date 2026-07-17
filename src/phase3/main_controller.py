# src/phase3/main_controller.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Main orchestrator controller for the Krishi Market Advisor Phase 3:
#   Market Comparison & Recommendation Engine.
#
# HOW TO RUN:
#   python src/phase3/main_controller.py
# ─────────────────────────────────────────────────────────────────────────────

import sys
import logging
from pathlib import Path

# Add the project root to path if needed (to support running from root)
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils import setup_logging
from src.phase3.config_loader import load_pilot_config
from src.phase3.csv_loader import scan_data_directory, load_csv_data
from src.phase3.comparator import compare_markets
from src.phase3.statistics import calculate_market_statistics
from src.phase3.trend_analyzer import analyze_trend
from src.phase3.recommendation import generate_recommendation
from src.phase3.report_generator import generate_phase3_reports

# Ensure standard output supports UTF-8 characters
sys.stdout.reconfigure(encoding='utf-8')

logger = logging.getLogger("krishi")


def run_phase3() -> None:
    """
    Orchestrate the full Phase 3 pipeline:
      1. Load config/pilot_config.json to identify selected crop.
      2. Scan data/ for daily price CSVs.
      3. Load latest CSV and compile ranked market statistics.
      4. If a previous CSV is available, run trend comparison.
      5. Formulate trend recommendations and write outputs (CSV, TXT).
      6. Output a summary report to the terminal.
    """
    # Initialize logger (re-uses krishi logger configuration)
    setup_logging()

    logger.info("=" * 60)
    logger.info("Krishi Market Advisor — Phase 3 Recommendation Engine Starting")
    logger.info("=" * 60)

    try:
        # 1. Load config
        config = load_pilot_config()
        pilot_crop = config["pilot_crop"]
        pilot_variety = config["pilot_variety"]

        # 2. Scan data directory
        csv_files = scan_data_directory()
        total_files = len(csv_files)

        if total_files == 0:
            logger.error("No daily mandi price CSV files found inside data/ directory.")
            print("\nError: No daily mandi price CSV files found. Please run Phase 1 first.")
            sys.exit(1)

        # Identify latest and previous CSV
        latest_file_path = csv_files[-1]
        latest_file_name = latest_file_path.name
        logger.info(f"Latest CSV file detected: {latest_file_name}")

        previous_file_path = None
        previous_file_name = "None"
        if total_files >= 2:
            previous_file_path = csv_files[-2]
            previous_file_name = previous_file_path.name
            logger.info(f"Previous CSV file detected for trend analysis: {previous_file_name}")

        # 3. Load latest data and perform market comparison
        latest_df = load_csv_data(latest_file_path)
        comparison_df = compare_markets(latest_df, pilot_crop, pilot_variety)

        if comparison_df.empty:
            print("\nSelected Variety")
            print(pilot_variety)
            print("No market data available today for this variety.")
            print("Please choose another variety or try again later.\n")
            return

        # 4. Calculate stats
        stats = calculate_market_statistics(comparison_df)

        # 5. Load previous data and perform trend analysis
        previous_df = None
        if previous_file_path is not None:
            previous_df = load_csv_data(previous_file_path)

        trend = analyze_trend(latest_df, previous_df, pilot_crop)

        # 6. Generate recommendation
        # The recommended market is the top market in our ranked comparison DataFrame
        recommended_market = comparison_df.iloc[0]["Market"]
        recommendation = generate_recommendation(stats, trend, recommended_market)

        # 7. Generate files and construct human-readable terminal report
        report_content = generate_phase3_reports(
            comparison_df=comparison_df,
            stats=stats,
            trend=trend,
            recommendation=recommendation,
            pilot_crop=pilot_crop,
            pilot_variety=pilot_variety,
            total_files=total_files,
            latest_file_name=latest_file_name
        )

        # 8. Output report to the console
        print()
        print(report_content)
        print()

    except Exception as e:
        logger.exception(f"Unexpected error executing Phase 3: {e}")
        print(f"\nExecution Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_phase3()
