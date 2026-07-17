# main.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Entry point for the Krishi Market Advisor Phase 1 pipeline.
#
#   Run this file to execute the complete data collection process:
#     1. Set up logging and directories
#     2. Connect to the data.gov.in OGD API
#     3. Download all Karnataka mandi price records
#     4. Validate and clean the data
#     5. Save the cleaned data as a dated CSV file
#     6. Print a summary to the terminal
#
# HOW TO RUN:
#   python main.py
#
# PREREQUISITE:
#   - Copy .env.example to .env
#   - Add your data.gov.in API key: DATA_GOV_IN_API_KEY=your_key_here
#   - Install dependencies: pip install -r requirements.txt
# ─────────────────────────────────────────────────────────────────────────────

import sys
import logging

# Import our pipeline modules from the src/ package
from src.utils import setup_logging, ensure_directories, get_today_filepath, print_summary
from src.fetch_mandi_prices import (
    fetch_all_records,
    filter_karnataka,
    validate_data,
    clean_data,
    save_data,
)


def run_pipeline() -> None:
    """
    Orchestrate the full Phase 1 data collection pipeline.

    This function calls each stage of the pipeline in sequence.
    If any stage fails, the error is logged and the program exits cleanly.
    """

    # ── Stage 1: Setup ─────────────────────────────────────────────────────
    # Create the data/ and logs/ directories if they don't exist yet
    ensure_directories()

    # Set up logging (writes to both the terminal and the log file)
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("Krishi Market Advisor — Phase 1 Pipeline Starting")
    logger.info("=" * 60)

    # Track counts for the final summary
    records_downloaded = 0
    karnataka_records = 0
    output_filepath = get_today_filepath()
    success = False

    # Check if today's CSV file already exists
    if output_filepath.exists():
        msg = "Today's data already exists."
        print(msg)
        logger.info(msg)
        return

    try:
        # ── Stage 2: Download Data ─────────────────────────────────────────
        logger.info("Stage 2: Downloading mandi price data from data.gov.in ...")
        raw_df = fetch_all_records()
        records_downloaded = len(raw_df)
        logger.info(f"Total records downloaded: {records_downloaded:,}")

        # ── Stage 3: Filter Karnataka ──────────────────────────────────────
        logger.info("Stage 3: Filtering Karnataka records ...")
        karnataka_df = filter_karnataka(raw_df)
        karnataka_records = len(karnataka_df)

        if karnataka_records == 0:
            logger.error(
                "No Karnataka records found after filtering. "
                "This may be a data availability issue — try again later."
            )
            print_summary(records_downloaded, 0, output_filepath, success=False)
            sys.exit(1)

        # ── Stage 4: Validate Data ─────────────────────────────────────────
        logger.info("Stage 4: Validating data ...")
        is_valid = validate_data(karnataka_df)

        if not is_valid:
            logger.error("Data validation failed. Aborting pipeline.")
            print_summary(records_downloaded, karnataka_records, output_filepath, success=False)
            sys.exit(1)

        # ── Stage 5: Clean Data ────────────────────────────────────────────
        logger.info("Stage 5: Cleaning data ...")
        cleaned_df = clean_data(karnataka_df)

        # Update count after cleaning (duplicates may have been removed)
        karnataka_records = len(cleaned_df)

        # ── Stage 6: Save Data ─────────────────────────────────────────────
        logger.info("Stage 6: Saving cleaned data to CSV ...")
        save_data(cleaned_df, output_filepath)

        # Mark the pipeline as successful
        success = True
        logger.info("=" * 60)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 60)

    except ValueError as e:
        # Catches configuration errors (e.g., missing API key)
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    except RuntimeError as e:
        # Catches runtime errors (e.g., no records returned)
        logger.error(f"Runtime error: {e}")
        sys.exit(1)

    except Exception as e:
        # Catches any unexpected errors so the program exits cleanly
        logger.exception(f"Unexpected error in pipeline: {e}")
        sys.exit(1)

    finally:
        # Always print the summary — even if an error occurred
        # This gives the user useful feedback regardless of outcome
        print_summary(
            records_downloaded=records_downloaded,
            karnataka_records=karnataka_records,
            output_filepath=output_filepath,
            success=success,
        )


# ─────────────────────────────────────────────────────────────────────────────
# STANDARD PYTHON ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
# This block only runs when the script is executed directly:
#   python main.py
#
# It does NOT run when main.py is imported as a module from another file.
# This is a Python best practice for all executable scripts.
if __name__ == "__main__":
    run_pipeline()
