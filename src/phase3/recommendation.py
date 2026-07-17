# src/phase3/recommendation.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Generate recommended actions and summary text based on computed metrics
#   and trend analysis results.
# ─────────────────────────────────────────────────────────────────────────────

import logging

logger = logging.getLogger("krishi")


def generate_recommendation(stats: dict, trend: dict, recommended_market: str) -> dict:
    """
    Generate recommendation text based on statistics and trend analysis.

    Args:
        stats (dict): Calculated market statistics.
        trend (dict): Calculated trend metrics.
        recommended_market (str): Name of the market offering the highest price.

    Returns:
        dict: Recommendation results including the summary string.
    """
    logger.info("Generating recommendation summary...")

    if not recommended_market:
        logger.warning("No recommended market available.")
        return {
            "recommended_market": "N/A",
            "recommendation_summary": "No data available to make a recommendation."
        }

    # Determine summary based on trend direction
    if trend.get("trend_status") == "Available":
        direction = trend.get("trend_direction", "")
        if "Increasing" in direction:
            summary = "Prices are increasing. Selling today is favourable."
        elif "Decreasing" in direction:
            summary = "Prices are decreasing. Consider monitoring tomorrow's market."
        else:
            summary = "Prices are stable. Selling today is standard."
    else:
        summary = "Insufficient data to determine price trend. Sell based on current prices."

    rec = {
        "recommended_market": recommended_market,
        "recommendation_summary": summary
    }

    logger.info(f"Recommendation generated: Market='{recommended_market}', Summary='{summary}'")
    return rec
