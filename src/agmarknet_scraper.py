# src/agmarknet_scraper.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Fallback data source for the Krishi Market Advisor pipeline.
#   Uses the Agmarknet 2.0 internal REST API (api.agmarknet.gov.in/v1)
#   which powers the official agmarknet.gov.in portal.
#
# HOW IT WORKS:
#   Agmarknet 2.0 is a React single-page application. The frontend calls a
#   backend REST API to fetch price data. By discovering these endpoints from
#   the app's JavaScript bundle, we can call them directly with requests —
#   no scraping, no JavaScript, no browser needed.
#
# KEY ENDPOINT DISCOVERED:
#   GET https://api.agmarknet.gov.in/v1/prices-and-arrivals/commodity-market/daily-report-state
#   Params: state=16 (Karnataka's ID), date=YYYY-MM-DD
#   Returns: Nested JSON with commodity groups → commodities → market rows
#
# RESPONSE STRUCTURE:
#   {
#     "success": true,
#     "commodityGroups": [
#       {
#         "CommodityGroup": "Cereals",
#         "commodities": [
#           {
#             "commodityName": "Jowar",
#             "markets": [
#               {
#                 "marketCenter": "Bellary APMC",
#                 "data": [
#                   {
#                     "variety": "Hybrid",
#                     "minimumPrice": 2232.0,
#                     "maximumPrice": 2709.0,
#                     "modalPrice": 2569.0,
#                     "arrivals": 13.8,
#                     "unitOfArrivals": "Metric Tonnes",
#                     "unitOfPrice": "Rs./Quintal"
#                   }
#                 ]
#               }
#             ]
#           }
#         ]
#       }
#     ]
#   }
# ─────────────────────────────────────────────────────────────────────────────

import logging
from datetime import date

import pandas as pd
import requests

from src.config import Config

# Get the named logger configured in utils.setup_logging()
logger = logging.getLogger("krishi")


def fetch_from_agmarknet(target_date: date = None) -> pd.DataFrame:
    """
    Fetch Karnataka mandi price data from the Agmarknet 2.0 internal REST API.

    This function calls the backend API that powers the official Agmarknet 2.0
    portal (agmarknet.gov.in). The endpoint was discovered by inspecting the
    React application's JavaScript bundle.

    The response has a nested structure (commodity groups → commodities → markets).
    This function flattens it into a clean tabular DataFrame — one row per
    commodity–variety–market combination.

    Args:
        target_date (date): The date to fetch prices for. Defaults to today.

    Returns:
        pd.DataFrame: Flat DataFrame with columns:
            state, district (None), market, commodity_group, commodity,
            variety, arrivals, unit_of_arrivals, min_price, max_price,
            modal_price, unit_of_price, arrival_date

    Raises:
        requests.exceptions.Timeout: If the API doesn't respond in time.
        requests.exceptions.ConnectionError: If the API is unreachable.
        requests.exceptions.HTTPError: If the API returns an HTTP error.
        RuntimeError: If the response contains no data.
    """
    if target_date is None:
        target_date = date.today()

    # Format date as YYYY-MM-DD (required by the Agmarknet 2.0 API)
    date_str = target_date.strftime("%Y-%m-%d")

    # Build the full API URL
    url = Config.AGMARKNET_API_BASE + Config.AGMARKNET_DAILY_ENDPOINT

    logger.info(
        f"Agmarknet 2.0 API: Fetching Karnataka data for {date_str} ..."
    )
    logger.debug(f"URL: {url} | state={Config.KARNATAKA_STATE_ID}")

    # ── Make the API Request ───────────────────────────────────────────────
    response = requests.get(
        url,
        headers=Config.AGMARKNET_HEADERS,
        params={
            "state": Config.KARNATAKA_STATE_ID,   # 16 = Karnataka
            "date": date_str,
        },
        timeout=Config.AGMARKNET_TIMEOUT,
    )

    # Raise an exception if the server returned an HTTP error code
    response.raise_for_status()

    # Parse the JSON response body
    data = response.json()

    # Verify the API reported success
    if not data.get("success", False):
        raise RuntimeError(
            f"Agmarknet 2.0 API returned success=False. "
            f"Message: {data.get('message', 'No message')}"
        )

    logger.info(f"Agmarknet 2.0 API responded successfully.")

    # ── Flatten the Nested JSON into a Flat Table ─────────────────────────
    # The response is nested 3 levels deep:
    #   commodityGroups → commodities → markets → data (variety rows)
    # We flatten this into one row per variety per market per commodity.
    flat_rows = []

    commodity_groups = data.get("commodityGroups", [])
    logger.debug(f"Number of commodity groups received: {len(commodity_groups)}")

    for group in commodity_groups:
        # Each group has a name (e.g., "Cereals", "Vegetables") and a list of commodities
        group_name = group.get("CommodityGroup", "Unknown")
        commodities = group.get("commodities", [])

        for commodity in commodities:
            # Each commodity has a name and a list of markets where it was traded
            commodity_name = commodity.get("commodityName") or "Unknown"
            markets = commodity.get("markets", [])

            for market in markets:
                # Each market has a name and a list of variety-level price records
                market_name = market.get("marketCenter", "Unknown")
                price_entries = market.get("data", [])

                for entry in price_entries:
                    # Each entry is one variety's price record at this market
                    # Build a single flat row with all relevant fields
                    row = {
                        "state":            Config.TARGET_STATE,      # Always "Karnataka"
                        "district":         None,                      # Not available at this level
                        "market":           market_name,
                        "commodity_group":  group_name,
                        "commodity":        commodity_name,
                        "variety":          entry.get("variety", "Unknown"),
                        "arrivals":         entry.get("arrivals"),
                        "unit_of_arrivals": entry.get("unitOfArrivals", "Metric Tonnes"),
                        "min_price":        entry.get("minimumPrice"),
                        "max_price":        entry.get("maximumPrice"),
                        "modal_price":      entry.get("modalPrice"),
                        "unit_of_price":    entry.get("unitOfPrice", "Rs./Quintal"),
                        "arrival_date":     date_str,
                    }
                    flat_rows.append(row)

    # ── Validate We Got Some Data ──────────────────────────────────────────
    if not flat_rows:
        raise RuntimeError(
            f"Agmarknet 2.0 API returned success=True but no price records "
            f"for Karnataka on {date_str}. "
            f"Market data may not be available for this date (e.g., holiday)."
        )

    # Convert list of flat dicts to a pandas DataFrame
    df = pd.DataFrame(flat_rows)

    logger.info(
        f"Agmarknet 2.0 scraper: successfully flattened {len(df):,} records "
        f"across {len(commodity_groups)} commodity groups."
    )

    return df
