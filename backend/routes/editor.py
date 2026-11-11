"""Editor endpoints: browse v_editor_mantras, add Mantras/translations,
the transactional edit-with-history, and the two-tab lock demo."""
import mysql.connector
from flask import Blueprint, g, jsonify, request

from ..auth import role_required
from ..db import conn_for, get_conn, query, run
from ..errors import friendly

bp = Blueprint("editor", __name__, url_prefix="/api/editor")

# lock demo: token -> {"con": connection, "mantra_id": int}
LOCKS = {}


def _page_args():
    page = max(1, request.args.get("page", type=int) or 1)
    size = min(100, max(1, request.args.get("size", type=int) or 20))
    return page, size


@bp.get("/mantras")
@role_required("editor")
def mantras():
    """Searchable, paginated list from v_editor_mantras."""
    search = request.args.get("search", "").strip()
    page, size = _page_args()
    clause, params = "1=1", []
    if search:
        clause = ("CONCAT_WS(' ', veda_name, rishi_name, deity_name, "
                  "sukta_number, mantra_number, COALESCE(metre,''), "
                  "COALESCE(sanskrit_text,''), COALESCE(iast_text,'')) "
                  "LIKE %s")
        params = [f"%{search}%"]
    with conn_for(g.sess) as con:
        total = query(con, f"SELECT COUNT(*) AS n FROM v_editor_mantras "
                           f"WHERE {clause}", params)[0]["n"]
        rows = query(con, "SELECT * FROM v_editor_mantras WHERE " + clause +
                     " ORDER BY mantra_id LIMIT %s OFFSET %s",
                     params + [size, (page - 1) * size])
    return jsonify(rows=rows, total=total, page=page,
                   pages=max(1, -(-total // size)), size=size)


@bp.post("/mantras")
@role_required("editor")
def mantra_add():
    """Add a Mantra; Sukta/Rishi/Deity arrive as ids from dropdowns."""
    d = request.get_json(silent=True) or {}
    for k in ("sukta_id", "rishi_id", "deity_id", "mantra_number"):
        if not d.get(k):
            return jsonify(message=f"{k} is required."), 400
    with conn_for(g.sess) as con:
        new_id, _ = run(con, """INSERT INTO Mantras (sukta_id, rishi_id,
                                 deity_id, mantra_number, metre,
                                 sanskrit_text, iast_text)
                                VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                       (d["sukta_id"], d["rishi_id"], d["deity_id"],
                        d["mantra_number"], d.get("metre") or None,
                        d.get("sanskrit_text") or None,
                        d.get("iast_text") or None))
    return jsonify(message="Mantra added.", mantra_id=new_id)


@bp.post("/mantras/<int:mantra_id>/edit")
@role_required("editor")
def mantra_edit(mantra_id):
    """F5: START TRANSACTION -> SELECT ... FOR UPDATE -> copy old text to
    Mantra_History -> UPDATE -> COMMIT (ROLLBACK on any error)."""
    d = request.get_json(silent=True) or {}
    changed_by = f'{g.sess["username"]} ({g.sess["role"]})'
    con = get_conn(g.sess["role"], g.sess["password"])
    try:
        cur = con.cursor()
        cur.execute("SELECT sanskrit_text, iast_text FROM Mantras "
                    "WHERE mantra_id=%s FOR UPDATE", (mantra_id,))
        old = cur.fetchone()
        if old is None:
            con.rollback()
            return jsonify(message=f"Mantra {mantra_id} not found."), 404
        cur.execute("""INSERT INTO Mantra_History (mantra_id,
                        old_sanskrit_text, old_iast_text, changed_by)
                       VALUES (%s,%s,%s,%s)""",
                    (mantra_id, old[0], old[1], changed_by))
        cur.execute("UPDATE Mantras SET sanskrit_text=%s, iast_text=%s "
                    "WHERE mantra_id=%s",
                    (d.get("sanskrit_text"), d.get("iast_text"), mantra_id))
        con.commit()
        cur.close()
    except mysql.connector.Error as e:
        con.rollback()
        msg, status = friendly(e)
        return jsonify(message=msg), status
    finally:
        con.close()
    return jsonify(message="Updated; old text saved in Mantra_History.",
                   old_sanskrit_text=old[0], old_iast_text=old[1],
                   changed_by=changed_by)


@bp.post("/translations")
@role_required("editor")
def translation_add():
    """Editors can only add translations as 'pending' (status is not in
    their column-level UPDATE grant; the INSERT pins it to pending)."""
    d = request.get_json(silent=True) or {}
    if not (d.get("mantra_id") and d.get("translator_name") and d.get("text")):
        return jsonify(message="mantra_id, translator_name and text "
                               "are required."), 400
    with conn_for(g.sess) as con:
        new_id, _ = run(con, """INSERT INTO Translations (mantra_id,
                                 translator_name, text, status)
                                VALUES (%s,%s,%s,'pending')""",
                       (d["mantra_id"], d["translator_name"], d["text"]))
    return jsonify(message="Translation added as pending.",
                   translation_id=new_id)


# ---------------- lock demo (two browser tabs) ----------------

@bp.post("/lock/start")
@role_required("editor")
def lock_start():
    d = request.get_json(silent=True) or {}
    mantra_id = d.get("mantra_id")
    if not mantra_id:
        return jsonify(message="mantra_id is required."), 400
    if g.token in LOCKS:
        return jsonify(message="You already hold a lock - commit it "
                               "first."), 409
    con = get_conn(g.sess["role"], g.sess["password"])
    try:
        cur = con.cursor()
        cur.execute("SET SESSION innodb_lock_wait_timeout = 10")
        con.commit()   # close implicit tx so start_transaction is clean
        con.start_transaction()
        cur.execute("SELECT mantra_id FROM Mantras WHERE mantra_id=%s "
                    "FOR UPDATE", (mantra_id,))
        if cur.fetchone() is None:
            con.rollback()
            return jsonify(message=f"Mantra {mantra_id} not found."), 404
    except mysql.connector.Error as e:
        con.close()
        msg, status = friendly(e)      # 1205 when another editor holds it
        return jsonify(message=msg), status
    LOCKS[g.token] = {"con": con, "mantra_id": mantra_id}
    return jsonify(message=f"Row {mantra_id} locked. Other editors now "
                           "wait until you commit.", mantra_id=mantra_id)


@bp.post("/lock/commit")
@role_required("editor")
def lock_commit():
    held = LOCKS.pop(g.token, None)
    if not held:
        return jsonify(message="You hold no lock."), 404
    held["con"].commit()
    held["con"].close()
    return jsonify(message="Committed - lock released.",
                   mantra_id=held["mantra_id"])


@bp.get("/lock/status")
@role_required("editor")
def lock_status():
    held = LOCKS.get(g.token)
    return jsonify(holding=bool(held),
                   mantra_id=held["mantra_id"] if held else None)
