from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parents[1]
RULES_PATH = BASE_DIR / "data" / "cz_rules_2025_2027.json"
PARTNER_JSON_PATH = BASE_DIR / "data" / "cz_partner_accrual_rules_2026.json"
PARTNER_CSV_PATH = BASE_DIR / "data" / "cz_partner_accrual_rules_2026.csv"
CARRIER_JSON_PATH = BASE_DIR / "data" / "cz_carrier_directory_2026.json"
CARRIER_CSV_PATH = BASE_DIR / "data" / "cz_carrier_directory_2026.csv"
CODESHARE_784_JSON_PATH = BASE_DIR / "data" / "cz_codeshare_784_accrual_rules_2026.json"
CODESHARE_784_CSV_PATH = BASE_DIR / "data" / "cz_codeshare_784_accrual_rules_2026.csv"
MILEAGE_TOOLS_JSON_PATH = BASE_DIR / "data" / "mileage_tool_links_2026.json"
MILEAGE_TOOLS_CSV_PATH = BASE_DIR / "data" / "mileage_tool_links_2026.csv"
PARTNER_STATUS_JSON_PATH = BASE_DIR / "data" / "cz_partner_status_2026.json"
PARTNER_STATUS_CSV_PATH = BASE_DIR / "data" / "cz_partner_status_2026.csv"
DATA_SOURCES_JSON_PATH = BASE_DIR / "data" / "data_sources_2026.json"
DATA_SOURCES_CSV_PATH = BASE_DIR / "data" / "data_sources_2026.csv"
SERVICE_CLASS_NOTES_JSON_PATH = BASE_DIR / "data" / "service_class_notes_2026.json"
SERVICE_CLASS_NOTES_CSV_PATH = BASE_DIR / "data" / "service_class_notes_2026.csv"


def _load_partner_rules_from_csv() -> Dict[str, Any]:
    partners: Dict[str, Any] = {}
    if not PARTNER_CSV_PATH.exists():
        return {"version": "csv-missing", "partners": {}}
    with PARTNER_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("carrier_code") or "").strip().upper()
            if not code:
                continue
            partner = partners.setdefault(code, {
                "name_cn": row.get("name_cn", ""),
                "name_en": row.get("name_en", ""),
                "valid_from": row.get("valid_from") or None,
                "valid_to": row.get("valid_to") or None,
                "validity_cn": row.get("validity_cn", ""),
                "rules": [],
            })
            partner["rules"].append({
                "service_class": row.get("service_class", ""),
                "cabins": [c.strip().upper() for c in (row.get("cabins") or "").replace(",", "/").split("/") if c.strip()],
                "mileage_rate": float(row.get("mileage_rate") or 0),
                "segment_credit": float(row.get("segment_credit") or 0),
            })
    return {"version": "csv-fallback", "partners": partners, "default_partner_award_rule": "same_as_qualifying_miles"}


def load_partner_rules() -> Dict[str, Any]:
    if PARTNER_JSON_PATH.exists():
        with PARTNER_JSON_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return _load_partner_rules_from_csv()


def _load_codeshare_784_rules_from_csv() -> Dict[str, Any]:
    carriers: Dict[str, Any] = {}
    if not CODESHARE_784_CSV_PATH.exists():
        return {"version": "csv-missing", "carriers": {}}
    with CODESHARE_784_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("carrier_code") or "").strip().upper()
            if not code:
                continue
            carrier = carriers.setdefault(code, {
                "name_cn": row.get("name_cn", ""),
                "name_en": row.get("name_en", ""),
                "valid_from": row.get("valid_from") or None,
                "valid_to": row.get("valid_to") or None,
                "validity_cn": row.get("validity_cn", ""),
                "rules": [],
            })
            carrier["rules"].append({
                "service_class": row.get("service_class", ""),
                "cabins": [c.strip().upper() for c in (row.get("cabins") or "").replace(",", "/").split("/") if c.strip()],
                "mileage_rate": float(row.get("mileage_rate") or 0),
                "rule_source": row.get("rule_source", "csv"),
            })
    return {
        "version": "csv-fallback",
        "source_note": "Loaded from CSV fallback.",
        "default_award_rule": "qualifying_miles_times_member_coefficient",
        "minimum_standard_miles": 500,
        "segment_rule": "use_cz_ticketed_booking_class_segment_credit",
        "carriers": carriers,
    }


def load_codeshare_784_rules() -> Dict[str, Any]:
    if CODESHARE_784_JSON_PATH.exists():
        with CODESHARE_784_JSON_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return _load_codeshare_784_rules_from_csv()


def load_carrier_directory() -> Dict[str, Any]:
    if CARRIER_JSON_PATH.exists():
        with CARRIER_JSON_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    if not CARRIER_CSV_PATH.exists():
        return {"version": "csv-missing", "carriers": []}
    carriers = []
    with CARRIER_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            carriers.append({
                "code": (row.get("code") or "").strip().upper(),
                "name_cn": row.get("name_cn", ""),
                "name_en": row.get("name_en", ""),
                "aliases": [x for x in (row.get("aliases") or "").split("/") if x],
                "relation_types": [x for x in (row.get("relation_types") or "").split("/") if x],
                "accrual_partner": str(row.get("accrual_partner", "")).lower() == "true",
                "has_partner_rule": str(row.get("has_partner_rule", "")).lower() == "true",
                "has_codeshare_784_rule": str(row.get("has_codeshare_784_rule", "")).lower() == "true",
                "notes_cn": row.get("notes_cn", ""),
                "source": row.get("source", ""),
            })
    return {"version": "csv-fallback", "carriers": carriers}



