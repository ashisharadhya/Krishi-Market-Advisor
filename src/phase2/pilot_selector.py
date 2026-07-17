# src/phase2/pilot_selector.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Evaluate commodities and select the best pilot crop and its best pilot mandis.
#   Uses a multi-criteria scoring algorithm based on market breadth, volume,
#   completeness, and reporting consistency.
# ─────────────────────────────────────────────────────────────────────────────

import logging
import pandas as pd

logger = logging.getLogger("krishi")


def select_pilot(
    commodity_df: pd.DataFrame,
    mandi_df: pd.DataFrame,
    merged_df: pd.DataFrame,
    top_n_markets: int = 3
) -> tuple:
    """
    Score all commodities, select the best pilot crop, and its top pilot markets.

    Scoring Logic:
      - We normalize unique_markets and records into [0, 1] scales.
      - Score = (Normalized Markets * 0.3) + (Normalized Records * 0.3)
                + (Completeness * 0.2) + (Consistency * 0.2)
      - The highest scoring commodity is selected as the Pilot Crop.
      - Top pilot markets are selected by finding all mandis that report the
        chosen Pilot Crop, sorted by the Mandi Reliability Score.

    Args:
        commodity_df (pd.DataFrame): Output from commodity_analyzer.
        mandi_df (pd.DataFrame): Output from mandi_analyzer.
        merged_df (pd.DataFrame): Merged raw transaction DataFrame.
        top_n_markets (int): Number of top reliable mandis to select.

    Returns:
        tuple: (pilot_crop_name, pilot_markets_list, scored_commodity_df, selection_reason)
    """
    logger.info("Running pilot selection algorithm...")

    if commodity_df.empty:
        logger.error("Cannot select pilot crop: commodity analysis is empty.")
        return None, [], commodity_df, "No data available."

    # Copy the DataFrame to avoid modifying the original
    scored_df = commodity_df.copy()

    # ── Normalize Unique Markets ──────────────────────────────────────────────
    max_markets = scored_df["unique_markets"].max()
    min_markets = scored_df["unique_markets"].min()
    if max_markets > min_markets:
        scored_df["norm_markets"] = (scored_df["unique_markets"] - min_markets) / (max_markets - min_markets)
    else:
        scored_df["norm_markets"] = 1.0

    # ── Normalize Records ─────────────────────────────────────────────────────
    max_records = scored_df["records"].max()
    min_records = scored_df["records"].min()
    if max_records > min_records:
        scored_df["norm_records"] = (scored_df["records"] - min_records) / (max_records - min_records)
    else:
        scored_df["norm_records"] = 1.0

    # ── Calculate Pilot Score ─────────────────────────────────────────────────
    # Weights:
    #   - norm_markets: 0.3  (we want a crop with wide representation across mandis)
    #   - norm_records: 0.3  (we want high volume of data points)
    #   - completeness: 0.2  (we want valid price & arrival counts)
    #   - consistency: 0.2   (we want reports on most of the days)
    scored_df["pilot_score"] = (
        (scored_df["norm_markets"] * 0.3) +
        (scored_df["norm_records"] * 0.3) +
        (scored_df["completeness"] * 0.2) +
        (scored_df["consistency"] * 0.2)
    )

    # Sort descending by pilot score
    scored_df = scored_df.sort_values(by="pilot_score", ascending=False).reset_index(drop=True)

    # Get the best crop (row index 0)
    best_row = scored_df.iloc[0]
    pilot_crop = best_row["commodity"]
    pilot_score = best_row["pilot_score"]

    logger.info(f"Selected Pilot Crop: '{pilot_crop}' with a Pilot Score of {pilot_score:.4f}")

    # ── Select Best Pilot Mandis for the Selected Pilot Crop ──────────────────
    # Filter merged raw data to get all transactions for the pilot crop
    pilot_crop_transactions = merged_df[merged_df["commodity"] == pilot_crop]

    # Find unique markets reporting this crop
    reporting_markets = pilot_crop_transactions["market"].unique()

    # Match these markets with their reliability scores from mandi_df
    crop_markets_reliability = mandi_df[mandi_df["mandi"].isin(reporting_markets)].copy()

    # Sort by reliability score (and secondary: days reported) descending
    crop_markets_reliability = crop_markets_reliability.sort_values(
        by=["reliability_score", "days_reported"],
        ascending=False
    )

    # Take the top N markets
    pilot_markets = crop_markets_reliability["mandi"].head(top_n_markets).tolist()

    # Formulate the selection reason
    reason = (
        f"Selected '{pilot_crop}' because it achieved the highest score ({pilot_score:.4f}) "
        f"across multiple criteria: reported by {int(best_row['unique_markets'])} mandis "
        f"with {int(best_row['records'])} total records, "
        f"data completeness of {best_row['completeness']:.1%}, and "
        f"reporting consistency of {best_row['consistency']:.1%} over the date range."
    )

    logger.info(f"Selected Pilot Mandis: {pilot_markets}")
    logger.info(f"Reasoning: {reason}")

    return pilot_crop, pilot_markets, scored_df, reason
