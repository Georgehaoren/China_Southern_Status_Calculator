from __future__ import annotations

import os

from flask import Flask, jsonify, request

from api import register_api_blueprints
from config import DEFAULT_HOST, DEFAULT_PORT
from web.routes import web_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(web_bp)
    register_api_blueprints(app)

    @app.errorhandler(Exception)
    def handle_error(exc: Exception):
        if request.path.startswith("/api/"):
            return jsonify({"error": type(exc).__name__, "message": str(exc)}), 500
        raise exc

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("CZ_APP_PORT", str(DEFAULT_PORT)))
    app.run(host=DEFAULT_HOST, port=port, debug=False, use_reloader=False)
