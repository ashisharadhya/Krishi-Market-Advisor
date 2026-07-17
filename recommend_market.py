"""
recommend_market.py

Phase 3: "which market should I sell at?"

This follows the flow Yukti sketched:
    Read CSV(s) -> read pilot crop from config -> filter to that crop ->
    compare markets -> sort by price -> recommend top market

BUT with two important additions, so the recommendation is actually
trustworthy and not just "whichever market happened to report highest
today":

  1. RELIABILITY FILTER (step 0): only recommend among markets that
     report this crop consistently across the days of data we have
     (uses the same logic as check_market_consistency.py). A market
     that shows up once with a freak high price is excluded, not
     recommended.

  2. TREND AWARENESS: if more than one day of data exists, show whether
     each reliable market's price is rising or falling, not just its
     single latest value. "Highest price today, but falling fast" is
     very different from "highest price today, and rising."

Honest limitation, stated plainly (not hidden): this does NOT account
for transport distance/cost yet. The "recommended" market is the best
by reported price among reliable markets -- a farmer should still weigh
distance themselves until we add that data. This is flagged in the
output every time, not left implicit.

Usage:
    python3 recommend_market.py --folder /path/to/csvs --config pilot_config.json
"""

import argparse
import csv
import glob
import json
import os
from collections import defaultdict


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all_csvs(folder: str) -> list[dict]:
    rows = []
    csv_files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    if not csv_files:
        print(f"No CSV files found in {folder}")
        return rows
    for path in csv_files:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    return rows


def to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def normalize_date(date_str: str) -> str:
    """
    Different pipeline runs have produced different date formats
    (YYYY-MM-DD on one day, DD/MM/YYYY on another) -- this was caught
    because it silently broke "latest price" sorting: comparing these
    as raw strings puts them in the wrong order.

    This converts any recognized format into YYYY-MM-DD so dates sort
    and compare correctly regardless of which format a given file used.
    If the format isn't recognized, the original string is returned
    unchanged (and will sort separately, which is safer than silently
    mixing it in wrong).
    """
    date_str = date_str.strip()
    if not date_str:
        return date_str

    # Already YYYY-MM-DD
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str

    # DD/MM/YYYY -> YYYY-MM-DD
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3 and len(parts[2]) == 4:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    return date_str


def find_common_variety(rows: list[dict], commodity: str) -> str:
    """
    Different varieties of the same commodity (e.g. 'Rashi' vs 'Sippegotu'
    arecanut) can have wildly different prices for reasons that have
    nothing to do with which market is better -- they're just different
    products. Comparing markets on raw commodity price alone silently
    mixes these together and produces a misleading gap.

    This finds whichever variety is reported by the MOST markets, so the
    comparison stays apples-to-apples by default.
    """
    variety_markets = defaultdict(set)
    for row in rows:
        if row.get("commodity", "").strip().lower() != commodity.strip().lower():
            continue
        variety = row.get("variety", "Unknown").strip()
        market = row.get("market", "Unknown")
        variety_markets[variety].add(market)

    if not variety_markets:
        return None

    best_variety = max(variety_markets.items(), key=lambda x: len(x[1]))[0]
    return best_variety


def find_reliable_markets(rows: list[dict], commodity: str, variety: str, threshold_pct: float) -> tuple:
    """Step 0: filter to markets that report this crop+variety consistently."""
    market_dates = defaultdict(set)
    all_dates = set()

    for row in rows:
        if row.get("commodity", "").strip().lower() != commodity.strip().lower():
            continue
        if variety and row.get("variety", "").strip().lower() != variety.strip().lower():
            continue
        market = row.get("market", "Unknown")
        date = normalize_date(row.get("arrival_date", "Unknown"))
        market_dates[market].add(date)
        all_dates.add(date)

    total_days = len(all_dates)
    if total_days == 0:
        return [], 0

    reliable = [
        market for market, dates in market_dates.items()
        if (len(dates) / total_days) * 100 >= threshold_pct
    ]
    return reliable, total_days


def build_price_history(rows: list[dict], commodity: str, variety: str, markets: list[str]) -> dict:
    """
    market -> sorted list of (date, modal_price)

    Filters to a SPECIFIC variety, not just the commodity name, so we
    never average or compare across products that only share a label.

    Also guards against a second real issue: a market can report the
    SAME crop+variety multiple times on the SAME day (e.g. different
    grades within that variety). Those get averaged into one daily
    price first, so a same-day duplicate is never mistaken for a
    second day's data point when computing trend.
    """
    daily_prices = defaultdict(list)  # (market, date) -> [prices]
    for row in rows:
        if row.get("commodity", "").strip().lower() != commodity.strip().lower():
            continue
        if variety and row.get("variety", "").strip().lower() != variety.strip().lower():
            continue
        market = row.get("market", "Unknown")
        if market not in markets:
            continue
        date = normalize_date(row.get("arrival_date", "Unknown"))
        price = to_float(row.get("modal_price"))
        if price is not None:
            daily_prices[(market, date)].append(price)

    history = defaultdict(list)
    for (market, date), prices in daily_prices.items():
        avg_price = sum(prices) / len(prices)
        history[market].append((date, avg_price))

    for market in history:
        history[market].sort(key=lambda x: x[0])
    return history


