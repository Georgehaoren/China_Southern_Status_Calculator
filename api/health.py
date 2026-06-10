from __future__ import annotations

from flask import Blueprint, jsonify

from config import APP_NAME, APP_VERSION

health_bp = Blueprint("api_health", __name__, url_prefix="/api")


@health_bp.get("/health")
def api_health():
    return jsonify({"status": "ok", "app": APP_NAME, "version": APP_VERSION, "unofficial": True})
