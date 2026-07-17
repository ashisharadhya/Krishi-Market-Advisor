# src/phase3/config_loader.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Load the Phase 3 config (pilot crop) from config/pilot_config.json.
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
from pathlib import Path
from src.config import PROJECT_ROOT

logger = logging.getLogger("krishi")


def load_pilot_config(config_path: Path = None) -> dict:
    """
    Load configuration from config/pilot_config.json.

    Args:
        config_path (Path, optional): Path to the config file. Defaults to config/pilot_config.json.

    Returns:
        dict: Configuration dictionary containing at least 'pilot_crop'.
    """
    if config_path is None:
        config_path = PROJECT_ROOT / "config" / "pilot_config.json"

    logger.info(f"Loading configuration from {config_path}...")

    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}. Please run Phase 2 analysis first.")
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse config JSON file: {e}")
        raise ValueError(f"Invalid JSON in config file: {e}")
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        raise e

    if "pilot_crop" not in config_data or not config_data["pilot_crop"]:
        logger.error("Required key 'pilot_crop' missing or empty in configuration file.")
        raise KeyError("Key 'pilot_crop' is missing or empty in config.")

    if "pilot_variety" not in config_data or not config_data["pilot_variety"]:
        logger.error("Required key 'pilot_variety' missing or empty in configuration file.")
        raise KeyError("Key 'pilot_variety' is missing or empty in config.")

    logger.info(f"Successfully loaded configuration. Selected Pilot Crop: '{config_data['pilot_crop']}', Pilot Variety: '{config_data['pilot_variety']}'")
    return config_data
