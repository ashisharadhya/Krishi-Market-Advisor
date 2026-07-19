"""
src/phase4/recommendation_adapter.py

Programmatic wrapper around Phase 3 market recommendation logic.
Transforms raw CSV price records into structured Python dictionaries
ready for prompt building, LLM context, and Streamlit visual widgets.
"""

import os
import glob
import csv
from collections import defaultdict
from typing import Dict, Any, List, Tuple, Optional


def to_float(x) -> Optional[float]:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def normalize_date(date_str: str) -> str:
    """Normalize date strings into YYYY-MM-DD format."""
    if not date_str:
        return date_str
    date_str = date_str.strip()
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3 and len(parts[2]) == 4:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return date_str


def load_all_csvs(folder: str) -> List[Dict[str, Any]]:
    rows = []
    csv_files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    if not csv_files:
        return rows
    for path in csv_files:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    return rows


def get_available_commodities(folder: str) -> List[str]:
    """Extract list of unique commodities present in historical CSVs."""
    rows = load_all_csvs(folder)
    commodities = set()
    for row in rows:
        c = row.get("commodity", "").strip()
        if c:
            commodities.add(c)
    return sorted(list(commodities))


def get_available_varieties(folder: str, commodity: str) -> List[str]:
    """Extract list of unique varieties for a given commodity."""
    rows = load_all_csvs(folder)
    varieties = set()
    for row in rows:
        if row.get("commodity", "").strip().lower() == commodity.strip().lower():
            v = row.get("variety", "").strip()
            if v:
                varieties.add(v)
    return sorted(list(varieties))


def find_common_variety(rows: List[Dict[str, Any]], commodity: str, threshold_pct: float = 70.0) -> Optional[str]:
    variety_dates = defaultdict(lambda: defaultdict(set))
    all_dates_by_variety = defaultdict(set)

    for row in rows:
        if row.get("commodity", "").strip().lower() != commodity.strip().lower():
            continue
        variety = row.get("variety", "Unknown").strip()
        market = row.get("market", "Unknown")
        date = normalize_date(row.get("arrival_date", "Unknown"))
        variety_dates[variety][market].add(date)
        all_dates_by_variety[variety].add(date)

    if not variety_dates:
        return None

    best_variety = None
    best_reliable_count = -1
    for variety, market_dates in variety_dates.items():
        total_days = len(all_dates_by_variety[variety])
        if total_days == 0:
            continue
        reliable_count = sum(
            1 for dates in market_dates.values()
            if (len(dates) / total_days) * 100 >= threshold_pct
        )
        if reliable_count > best_reliable_count:
            best_reliable_count = reliable_count
            best_variety = variety

    return best_variety


def find_reliable_markets(rows: List[Dict[str, Any]], commodity: str, variety: Optional[str], threshold_pct: float) -> Tuple[List[str], int]:
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


def build_price_history(rows: List[Dict[str, Any]], commodity: str, variety: Optional[str], markets: List[str]) -> Dict[str, List[Tuple[str, float]]]:
    daily_prices = defaultdict(list)
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


def get_market_recommendation(
    folder: str = "data",
    commodity: str = "Arecanut(Betelnut/Supari)",
    variety: Optional[str] = None,
    threshold_pct: float = 70.0
) -> Dict[str, Any]:
    """
    Executes Phase 3 recommendation logic and returns a structured dictionary.
    """
    rows = load_all_csvs(folder)
    if not rows:
        return {
            "status": "error",
            "message": f"No CSV price data files found in '{folder}'."
        }

    selected_variety = variety
    if not selected_variety:
        selected_variety = find_common_variety(rows, commodity, threshold_pct)

    reliable_markets, total_days = find_reliable_markets(rows, commodity, selected_variety, threshold_pct)

    if not reliable_markets:
        return {
            "status": "no_reliable_markets",
            "commodity": commodity,
            "variety": selected_variety or "Unknown",
            "total_days": total_days,
            "threshold_pct": threshold_pct,
            "message": f"No reliable markets found reporting '{commodity}' (Variety: '{selected_variety}') on at least {threshold_pct}% of available days ({total_days} total days)."
        }

    history = build_price_history(rows, commodity, selected_variety, reliable_markets)

    market_entries = []
    any_trend_known = False
    for market, points in history.items():
        latest_date, latest_price = points[-1]
        if len(points) >= 2:
            prev_price = points[-2][1]
            change = latest_price - prev_price
            trend = "rising" if change > 0 else ("falling" if change < 0 else "flat")
            trend_desc = f"{trend} ({change:+.0f} vs previous reading)"
            any_trend_known = True
        else:
            trend = "unknown"
            change = 0.0
            trend_desc = "Trend Analysis: Not Available (Insufficient historical points)"

        market_entries.append({
            "market": market,
            "latest_price": latest_price,
            "latest_date": latest_date,
            "trend": trend,
            "change": change,
            "trend_desc": trend_desc,
            "history": points
        })

    # Sort descending by latest modal price
    market_entries.sort(key=lambda x: -x["latest_price"])

    prices = [m["latest_price"] for m in market_entries]
    top_entry = market_entries[0]
    lowest_entry = market_entries[-1]
    average_price = sum(prices) / len(prices)
    extra_earnings = top_entry["latest_price"] - lowest_entry["latest_price"]
    extra_earnings_pct = (extra_earnings / lowest_entry["latest_price"] * 100) if lowest_entry["latest_price"] else 0

    transport_warning = (
        "This recommendation is based solely on reported market prices and trends. "
        "It does NOT yet account for transport distance or fuel/freight costs. "
        "A closer market with a slightly lower price may yield higher net profit after transport expenses."
    )

    return {
        "status": "success",
        "commodity": commodity,
        "variety": selected_variety,
        "total_days": total_days,
        "threshold_pct": threshold_pct,
        "reliable_markets_count": len(reliable_markets),
        "markets": market_entries,
        "recommendation": {
            "recommended_market": top_entry["market"],
            "highest_price": top_entry["latest_price"],
            "date": top_entry["latest_date"],
            "trend": top_entry["trend"],
            "trend_desc": top_entry["trend_desc"],
            "lowest_market": lowest_entry["market"],
            "lowest_price": lowest_entry["latest_price"],
            "average_price": average_price,
            "extra_earnings": extra_earnings,
            "extra_earnings_pct": extra_earnings_pct,
            "any_trend_known": any_trend_known
        },
        "transport_warning": transport_warning
    }
