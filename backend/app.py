"""Vedas DBMS - Flask REST API for the React frontend.

Run from the project root:
    .\\venv\\Scripts\\python.exe -m flask --app backend.app run --port 5000
"""
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .errors import friendly
from .routes import (admin_bp, auth_bp, editor_bp, options_bp, scholar_bp,
                     student_bp)


def create_app():
    app = Flask(__name__)
    CORS(app)   # dev convenience; the Vite proxy avoids needing it anyway

    for bp in (auth_bp, options_bp, student_bp, scholar_bp, editor_bp,
               admin_bp):
        app.register_blueprint(bp)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(Exception)
    def any_error(e):
        """Every failure becomes readable JSON - never a stack trace."""
        if isinstance(e, HTTPException):
            return jsonify(message=e.description), e.code
        msg, status = friendly(e)
        return jsonify(message=msg, detail=str(e)), status

    return app


app = create_app()
