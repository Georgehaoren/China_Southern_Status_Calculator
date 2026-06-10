from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict


def export_json(result: Dict[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)


def export_csv(result: Dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "name", "count", "type", "mode", "marketing", "operating", "flight_number", "origin_airport", "destination_airport",
        "standard_miles_source", "standard_miles_note", "cost_group", "cost_input_mode", "cost_input_mode_label", "entered_cash_amount", "allocated_total_cost", "cost_allocation_note", "official_tool_name", "official_tool_url", "ticket_prefix", "booking_class",
        "partner_code", "partner_label", "service_class", "service_class_display", "cash_per_unit", "standard_miles", "category_coef",
        "cabin_rate", "segment_credit_per_unit", "reward_coef", "q_miles_per_unit", "q_segments_per_unit",
        "award_miles_per_unit", "total_cost", "total_q_miles", "total_q_segments", "total_award_miles",
        "cost_per_q_mile", "cost_per_q_segment", "notes"
    ])
    for row in result.get("items", []):
        writer.writerow([
            row.get("name", ""), row.get("count", ""), row.get("product_type", ""), row.get("earning_mode", ""),
            row.get("marketing_carrier", ""), row.get("operating_carrier", ""), row.get("flight_number", ""), row.get("origin_airport", ""), row.get("destination_airport", ""),
            row.get("standard_miles_source", ""), row.get("standard_miles_note", ""), row.get("cost_group", ""), row.get("cost_input_mode", ""), row.get("cost_input_mode_label", ""), row.get("entered_cash_amount", ""), row.get("allocated_total_cost", ""), row.get("cost_allocation_note", ""), row.get("official_tool_name", ""), row.get("official_tool_url", ""),
            row.get("ticket_prefix", ""), row.get("booking_class", ""),
            row.get("partner_code", ""), row.get("partner_label", ""), row.get("service_class", ""), row.get("service_class_display", ""),
            row.get("cash_amount_per_unit", ""), row.get("standard_miles_per_segment", ""), row.get("category_coefficient", ""),
            row.get("cabin_accrual_rate", ""), row.get("segment_credit_per_segment", ""), row.get("member_reward_coefficient", ""),
            row.get("qualifying_miles_per_unit", ""), row.get("qualifying_segments_per_unit", ""), row.get("award_miles_per_unit", ""),
            row.get("total_cost", ""), row.get("total_qualifying_miles", ""), row.get("total_qualifying_segments", ""),
            row.get("total_award_miles", ""), row.get("cost_per_qualifying_mile", ""), row.get("cost_per_qualifying_segment", ""),
            " | ".join(row.get("notes", [])),
        ])
    writer.writerow([])
    summary = result.get("summary", {})
    writer.writerow(["summary"])
    for key, value in summary.items():
        writer.writerow([key, value])
    return output.getvalue()
