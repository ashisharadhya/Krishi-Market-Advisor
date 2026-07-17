# src/phase2/report_generator.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Generate the Phase 2 analysis reports and configuration files.
#   Outputs reports inside reports/ and configuration files inside config/.
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd

from src.config import Config, PROJECT_ROOT

logger = logging.getLogger("krishi")


def generate_reports(
    scored_commodities: pd.DataFrame,
    mandi_reliability: pd.DataFrame,
    pilot_crop: str,
    pilot_markets: list,
    selection_reason: str,
    total_files: int,
    total_records: int,
    start_date: str,
    end_date: str
) -> str:
    """
    Generate analysis reports and write them to the filesystem.

    Creates:
      1. reports/commodity_analysis.csv
      2. reports/mandi_reliability.csv
      3. reports/pilot_crop_report.csv
      4. reports/pilot_crop_report.txt
      5. config/pilot_config.json

    Args:
        scored_commodities (pd.DataFrame): Commodity analyzer output with scores.
        mandi_reliability (pd.DataFrame): Mandi analyzer output ranked by reliability.
        pilot_crop (str): Selected pilot crop name.
        pilot_markets (list): List of selected pilot market names.
        selection_reason (str): Formulated explanation for the choice of crop.
        total_files (int): Total number of files analyzed.
        total_records (int): Total records in the merged dataset.
        start_date (str): Min date in dataset.
        end_date (str): Max date in dataset.

    Returns:
        str: Formatted human-readable report content.
    """
    logger.info("Generating report files and configuration...")

    # Create reports/ and config/ folders relative to PROJECT_ROOT
    reports_dir = PROJECT_ROOT / "reports"
    config_dir = PROJECT_ROOT / "config"

    reports_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── 1. Write commodity_analysis.csv ───────────────────────────────────────
    commodity_path = reports_dir / "commodity_analysis.csv"
    scored_commodities.to_csv(commodity_path, index=False, encoding="utf-8")
    logger.info(f"Generated report: {commodity_path}")

    # ── 2. Write mandi_reliability.csv ────────────────────────────────────────
    mandi_path = reports_dir / "mandi_reliability.csv"
    mandi_reliability.to_csv(mandi_path, index=False, encoding="utf-8")
    logger.info(f"Generated report: {mandi_path}")

    # ── 3. Write pilot_crop_report.csv ────────────────────────────────────────
    # Contains a tabular view of the selected pilot crop and its markets
    pilot_rows = []
    for idx, market in enumerate(pilot_markets):
        mandi_info = mandi_reliability[mandi_reliability["mandi"] == market]
        rel_score = mandi_info["reliability_score"].values[0] if not mandi_info.empty else 0.0
        days_rep = mandi_info["days_reported"].values[0] if not mandi_info.empty else 0
        
        pilot_rows.append({
            "pilot_crop": pilot_crop,
            "pilot_market": market,
            "rank": idx + 1,
            "mandi_reliability_score": rel_score,
            "mandi_days_reported": days_rep,
            "selection_date": today_str
        })
    
    pilot_csv_df = pd.DataFrame(pilot_rows)
    pilot_csv_path = reports_dir / "pilot_crop_report.csv"
    pilot_csv_df.to_csv(pilot_csv_path, index=False, encoding="utf-8")
    logger.info(f"Generated report: {pilot_csv_path}")

    # ── 4. Construct Human Readable Text Report ───────────────────────────────
    pilot_info = scored_commodities[scored_commodities["commodity"] == pilot_crop]
    if not pilot_info.empty:
        pilot_row = pilot_info.iloc[0]
        pilot_score_val = pilot_row["pilot_score"]
        reporting_markets_val = int(pilot_row["unique_markets"])
        total_records_val = int(pilot_row["records"])
        completeness_val = pilot_row["completeness"]
        consistency_val = pilot_row["consistency"]
    else:
        pilot_score_val = 0.0
        reporting_markets_val = 0
        total_records_val = 0
        completeness_val = 0.0
        consistency_val = 0.0

    lines = []
    lines.append("============================================================")
    lines.append("                   Krishi Market Advisor")
    lines.append("                          Phase 2")
    lines.append("                  Data Reliability Report")
    lines.append("============================================================")
    lines.append(f"Generated At         : {today_str}")
    lines.append(f"Files Analysed       : {total_files}")
    lines.append(f"Total Records        : {total_records:,}")
    lines.append(f"Date Range           : {start_date} to {end_date}")
    lines.append("------------------------------------------------------------")
    
    # Top Commodities
    lines.append("Top Commodities")
    lines.append(f"{'Commodity':<25} | {'Records':<8} | {'Markets':<7} | {'Pilot Score':<11}")
    lines.append("-" * 60)
    
    top_commodities_print = scored_commodities.head(5)
    for _, row in top_commodities_print.iterrows():
        c_name = row["commodity"]
        c_name_trunc = c_name[:23] + ".." if len(c_name) > 25 else c_name
        lines.append(f"{c_name_trunc:<25} | {int(row['records']):<8} | {int(row['unique_markets']):<7} | {row['pilot_score']:.4f}")
        
    lines.append("------------------------------------------------------------")
    
    # Top Reporting Mandis
    lines.append("Top Reporting Mandis")
    lines.append(f"{'Mandi':<25} | {'Reporting Days':<14} | {'Reliability %':<13}")
    lines.append("-" * 60)
    
    top_mandis_print = mandi_reliability.head(5)
    for _, row in top_mandis_print.iterrows():
        m_name = row["mandi"]
        m_name_trunc = m_name[:23] + ".." if len(m_name) > 25 else m_name
        lines.append(f"{m_name_trunc:<25} | {int(row['days_reported']):<14} | {row['reliability_score']:.1%}")
        
    lines.append("------------------------------------------------------------")
    
    # Recommended Pilot Crop & Reason
    lines.append(f"Recommended Pilot Crop : {pilot_crop}")
    lines.append("")
    lines.append("Reason")
    lines.append("")
    lines.append(f"• Highest Pilot Score : {pilot_score_val:.4f}")
    lines.append("")
    lines.append(f"• Reporting Markets : {reporting_markets_val}")
    lines.append("")
    lines.append(f"• Total Records : {total_records_val}")
    lines.append("")
    lines.append(f"• Data Completeness : {completeness_val * 100:g}%")
    lines.append("")
    lines.append(f"• Reporting Consistency : {consistency_val * 100:g}%")
    lines.append("------------------------------------------------------------")
    
    # Phase 3 Preview
    lines.append("Phase 3 Preview")
    lines.append("")
    lines.append("Selected Crop")
    lines.append(f"{pilot_crop}")
    lines.append("")
    lines.append("Next Step")
    lines.append("")
    lines.append(f"Compare today's prices for {pilot_crop}")
    lines.append("across all Karnataka mandis and recommend the")
    lines.append("best market offering the highest modal price.")
    lines.append("")
    lines.append("Trend Analysis")
    lines.append("")
    lines.append("Not available until multiple days of")
    lines.append("historical data are collected.")
    lines.append("")
    lines.append("------------------------------------------------------------")
    
    # Project Status
    lines.append("Project Status")
    lines.append("")
    lines.append("✓ Phase 1 Completed")
    lines.append("✓ Phase 2 Completed")
    lines.append("→ Ready for Phase 3:")
    lines.append("Market Comparison & Recommendation Engine")
    lines.append("")
    lines.append("------------------------------------------------------------")
    
    # Completion status
    lines.append("Phase 2 Completed Successfully")
    lines.append("============================================================")
    
    report_content = "\n".join(lines)

    # ── 4. Write pilot_crop_report.txt (human readable text) ──────────────────
    pilot_txt_path = reports_dir / "pilot_crop_report.txt"
    with open(pilot_txt_path, "w", encoding="utf-8") as f:
        f.write(report_content + "\n")
    logger.info(f"Generated report: {pilot_txt_path}")

    # ── 5. Write pilot_config.json ────────────────────────────────────────────
    config_data = {
        "pilot_crop": pilot_crop,
        "pilot_markets": pilot_markets,
        "analysis_date": today_str,
        "total_files": total_files
    }
    
    json_path = config_dir / "pilot_config.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(config_data, jf, indent=4, ensure_ascii=False)
    logger.info(f"Generated config: {json_path}")

    return report_content
