"""Student endpoints - read-only through the two student views, plus
bookmark management. Everything runs as student_u, so MySQL blocks
anything else (the /demo-denied endpoint relies on that)."""
from flask import Blueprint, g, jsonify, request

from ..auth import role_required
from ..db import conn_for, query, run

bp = Blueprint("student", __name__, url_prefix="/api/student")


def _int_arg(name):
    try:
        return int(request.args.get(name, ""))
    except (TypeError, ValueError):
        return None


@bp.get("/mantras")
@role_required("student")
def search():
    """Search + paginate v_student_mantras (never loads everything)."""
    a = request.args
    where = ["veda_name LIKE %s", "rishi_name LIKE %s", "deity_name LIKE %s",
             "COALESCE(metre,'') LIKE %s", "COALESCE(themes,'') LIKE %s",
             "COALESCE(sanskrit_text,'') LIKE %s"]
    params = [f"%{a.get('veda', '')}%", f"%{a.get('rishi', '')}%",
              f"%{a.get('deity', '')}%", f"%{a.get('metre', '')}%",
              f"%{a.get('theme', '')}%", f"%{a.get('word', '')}%"]
    kanda, sukta = _int_arg("kanda"), _int_arg("sukta")
    if kanda is not None:
        where.append("kanda_name = %s")
        params.append(f"Kanda {kanda}")
    if sukta is not None:
        where.append("sukta_number = %s")
        params.append(sukta)
    clause = " AND ".join(where)

    page = max(1, _int_arg("page") or 1)
    size = min(100, max(1, _int_arg("size") or 20))

    with conn_for(g.sess) as con:
        total = query(con, f"SELECT COUNT(*) AS n FROM v_student_mantras "
                           f"WHERE {clause}", params)[0]["n"]
        rows = query(con, """SELECT mantra_id, veda_name, kanda_name,
                                     sukta_number, mantra_number, rishi_name,
                                     deity_name, metre, sanskrit_text,
                                     iast_text, themes, translation
                              FROM v_student_mantras WHERE """ + clause +
                        " ORDER BY mantra_id LIMIT %s OFFSET %s",
                        params + [size, (page - 1) * size])
    return jsonify(rows=rows, total=total, page=page,
                   pages=max(1, -(-total // size)), size=size)


@bp.get("/bookmarks")
@role_required("student")
def bookmarks_list():
    """Own bookmarks, as full mantra cards (join of the two views)."""
    uid = g.sess["user_id"]
    with conn_for(g.sess) as con:
        rows = query(con, """SELECT m.* FROM v_student_mantras m
                             JOIN v_student_bookmarks b
                               ON b.mantra_id = m.mantra_id
                             WHERE b.user_id = %s ORDER BY m.mantra_id""",
                     (uid,))
    return jsonify(rows=rows, user_id=uid)


@bp.post("/bookmarks")
@role_required("student")
def bookmark_add():
    data = request.get_json(silent=True) or {}
    mantra_id = data.get("mantra_id")
    if not mantra_id:
        return jsonify(message="mantra_id is required."), 400
    with conn_for(g.sess) as con:
        run(con, "INSERT INTO Bookmarks (user_id, mantra_id) VALUES (%s,%s)",
            (g.sess["user_id"], mantra_id))
    return jsonify(message="Bookmarked.")


@bp.delete("/bookmarks/<int:mantra_id>")
@role_required("student")
def bookmark_remove(mantra_id):
    with conn_for(g.sess) as con:
        _, count = run(con, "DELETE FROM Bookmarks WHERE user_id=%s "
                            "AND mantra_id=%s",
                       (g.sess["user_id"], mantra_id))
    if not count:
        return jsonify(message="That mantra was not bookmarked."), 404
    return jsonify(message="Bookmark removed.")


@bp.get("/demo-denied")
@role_required("student")
def demo_denied():
    """F11 demo: attempt an UPDATE as student_u and show MySQL blocking it."""
    import mysql.connector
    from ..errors import friendly
    try:
        with conn_for(g.sess) as con:
            run(con, "UPDATE Mantras SET metre='x' WHERE mantra_id=1")
    except mysql.connector.Error as e:
        msg, _ = friendly(e)
        return jsonify(denied=True, message=msg, mysql_error=str(e))
    return jsonify(denied=False, message="Unexpected: the UPDATE worked!"), 500
