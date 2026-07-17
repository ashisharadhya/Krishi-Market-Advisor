# src/phase3/report_generator.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Generate CSV and human-readable TXT reports, and format the Phase 3
#   terminal output using consistent styling.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from pathlib import Path
import pandas as pd
from src.config import PROJECT_ROOT

logger = logging.getLogger("krishi")


def generate_phase3_reports(
    comparison_df: pd.DataFrame,
    stats: dict,
    trend: dict,
    recommendation: dict,
    pilot_crop: str,
    pilot_variety: str,
    total_files: int,
    latest_file_name: str,
    reports_dir: Path = None
) -> str:
    """
    Generate reports inside reports/ folder and return the formatted report
    string for terminal output.

    Args:
        comparison_df (pd.DataFrame): Ranked market data.
        stats (dict): Calculated metrics.
        trend (dict): Calculated trend metrics.
        recommendation (dict): Recommendation summaries.
        pilot_crop (str): Selected crop name.
        pilot_variety (str): Selected variety name.
        total_files (int): Total historical CSV count.
        latest_file_name (str): Name of the latest CSV analyzed.
        reports_dir (Path, optional): Reports output directory. Defaults to reports/.

    Returns:
        str: Human-readable terminal report content.
    """
    if reports_dir is None:
        reports_dir = PROJECT_ROOT / "reports"

    reports_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing Phase 3 reports to: {reports_dir}...")

    # ── 1. Write reports/market_comparison.csv ────────────────────────────────
    csv_path = reports_dir / "market_comparison.csv"
    comparison_df.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info(f"Generated Phase 3 CSV report: {csv_path}")

    # ── 2. Write reports/recommendation.txt ───────────────────────────────────
    txt_path = reports_dir / "recommendation.txt"
    
    # Extract values safely
    rec_market = recommendation.get("recommended_market", "N/A")
    rec_summary = recommendation.get("recommendation_summary", "")
    trend_status = trend.get("trend_status", "Not Available")
    
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Selected Crop           : {pilot_crop}\n")
        f.write(f"Selected Variety        : {pilot_variety}\n")
        f.write(f"Recommended Market      : {rec_market}\n")
        f.write(f"Markets Compared        : {stats['markets_compared']}\n")
        f.write(f"Highest Price           : {stats['highest_modal_price']:.2f}\n")
        f.write(f"Lowest Price            : {stats['lowest_modal_price']:.2f}\n")
        f.write(f"Average Price           : {stats['average_modal_price']:.2f}\n")
        f.write(f"Estimated Extra Earnings: {stats['estimated_extra_earnings']:.2f}\n")
        f.write(f"Historical CSV Files    : {total_files}\n")
        f.write(f"Trend Status            : {trend_status}\n")
        f.write(f"Recommendation Summary  : {rec_summary}\n")
    logger.info(f"Generated Phase 3 text recommendation report: {txt_path}")

    # ── 3. Build Terminal/Human Readable report ───────────────────────────────
    # Standardize separator width to 52 characters to match user request layout
    sep_line = "-" * 52
    double_sep = "=" * 52

    lines = []
    lines.append(double_sep)
    lines.append("Krishi Market Advisor")
    lines.append("")
    lines.append("Phase 3")
    lines.append("")
    lines.append("Market Comparison & Recommendation")
    lines.append(double_sep)
    lines.append("")
    lines.append("Selected Crop")
    lines.append(pilot_crop)
    lines.append("")
    lines.append("Selected Variety")
    lines.append(pilot_variety)
    lines.append("")
    lines.append("Historical CSV Files Loaded")
    lines.append(str(total_files))
    lines.append("")
    lines.append("Latest CSV Used")
    lines.append(latest_file_name)
    lines.append("")
    lines.append("Markets Compared")
    lines.append(str(stats["markets_compared"]))
    lines.append("")
    lines.append(sep_line)
    lines.append("")
    lines.append("Market Ranking")
    lines.append("")
    lines.append(f"{'Rank':<5} | {'Market':<18} | {'Variety':<10} | {'Modal Price':<10}")
    lines.append(sep_line)
    
    # Display all compared markets in the ranking table
    for _, row in comparison_df.iterrows():
        m_name = row["Market"]
        m_name_trunc = m_name[:16] + ".." if len(m_name) > 18 else m_name
        v_name = row["Variety"]
        v_name_trunc = v_name[:8] + ".." if len(v_name) > 10 else v_name
        lines.append(f"{int(row['Rank']):<5} | {m_name_trunc:<18} | {v_name_trunc:<10} | {row['Modal Price']:.2f}")
        
    lines.append("")
    lines.append(sep_line)
    lines.append("")
    lines.append("Recommended Market")
    lines.append(rec_market)
    lines.append("")
    lines.append("Highest Modal Price")
    lines.append(f"{stats['highest_modal_price']:.2f}")
    lines.append("")
    lines.append("Lowest Modal Price")
    lines.append(f"{stats['lowest_modal_price']:.2f}")
    lines.append("")
    lines.append("Average Modal Price")
    lines.append(f"{stats['average_modal_price']:.2f}")
    lines.append("")
    lines.append("Estimated Extra Earnings")
    lines.append(f"{stats['estimated_extra_earnings']:.2f}")
    lines.append("")
    lines.append(sep_line)
    lines.append("")
    lines.append("Trend Analysis")
    lines.append("")
    
    if trend_status != "Available":
        lines.append("Trend Status")
        lines.append("Not Available")
        lines.append("")
        lines.append("Reason")
        lines.append("Insufficient historical data.")
        lines.append("")
        lines.append("Historical CSV Files")
        lines.append(str(total_files))
    else:
        lines.append("Previous Price")
        lines.append(f"{trend['previous_price']:.2f}")
        lines.append("")
        lines.append("Current Price")
        lines.append(f"{trend['current_price']:.2f}")
        lines.append("")
        lines.append("Percentage Change")
        lines.append(f"{trend['percentage_change']:.2f}%")
        lines.append("")
        lines.append("Trend Direction")
        lines.append(trend["trend_direction"])
        lines.append("")
        lines.append("Recommendation")
        lines.append(rec_summary)
        
    lines.append("")
    lines.append(sep_line)
    lines.append("")
    lines.append("Reports Generated")
    lines.append("")
    lines.append(f"✓ reports/market_comparison.csv")
    lines.append(f"✓ reports/recommendation.txt")
    lines.append("")
    lines.append(sep_line)
    lines.append("")
    lines.append("Project Status")
    lines.append("")
    lines.append("✓ Phase 1 Completed")
    lines.append("✓ Phase 2 Completed")
    lines.append("✓ Phase 3 Completed")
    lines.append("→ Ready for Phase 4")
    lines.append("")
    lines.append(double_sep)

    return "\n".join(lines)
