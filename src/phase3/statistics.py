# src/phase3/statistics.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Calculate aggregated market statistics (highest, lowest, average, difference,
#   and estimated extra earnings) for the selected crop.
# ─────────────────────────────────────────────────────────────────────────────

import logging
import pandas as pd

logger = logging.getLogger("krishi")


def calculate_market_statistics(comparison_df: pd.DataFrame) -> dict:
    """
    Calculate summary statistics from the ranked market comparison DataFrame.

    Args:
        comparison_df (pd.DataFrame): Output from comparator.py.

    Returns:
        dict: Dictionary containing calculated metrics:
              - markets_compared
              - highest_modal_price
              - lowest_modal_price
              - average_modal_price
              - price_range
              - estimated_extra_earnings
    """
    logger.info("Calculating market statistics...")

    if comparison_df.empty:
        logger.warning("Empty comparison DataFrame. Returning default empty stats.")
        return {
            "markets_compared": 0,
            "highest_modal_price": 0.0,
            "lowest_modal_price": 0.0,
            "average_modal_price": 0.0,
            "price_range": 0.0,
            "estimated_extra_earnings": 0.0
        }

    prices = comparison_df["Modal Price"]
    
    markets_compared = len(comparison_df)
    highest_modal_price = float(prices.max())
    lowest_modal_price = float(prices.min())
    average_modal_price = float(prices.mean())
    price_range = highest_modal_price - lowest_modal_price
    
    # Estimated Extra Earnings per Quintal is the difference between the
    # Recommended Market (highest modal price) and the average price.
    estimated_extra_earnings = highest_modal_price - average_modal_price

    stats = {
        "markets_compared": markets_compared,
        "highest_modal_price": highest_modal_price,
        "lowest_modal_price": lowest_modal_price,
        "average_modal_price": average_modal_price,
        "price_range": price_range,
        "estimated_extra_earnings": estimated_extra_earnings
    }

    logger.info(
        f"Stats calculated: Compared={markets_compared}, Max={highest_modal_price:.2f}, "
        f"Min={lowest_modal_price:.2f}, Avg={average_modal_price:.2f}, Extra Earnings={estimated_extra_earnings:.2f}"
    )
    return stats