def load_mileage_tools() -> Dict[str, Any]:
    if MILEAGE_TOOLS_JSON_PATH.exists():
        with MILEAGE_TOOLS_JSON_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    if not MILEAGE_TOOLS_CSV_PATH.exists():
        return {"version": "csv-missing", "tools": [], "default_tool_code": "CZ"}
    tools = []
    with MILEAGE_TOOLS_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tools.append({
                "code": (row.get("code") or "").strip().upper(),
                "program": row.get("program", ""),
                "name_cn": row.get("name_cn", ""),
                "name_en": row.get("name_en", ""),
                "tool_url": row.get("tool_url", ""),
                "tool_type": row.get("tool_type", ""),
                "priority": int(float(row.get("priority") or 999)),
                "default_for_cz_tool": str(row.get("default_for_cz_tool", "")).lower() == "true",
                "recommended_for": row.get("recommended_for", ""),
                "notes_cn": row.get("notes_cn", ""),
                "source_url": row.get("source_url", ""),
            })
    return {
        "version": "csv-fallback",
        "default_tool_code": "CZ",
        "recommended_sources_order": ["manual_actual_posting", "manual_official_tool", "cz_skypearl_calculator", "airline_own_calculator", "airport_distance_estimate", "unknown"],
        "tools": sorted(tools, key=lambda item: item.get("priority", 999)),
    }



def load_data_sources() -> Dict[str, Any]:
    if DATA_SOURCES_JSON_PATH.exists():
        with DATA_SOURCES_JSON_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    if not DATA_SOURCES_CSV_PATH.exists():
        return {"version": "csv-missing", "sources": []}
    sources = []
    with DATA_SOURCES_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sources.append({
                "id": row.get("id", ""),
                "name_cn": row.get("name_cn", ""),
                "source_category": row.get("source_category", ""),
                "url": row.get("url", ""),
                "applies_to": [x.strip() for x in (row.get("applies_to") or "").split("/") if x.strip()],
                "retrieved_or_provided_at": row.get("retrieved_or_provided_at", ""),
                "notes_cn": row.get("notes_cn", ""),
            })
    return {"version": "csv-fallback", "sources": sources}



def load_service_class_notes() -> Dict[str, Any]:
    if SERVICE_CLASS_NOTES_JSON_PATH.exists():
        with SERVICE_CLASS_NOTES_JSON_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    if not SERVICE_CLASS_NOTES_CSV_PATH.exists():
        return {"version": "csv-missing", "records": []}
    records = []
    with SERVICE_CLASS_NOTES_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    return {"version": "csv-fallback", "records": records}

def load_partner_status() -> Dict[str, Any]:
    if PARTNER_STATUS_JSON_PATH.exists():
        with PARTNER_STATUS_JSON_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    if not PARTNER_STATUS_CSV_PATH.exists():
        return {"version": "csv-missing", "carriers": {}}
    carriers: Dict[str, Any] = {}
    with PARTNER_STATUS_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("code") or "").strip().upper()
            if not code:
                continue
            carriers[code] = {
                "code": code,
                "ffp_status": row.get("ffp_status", "unknown_unverified"),
                "current_accrual_eligible": str(row.get("current_accrual_eligible", "")).lower() == "true",
                "risk_level": row.get("risk_level", "medium"),
                "relation_hint": row.get("relation_hint", ""),
                "status_note_cn": row.get("status_note_cn", ""),
                "source": row.get("source", "csv"),
            }
    return {"version": "csv-fallback", "carriers": carriers}


def get_partner_status(rules: Dict[str, Any], carrier_code: str) -> Dict[str, Any]:
    code = str(carrier_code or "").strip().upper()
    statuses = rules.get("partner_status", {}).get("carriers", {})
    return statuses.get(code, {
        "code": code,
        "ffp_status": "unknown_unverified",
        "current_accrual_eligible": False,
        "risk_level": "medium",
        "status_note_cn": "未在合作状态库中确认；请按南航最新页面/公告核对后再计入。",
    })


def is_current_accrual_partner(rules: Dict[str, Any], carrier_code: str) -> bool:
    return bool(get_partner_status(rules, carrier_code).get("current_accrual_eligible"))


def load_rules() -> Dict[str, Any]:
    with RULES_PATH.open("r", encoding="utf-8") as f:
        rules = json.load(f)
    rules["partner_accrual"] = load_partner_rules()
    rules["codeshare_784_accrual"] = load_codeshare_784_rules()
    rules["mileage_tools"] = load_mileage_tools()
    rules["partner_status"] = load_partner_status()
    rules["data_sources"] = load_data_sources()
    rules["service_class_notes"] = load_service_class_notes()
    return rules


def tier_order(rules: Dict[str, Any]) -> list[str]:
    return [key for key, _ in sorted(rules["tiers"].items(), key=lambda item: item[1]["rank"])]


def tier_label(rules: Dict[str, Any], tier_code: str) -> str:
    tier = rules["tiers"].get(tier_code, {})
    return tier.get("name_cn", tier_code)


def partner_label(rules: Dict[str, Any], carrier_code: str) -> str:
    code = str(carrier_code or "").upper()
    partner = rules.get("partner_accrual", {}).get("partners", {}).get(code)
    if partner:
        return f"{partner.get('name_cn', code)} / {partner.get('name_en', code)}"
    c = rules.get("codeshare_784_accrual", {}).get("carriers", {}).get(code)
    if c:
        return f"{c.get('name_cn', code)} / {c.get('name_en', code)}"
    return code
