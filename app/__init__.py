import logging
import os

from flask import Flask, jsonify, render_template
from werkzeug.exceptions import HTTPException

from config import Config
from app.routes.resume_routes import resume_bp
from app.routes.job_routes import job_bp
from app.routes.ats_routes import ats_bp
from app.routes.rewrite_routes import rewrite_bp
from app.routes.generation_routes import generation_bp


def _configure_logging(app):
    log_level_name = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    log_level = getattr(
        logging,
        log_level_name,
        logging.INFO,
    )

    logging.basicConfig(
        level=log_level,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    app.logger.setLevel(log_level)


def _register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            "status": "error",
            "message": error.description,
        }), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        app.logger.exception(
            "Unhandled application exception",
            exc_info=error,
        )

        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred.",
        }), 500


def _register_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault(
            "X-Content-Type-Options",
            "nosniff",
        )

        response.headers.setdefault(
            "X-Frame-Options",
            "SAMEORIGIN",
        )

        response.headers.setdefault(
            "Referrer-Policy",
            "strict-origin-when-cross-origin",
        )

        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )

        return response


def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    app.config.from_object(Config)

    _configure_logging(app)
    _register_error_handlers(app)
    _register_security_headers(app)

    app.register_blueprint(resume_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(ats_bp)
    app.register_blueprint(rewrite_bp)
    app.register_blueprint(generation_bp)

    @app.route("/", methods=["GET"])
    def home():
        return render_template("index.html")

    return app