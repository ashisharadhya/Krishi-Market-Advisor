"""
check_market_consistency.py

Phase 2 validation: once multiple days of CSVs have accumulated, this
checks which markets ACTUALLY report a given commodity reliably, day
after day -- not just on one lucky snapshot.

This settles the open question from the Phase 2 report: "markets with
consistent reporting" needs multi-day evidence, not a single day's pull.

Usage:
    python3 check_market_consistency.py --folder /path/to/csvs --commodity "Arecanut(Betelnut/Supari)"

Expects CSVs with at least these columns (matches Yukti's cleaned schema):
    market, commodity, modal_price, arrival_date
(Extra columns are fine and ignored.)
"""

import argparse
import csv
import glob
import os
from collections import defaultdict


def load_all_csvs(folder: str) -> list[dict]:
    rows = []
    csv_files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    if not csv_files:
        print(f"No CSV files found in {folder}")
        return rows

    print(f"Found {len(csv_files)} CSV file(s):")
    for path in csv_files:
        print(f"  - {os.path.basename(path)}")
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    print()
    return rows


def check_consistency(rows: list[dict], commodity: str) -> None:
    # market -> set of dates it reported this commodity
    market_dates = defaultdict(set)
    # market -> list of (date, modal_price) for trend view
    market_prices = defaultdict(list)

    all_dates = set()

    for row in rows:
        if row.get("commodity", "").strip().lower() != commodity.strip().lower():
            continue
        market = row.get("market", "Unknown")
        date = row.get("arrival_date", "Unknown")
        price = row.get("modal_price", "")
        market_dates[market].add(date)
        market_prices[market].append((date, price))
        all_dates.add(date)

    total_days = len(all_dates)
    if total_days == 0:
        print(f"No records found for commodity '{commodity}' in the data provided.")
        return

    print(f"Commodity: {commodity}")
    print(f"Total distinct days in dataset: {total_days}")
    print(f"Dates seen: {sorted(all_dates)}\n")

    print(f"{'Market':<35}{'Days reported':<16}{'Reliability'}")
    print("-" * 75)

    reliable_markets = []
    for market, dates in sorted(market_dates.items(), key=lambda x: -len(x[1])):
        days_reported = len(dates)
        reliability_pct = (days_reported / total_days) * 100
        tag = "RELIABLE" if reliability_pct >= 70 else (
              "PARTIAL" if reliability_pct >= 40 else "SPARSE")
        if tag == "RELIABLE":
            reliable_markets.append(market)
        print(f"{market:<35}{days_reported}/{total_days:<14}{reliability_pct:.0f}% - {tag}")

    print()
    if reliable_markets:
        print(f"{len(reliable_markets)} market(s) report '{commodity}' reliably (70%+ of days):")
        for m in reliable_markets:
            print(f"  - {m}")
        print("\nThese are the markets safe to build comparison logic on.")
    else:
        print("No market meets the 70% reliability bar yet.")
        print("This usually means: not enough days of data collected yet.")
        print("Keep accumulating daily pulls and re-run this check.")

    # Only meaningful with 2+ days of data
    if total_days < 3:
        print("\nNote: fewer than 3 days of data collected so far.")
        print("Reliability percentages will firm up as more days accumulate.")
        print("Treat this run as a preview, not a final answer.")


def main():
    parser = argparse.ArgumentParser(description="Check multi-day market reporting consistency")
    parser.add_argument("--folder", required=True, help="Folder containing daily CSV files")
    parser.add_argument("--commodity", default="Arecanut(Betelnut/Supari)",
                         help="Commodity to check (must match exactly as it appears in the data)")
    args = parser.parse_args()

    rows = load_all_csvs(args.folder)
    if rows:
        check_consistency(rows, args.commodity)


if __name__ == "__main__":
    main()
