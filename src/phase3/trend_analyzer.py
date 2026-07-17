# src/phase3/trend_analyzer.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Analyze price trends between the latest daily data and the previous daily
#   data if available.
# ─────────────────────────────────────────────────────────────────────────────

import logging
import pandas as pd

logger = logging.getLogger("krishi")


def analyze_trend(latest_df: pd.DataFrame, previous_df: pd.DataFrame, crop: str) -> dict:
    """
    Compare average modal prices of the selected crop between the latest and
    previous day to analyze price trends.

    Args:
        latest_df (pd.DataFrame): Data from the latest CSV.
        previous_df (pd.DataFrame): Data from the previous CSV (if any).
        crop (str): Selected crop name.

    Returns:
        dict: Trend metrics and status.
    """
    logger.info("Analyzing price trends...")

    if previous_df is None or previous_df.empty:
        logger.info("Insufficient historical data available for trend calculation.")
        return {
            "trend_status": "Not Available",
            "reason": "Insufficient historical data."
        }

    # 1. Filter and compute average price for latest day
    crop_lower = crop.strip().lower()
    
    latest_crop_df = latest_df[latest_df["commodity"].str.strip().str.lower() == crop_lower].copy()
    latest_crop_df["modal_price"] = pd.to_numeric(latest_crop_df["modal_price"], errors="coerce")
    latest_valid = latest_crop_df[latest_crop_df["modal_price"] > 0]
    
    # 2. Filter and compute average price for previous day
    previous_crop_df = previous_df[previous_df["commodity"].str.strip().str.lower() == crop_lower].copy()
    previous_crop_df["modal_price"] = pd.to_numeric(previous_crop_df["modal_price"], errors="coerce")
    previous_valid = previous_crop_df[previous_crop_df["modal_price"] > 0]

    if latest_valid.empty or previous_valid.empty:
        logger.warning("Missing price records for the crop in one or both days. Trend not available.")
        return {
            "trend_status": "Not Available",
            "reason": "Insufficient historical data."
        }

    current_price = float(latest_valid["modal_price"].mean())
    previous_price = float(previous_valid["modal_price"].mean())
    
    price_diff = current_price - previous_price
    
    if previous_price > 0:
        pct_change = (price_diff / previous_price) * 100
    else:
        pct_change = 0.0

    # 3. Determine trend direction
    if price_diff > 0:
        direction = "↑ Increasing"
    elif price_diff < 0:
        direction = "↓ Decreasing"
    else:
        direction = "→ Stable"

    trend_data = {
        "trend_status": "Available",
        "previous_price": previous_price,
        "current_price": current_price,
        "price_difference": price_diff,
        "percentage_change": pct_change,
        "trend_direction": direction
    }

    logger.info(
        f"Trend analysis complete: Status={trend_data['trend_status']}, "
        f"Prev={previous_price:.2f}, Curr={current_price:.2f}, Change={pct_change:.2f}% ({direction})"
    )
    return trend_data