def recommend(history: dict) -> None:
    if not history:
        print("No reliable markets with price data found. Cannot make a recommendation yet.")
        print("This usually means: not enough days of data collected, or the pilot")
        print("crop name doesn't match exactly how it's spelled in the CSV.")
        return

    latest_snapshot = []
    any_trend_known = False
    for market, points in history.items():
        latest_date, latest_price = points[-1]
        if len(points) >= 2:
            prev_price = points[-2][1]
            change = latest_price - prev_price
            trend = "rising" if change > 0 else ("falling" if change < 0 else "flat")
            trend_str = f"{trend} ({change:+.0f} vs previous reading)"
            any_trend_known = True
        else:
            trend_str = "Trend Analysis: Not Available (Insufficient historical data)"
        latest_snapshot.append((market, latest_price, latest_date, trend_str))

    latest_snapshot.sort(key=lambda x: -x[1])

    print(f"{'Market':<35}{'Latest modal price':<20}{'Date':<14}{'Trend'}")
    print("-" * 100)
    for market, price, date, trend_str in latest_snapshot:
        print(f"{market:<35}{price:<20.0f}{date:<14}{trend_str}")

    prices = [p for _, p, _, _ in latest_snapshot]
    highest_market, highest_price, top_date, top_trend = latest_snapshot[0]
    lowest_market, lowest_price = latest_snapshot[-1][0], latest_snapshot[-1][1]
    average_price = sum(prices) / len(prices)
    extra_earnings = highest_price - lowest_price
    extra_earnings_pct = (extra_earnings / lowest_price * 100) if lowest_price else 0

    print(f"\nSUMMARY")
    print(f"  Highest price : {highest_price:.0f}  ({highest_market})")
    print(f"  Lowest price  : {lowest_price:.0f}  ({lowest_market})")
    print(f"  Average price : {average_price:.0f}  (across {len(prices)} reliable markets)")
    print(f"  Extra earnings selling at the highest vs the lowest market: "
          f"{extra_earnings:.0f} per quintal ({extra_earnings_pct:.0f}% more)")

    print(f"\nRECOMMENDATION: {highest_market}")
    print(f"  Highest reported price among reliable markets: {highest_price:.0f} (as of {top_date})")
    print(f"  Trend: {top_trend}")
    if not any_trend_known:
        print(f"\n  Trend Analysis: Not Available (Insufficient historical data)")
    print(f"\nIMPORTANT - this does NOT account for transport distance or cost yet.")
    print(f"A market with a slightly lower price but much closer to you could still")
    print(f"be the better real choice. Weigh distance yourself for now.")


def main():
    parser = argparse.ArgumentParser(description="Recommend the best market for the pilot crop")
    parser.add_argument("--folder", required=True, help="Folder containing daily CSV files")
    parser.add_argument("--config", default="pilot_config.json", help="Path to pilot_config.json")
    args = parser.parse_args()

    config = load_config(args.config)
    commodity = config["pilot_crop"]
    threshold = config.get("reliability_threshold_pct", 70)
    configured_variety = config.get("pilot_variety")  # may be None

    rows = load_all_csvs(args.folder)
    if not rows:
        return

    if configured_variety:
        variety = configured_variety
        print(f"Using configured variety: {variety}")
    else:
        variety = find_common_variety(rows, commodity)
        print(f"No variety set in config - auto-selected '{variety}' "
              f"(the variety reported by the most markets, for a fair comparison)")

    reliable_markets, total_days = find_reliable_markets(rows, commodity, variety, threshold)
    print(f"\nPilot crop: {commodity}")
    print(f"Variety being compared: {variety}")
    print(f"Days of data available: {total_days}")
    print(f"Reliable markets (>= {threshold}% of days): {len(reliable_markets)}")
    if reliable_markets:
        print(f"  {reliable_markets}")
    print()

    if total_days < 3:
        print("NOTE: fewer than 3 days of data collected so far.")
        print("Reliability and trend results below are a preview, not final.\n")

    history = build_price_history(rows, commodity, variety, reliable_markets)
    recommend(history)


if __name__ == "__main__":
    main()
