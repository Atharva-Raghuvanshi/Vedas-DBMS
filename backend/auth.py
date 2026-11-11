"""Login sessions for the Flask API.

The client gets a random bearer token; the SERVER keeps
{role, user_id, username, password} and opens a fresh MySQL connection
as {role}_u on every request. Passwords are verified by MySQL itself
against its hashed storage - we never store or hash passwords ourselves.
(In-memory sessions: fine for the single-process demo server.)
"""
import secrets
from functools import wraps

import mysql.connector
from flask import g, jsonify, request

from .db import ROLES, get_conn, query

SESSIONS = {}   # token -> {"role", "user_id", "username", "password"}


def login(role, password):
    """Verify role+password with a real MySQL connect; return session."""
    con = get_conn(role, password)          # 1045 if wrong password
    try:
        rows = query(con, "SELECT user_id, username FROM v_app_users "
                          "WHERE role=%s ORDER BY user_id LIMIT 1", (role,))
    finally:
        con.close()
    user_id, username = (rows[0]["user_id"], rows[0]["username"]) if rows \
        else (None, role)
    token = secrets.token_urlsafe(24)
    SESSIONS[token] = {"role": role, "user_id": user_id,
                       "username": username, "password": password}
    return {"token": token, "role": role, "user_id": user_id,
            "username": username}


def bearer_token():
    header = request.headers.get("Authorization", "")
    return header[7:] if header.startswith("Bearer ") else None


def role_required(*roles):
    """Route gate: 401 without a session, 403 if the role is not allowed.
    The MySQL GRANTs remain the real enforcement behind it."""
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            sess = SESSIONS.get(bearer_token() or "")
            if not sess:
                return jsonify(message="Not logged in."), 401
            if roles and sess["role"] not in roles:
                return jsonify(message=f"A '{sess['role']}' may not do "
                                        "this."), 403
            g.sess = sess
            g.token = bearer_token()
            return fn(*args, **kwargs)
        return wrapper
    return deco
