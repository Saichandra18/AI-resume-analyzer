from flask import Flask, jsonify, render_template

from app.routes.resume_routes import resume_bp
from app.routes.job_routes import job_bp
from app.routes.ats_routes import ats_bp


def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    app.register_blueprint(resume_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(ats_bp)

    @app.route("/", methods=["GET"])
    def home():
        return render_template("index.html")

    return app