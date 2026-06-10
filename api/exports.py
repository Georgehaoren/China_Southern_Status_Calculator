from __future__ import annotations

from flask import Blueprint, Response, request

from services.calculator import calculate_plan
from services.exporter import export_csv, export_json

exports_bp = Blueprint("api_exports", __name__, url_prefix="/api")


@exports_bp.post("/export/json")
def api_export_json():
    payload = request.get_json(force=True) or {}
    result = calculate_plan(payload)
    return Response(
        export_json(result),
        mimetype="application/json; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=cz_status_plan.json"},
    )


@exports_bp.post("/export/csv")
def api_export_csv():
    payload = request.get_json(force=True) or {}
    result = calculate_plan(payload)
    return Response(
        export_csv(result),
        mimetype="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=cz_status_plan.csv"},
    )
