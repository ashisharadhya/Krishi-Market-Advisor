# src/phase2/commodity_analyzer.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Analyze commodity data collected across all mandi price CSV files.
#   Computes counts, unique market participation, completeness metrics,
#   and consistency of reports over time to help score each commodity's
#   suitability for pilot programs.
# ─────────────────────────────────────────────────────────────────────────────

import logging
import pandas as pd

logger = logging.getLogger("krishi")


def analyze_commodities(df: pd.DataFrame, total_days: int) -> pd.DataFrame:
    """
    Perform statistical analysis on each commodity in the merged dataset.

    Calculates:
      1. Total Records (rows of data for this commodity)
      2. Unique Markets (number of distinct mandis reporting this commodity)
      3. Completeness (percentage of rows with positive prices and arrivals)
      4. Consistency (percentage of total days this commodity was reported)

    Args:
        df (pd.DataFrame): The merged mandi price DataFrame.
        total_days (int): The total number of unique days available in the dataset.

    Returns:
        pd.DataFrame: A DataFrame indexed by commodity with columns:
                      - records: Total number of rows
                      - unique_markets: Count of unique reporting markets
                      - completeness: Ratio of complete records (non-null/positive modal_price & arrivals)
                      - consistency: Ratio of unique reporting days to total available days
    """
    logger.info("Starting commodity reliability analysis...")

    # Group by commodity to gather aggregates
    commodity_stats = []

    for commodity_name, group in df.groupby("commodity"):
        # 1. Total records count
        records_count = len(group)

        # 2. Count of unique markets/mandis
        unique_markets_count = group["market"].nunique()

        # 3. Completeness check
        # We define a record as complete if 'modal_price' and 'arrivals' are positive and non-null
        # First, ensure we handle missing values correctly (using float checks)
        try:
            modal_prices = pd.to_numeric(group["modal_price"], errors="coerce").fillna(0)
            arrivals = pd.to_numeric(group["arrivals"], errors="coerce").fillna(0)
            complete_mask = (modal_prices > 0) & (arrivals > 0)
            complete_count = complete_mask.sum()
            completeness_ratio = float(complete_count / records_count) if records_count > 0 else 0.0
        except Exception as e:
            logger.warning(f"Error computing completeness for {commodity_name}: {e}")
            completeness_ratio = 0.0

        # 4. Consistency check
        # Consistency is how many unique days this commodity has at least one report
        # relative to the total number of days available in the date range
        try:
            unique_days_reported = group["arrival_date"].nunique()
            consistency_ratio = float(unique_days_reported / total_days) if total_days > 0 else 0.0
        except Exception as e:
            logger.warning(f"Error computing consistency for {commodity_name}: {e}")
            consistency_ratio = 0.0

        commodity_stats.append({
            "commodity": commodity_name,
            "records": records_count,
            "unique_markets": unique_markets_count,
            "completeness": completeness_ratio,
            "consistency": consistency_ratio
        })

    # Convert analysis list to a DataFrame
    analysis_df = pd.DataFrame(commodity_stats)

    if analysis_df.empty:
        logger.warning("No commodities found during analysis.")
        return pd.DataFrame(columns=["commodity", "records", "unique_markets", "completeness", "consistency"])

    analysis_df = analysis_df.sort_values(by="records", ascending=False)
    logger.info(f"Analyzed {len(analysis_df)} commodities successfully.")
    return analysis_df
