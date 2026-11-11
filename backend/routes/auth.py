"""POST /api/auth/login | GET /api/auth/me | POST /api/auth/logout"""
import mysql.connector
from flask import Blueprint, g, jsonify, request

from ..auth import SESSIONS, bearer_token, login, role_required
from ..db import ROLES
from ..errors import friendly

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login_route():
    data = request.get_json(silent=True) or {}
    role, password = data.get("role"), data.get("password") or ""
    if role not in ROLES:
        return jsonify(message="Role must be one of: " + ", ".join(ROLES)), 400
    try:
        info = login(role, password)
    except mysql.connector.Error as e:
        msg, status = friendly(e)
        return jsonify(message=msg), status
    return jsonify(info)


@bp.get("/me")
@role_required()
def me():
    return jsonify(role=g.sess["role"], user_id=g.sess["user_id"],
                   username=g.sess["username"])


@bp.post("/logout")
@role_required()
def logout():
    SESSIONS.pop(bearer_token(), None)
    return jsonify(message="Logged out.")
