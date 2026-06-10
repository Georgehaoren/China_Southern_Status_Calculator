from __future__ import annotations

from flask import Flask

from .calculate import calculate_bp
from .exports import exports_bp
from .health import health_bp
from .reference_data import reference_bp


def register_api_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(reference_bp)
    app.register_blueprint(calculate_bp)
    app.register_blueprint(exports_bp)
