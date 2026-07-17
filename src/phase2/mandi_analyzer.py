# src/phase2/mandi_analyzer.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Analyze market (mandi) reporting behavior.
#   Computes how consistently each mandi reports data, calculates reliability
#   scores, and identifies missing reporting days within the overall date range.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger("krishi")


def get_all_dates_in_range(start_date_str: str, end_date_str: str) -> list:
    """
    Generate a list of all date strings (YYYY-MM-DD) between start and end dates.

    Args:
        start_date_str (str): Start date string.
        end_date_str (str): End date string.

    Returns:
        list: Sorted list of date strings (YYYY-MM-DD) representing the calendar range.
    """
    try:
        # Parse dates. Agmarknet dates could be YYYY-MM-DD or DD/MM/YYYY.
        # We try YYYY-MM-DD first since our pipeline outputs it that way.
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        # Fallback to alternate format if dates differ
        try:
            start_dt = datetime.strptime(start_date_str, "%d/%m/%Y")
            end_dt = datetime.strptime(end_date_str, "%d/%m/%Y")
        except ValueError as e:
            logger.error(f"Failed to parse dates for range generation: {e}")
            return [start_date_str]

    # Generate range of days
    delta = end_dt - start_dt
    date_list = []
    for i in range(delta.days + 1):
        day = start_dt + timedelta(days=i)
        date_list.append(day.strftime("%Y-%m-%d"))
    return sorted(date_list)


def analyze_mandis(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Analyze the reporting frequency and reliability of each mandi.

    Calculates:
      1. Days Reported (unique dates the mandi appears in the dataset)
      2. Reliability Score (Days Reported / Total Days Available in date range)
      3. Missing Dates (a comma-separated list of dates the mandi did not report)

    Args:
        df (pd.DataFrame): Merged mandi price DataFrame.
        start_date (str): Min date in the entire dataset (format: YYYY-MM-DD).
        end_date (str): Max date in the entire dataset (format: YYYY-MM-DD).

    Returns:
        pd.DataFrame: A DataFrame representing mandi statistics, sorted by
                      reliability descending. Columns:
                      - mandi: Name of the market/mandi
                      - days_reported: Number of unique days reported
                      - reliability_score: Ratio of days reported to total days
                      - missing_days: Comma-separated list of missing date strings
    """
    logger.info("Starting mandi reliability analysis...")

    # Get the complete list of days that should have been reported
    all_dates = get_all_dates_in_range(start_date, end_date)
    total_days = len(all_dates)
    logger.info(f"Temporal analysis window: {start_date} to {end_date} ({total_days} total days)")

    mandi_stats = []

    for mandi_name, group in df.groupby("market"):
        # 1. Unique dates reported by this mandi
        # Normalize date format to YYYY-MM-DD for consistency
        reported_dates_raw = group["arrival_date"].unique()
        reported_dates = set()

        for d_str in reported_dates_raw:
            try:
                # Try parsing as YYYY-MM-DD
                parsed_dt = datetime.strptime(str(d_str).strip(), "%Y-%m-%d")
                reported_dates.add(parsed_dt.strftime("%Y-%m-%d"))
            except ValueError:
                try:
                    # Try parsing as DD/MM/YYYY
                    parsed_dt = datetime.strptime(str(d_str).strip(), "%d/%m/%Y")
                    reported_dates.add(parsed_dt.strftime("%Y-%m-%d"))
                except ValueError:
                    # Fallback to direct string representation if unparseable
                    reported_dates.add(str(d_str).strip())

        days_reported_count = len(reported_dates)

        # 2. Calculate Reliability Score
        reliability_score = float(days_reported_count / total_days) if total_days > 0 else 0.0

        # 3. Find missing reporting days
        missing_dates = [d for d in all_dates if d not in reported_dates]
        missing_dates_str = ", ".join(missing_dates) if missing_dates else "None"

        mandi_stats.append({
            "mandi": mandi_name,
            "days_reported": days_reported_count,
            "reliability_score": reliability_score,
            "missing_days": missing_dates_str
        })

    # Convert to DataFrame
    mandi_df = pd.DataFrame(mandi_stats)

    if mandi_df.empty:
        logger.warning("No mandis found during analysis.")
        return pd.DataFrame(columns=["mandi", "days_reported", "reliability_score", "missing_days"])

    # Rank all mandis from highest reliability to lowest
    mandi_df = mandi_df.sort_values(by=["reliability_score", "days_reported"], ascending=False)
    logger.info(f"Ranked {len(mandi_df)} mandis by reliability.")
    return mandi_df
