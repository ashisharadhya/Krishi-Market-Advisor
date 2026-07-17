# src/phase3/comparator.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Filter, clean, and rank all Karnataka markets reporting the selected crop
#   and variety by modal price in descending order.
# ─────────────────────────────────────────────────────────────────────────────

import logging
import pandas as pd

logger = logging.getLogger("krishi")


def compare_markets(df: pd.DataFrame, crop: str, variety: str) -> pd.DataFrame:
    """
    Filter the dataset for the selected crop and variety, rank markets by modal price descending,
    and calculate differences from the highest modal price.

    Args:
        df (pd.DataFrame): Today's loaded mandi prices.
        crop (str): Selected pilot crop name.
        variety (str): Selected pilot variety name.

    Returns:
        pd.DataFrame: Ranked and compared market DataFrame containing:
                      - Rank
                      - Market
                      - Commodity
                      - Variety
                      - Modal Price
                      - Difference From Highest Price
    """
    logger.info(f"Comparing all markets for crop: '{crop}', variety: '{variety}'...")

    if df.empty:
        logger.warning("Empty DataFrame provided for comparison.")
        return pd.DataFrame(columns=["Rank", "Market", "Commodity", "Variety", "Modal Price", "Difference From Highest Price"])

    # 1. Filter for the selected crop and variety (case-insensitive to be robust)
    crop_lower = crop.strip().lower()
    variety_lower = variety.strip().lower()
    crop_mask = df["commodity"].astype(str).str.strip().str.lower() == crop_lower
    variety_mask = df["variety"].astype(str).str.strip().str.lower() == variety_lower
    filtered_df = df[crop_mask & variety_mask].copy()

    if filtered_df.empty:
        logger.warning(f"No records found for crop '{crop}' and variety '{variety}' in current dataset.")
        return pd.DataFrame(columns=["Rank", "Market", "Commodity", "Variety", "Modal Price", "Difference From Highest Price"])

    # 2. Ensure modal price is numeric and clean invalid records
    filtered_df["modal_price"] = pd.to_numeric(filtered_df["modal_price"], errors="coerce")
    
    # Drop rows with NaN or non-positive modal prices
    valid_df = filtered_df[filtered_df["modal_price"] > 0].copy()

    if valid_df.empty:
        logger.warning(f"No valid modal price records found for crop '{crop}' and variety '{variety}'.")
        return pd.DataFrame(columns=["Rank", "Market", "Commodity", "Variety", "Modal Price", "Difference From Highest Price"])

    # 3. Sort by modal_price in descending order
    # If there is a tie, sort alphabetically by market name
    sorted_df = valid_df.sort_values(by=["modal_price", "market"], ascending=[False, True]).reset_index(drop=True)

    # 4. Identify highest modal price
    highest_price = sorted_df.iloc[0]["modal_price"]

    # 5. Build compared DataFrame columns
    comparison_rows = []
    for idx, row in sorted_df.iterrows():
        modal_price_val = float(row["modal_price"])
        difference = highest_price - modal_price_val
        
        comparison_rows.append({
            "Rank": idx + 1,
            "Market": row["market"],
            "Commodity": row["commodity"],
            "Variety": row["variety"],
            "Modal Price": modal_price_val,
            "Difference From Highest Price": difference
        })

    comparison_df = pd.DataFrame(comparison_rows)
    logger.info(f"Successfully compared {len(comparison_df)} markets for '{crop}' variety '{variety}'.")
    return comparison_df
