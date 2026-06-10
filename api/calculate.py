from __future__ import annotations

from flask import Blueprint, jsonify, request

from services.calculator import calculate_plan

calculate_bp = Blueprint("api_calculate", __name__, url_prefix="/api")


@calculate_bp.post("/calculate")
def api_calculate():
    payload = request.get_json(force=True) or {}
    return jsonify(calculate_plan(payload))
