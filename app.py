from flask import Flask, jsonify

from app.routes.resume_routes import resume_bp
from app.routes.job_routes import job_bp
from app.routes.ats_routes import ats_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(resume_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(ats_bp)

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "AI Resume Analyzer API is running",
            "status": "success"
        })

    return app