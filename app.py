from flask import Flask, jsonify

from config import Config
from app.routes.resume_routes import resume_bp
from app.routes.job_routes import job_bp
from app.routes.ats_routes import ats_bp
from app.routes.rewrite_routes import rewrite_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.register_blueprint(resume_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(ats_bp)
    app.register_blueprint(rewrite_bp)

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "AI Resume Analyzer API is running",
            "status": "success"
        })

    return app