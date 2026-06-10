from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Any

from flask import Blueprint, jsonify, send_file

from config import DATA_FILES
from services.rules import (
    load_rules,
    load_partner_rules,
    load_carrier_directory,
    load_codeshare_784_rules,
    load_mileage_tools,
    load_partner_status,
    load_data_sources,
    load_service_class_notes,
)

reference_bp = Blueprint("api_reference", __name__, url_prefix="/api")


def _send_data_file(path: Path, mimetype: str, download_name: str):
    return send_file(path, mimetype=mimetype, as_attachment=True, download_name=download_name)


@reference_bp.get("/rules")
def api_rules():
    return jsonify(load_rules())


@reference_bp.get("/partners")
def api_partners():
    return jsonify(load_partner_rules())


@reference_bp.get("/partners/json")
def api_partner_json_file():
    return _send_data_file(DATA_FILES["partner_rules_json"], "application/json", "cz_partner_accrual_rules_2026.json")


@reference_bp.get("/partners/csv")
def api_partner_csv_file():
    return _send_data_file(DATA_FILES["partner_rules_csv"], "text/csv", "cz_partner_accrual_rules_2026.csv")


@reference_bp.get("/carriers")
def api_carriers():
    return jsonify(load_carrier_directory())


@reference_bp.get("/carriers/json")
def api_carriers_json_file():
    return _send_data_file(DATA_FILES["carrier_directory_json"], "application/json", "cz_carrier_directory_2026.json")


@reference_bp.get("/carriers/csv")
def api_carriers_csv_file():
    return _send_data_file(DATA_FILES["carrier_directory_csv"], "text/csv", "cz_carrier_directory_2026.csv")


@reference_bp.get("/codeshare-784")
def api_codeshare_784():
    return jsonify(load_codeshare_784_rules())


@reference_bp.get("/codeshare-784/json")
def api_codeshare_784_json_file():
    return _send_data_file(DATA_FILES["codeshare_784_json"], "application/json", "cz_codeshare_784_accrual_rules_2026.json")


@reference_bp.get("/codeshare-784/csv")
def api_codeshare_784_csv_file():
    return _send_data_file(DATA_FILES["codeshare_784_csv"], "text/csv", "cz_codeshare_784_accrual_rules_2026.csv")


@reference_bp.get("/partner-status")
def api_partner_status():
    return jsonify(load_partner_status())


@reference_bp.get("/partner-status/json")
def api_partner_status_json_file():
    return _send_data_file(DATA_FILES["partner_status_json"], "application/json", "cz_partner_status_2026.json")


@reference_bp.get("/partner-status/csv")
def api_partner_status_csv_file():
    return _send_data_file(DATA_FILES["partner_status_csv"], "text/csv", "cz_partner_status_2026.csv")


@reference_bp.get("/mileage-tools")
def api_mileage_tools():
    return jsonify(load_mileage_tools())


@reference_bp.get("/mileage-tools/json")
def api_mileage_tools_json_file():
    return _send_data_file(DATA_FILES["mileage_tools_json"], "application/json", "mileage_tool_links_2026.json")


@reference_bp.get("/mileage-tools/csv")
def api_mileage_tools_csv_file():
    return _send_data_file(DATA_FILES["mileage_tools_csv"], "text/csv", "mileage_tool_links_2026.csv")


@reference_bp.get("/data-sources")
def api_data_sources():
    return jsonify(load_data_sources())


@reference_bp.get("/data-sources/json")
def api_data_sources_json_file():
    return _send_data_file(DATA_FILES["data_sources_json"], "application/json", "data_sources_2026.json")


@reference_bp.get("/data-sources/csv")
def api_data_sources_csv_file():
    return _send_data_file(DATA_FILES["data_sources_csv"], "text/csv", "data_sources_2026.csv")


@reference_bp.get("/service-class-notes")
def api_service_class_notes():
    return jsonify(load_service_class_notes())


@reference_bp.get("/service-class-notes/json")
def api_service_class_notes_json_file():
    return _send_data_file(DATA_FILES["service_class_notes_json"], "application/json", "service_class_notes_2026.json")


@reference_bp.get("/service-class-notes/csv")
def api_service_class_notes_csv_file():
    return _send_data_file(DATA_FILES["service_class_notes_csv"], "text/csv", "service_class_notes_2026.csv")
