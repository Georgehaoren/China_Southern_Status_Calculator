from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

APP_NAME = "cz_status_webui"
APP_VERSION = "v26-modular-api"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = int(os.environ.get("CZ_APP_PORT", "5055"))

DATA_FILES = {
    "partner_rules_json": DATA_DIR / "cz_partner_accrual_rules_2026.json",
    "partner_rules_csv": DATA_DIR / "cz_partner_accrual_rules_2026.csv",
    "carrier_directory_json": DATA_DIR / "cz_carrier_directory_2026.json",
    "carrier_directory_csv": DATA_DIR / "cz_carrier_directory_2026.csv",
    "codeshare_784_json": DATA_DIR / "cz_codeshare_784_accrual_rules_2026.json",
    "codeshare_784_csv": DATA_DIR / "cz_codeshare_784_accrual_rules_2026.csv",
    "mileage_tools_json": DATA_DIR / "mileage_tool_links_2026.json",
    "mileage_tools_csv": DATA_DIR / "mileage_tool_links_2026.csv",
    "partner_status_json": DATA_DIR / "cz_partner_status_2026.json",
    "partner_status_csv": DATA_DIR / "cz_partner_status_2026.csv",
    "data_sources_json": DATA_DIR / "data_sources_2026.json",
    "data_sources_csv": DATA_DIR / "data_sources_2026.csv",
    "service_class_notes_json": DATA_DIR / "service_class_notes_2026.json",
    "service_class_notes_csv": DATA_DIR / "service_class_notes_2026.csv",
}
