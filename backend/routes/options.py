"""GET /api/options/<kind> - dropdown data for every role, from the
migration view v_filter_options (sql/07_react_migration.sql)."""
from flask import Blueprint, g, jsonify

from ..auth import role_required
from ..db import conn_for, query

bp = Blueprint("options", __name__, url_prefix="/api/options")

KINDS = ("veda", "kanda", "sukta", "rishi", "deity", "theme", "metre")


@bp.get("/<kind>")
@role_required("student", "scholar", "editor", "admin")
def options(kind):
    if kind not in KINDS:
        return jsonify(message=f"kind must be one of {KINDS}"), 400
    order = "item_id" if kind == "sukta" else "label"   # keep 1..10..N order
    with conn_for(g.sess) as con:
        rows = query(con, "SELECT item_id, label FROM v_filter_options "
                          f"WHERE kind=%s ORDER BY {order}", (kind,))
    return jsonify(rows)
