"""Admin endpoints: approve translations, six reports, CRUD on the
reference tables, Mantra_History and theme tagging. Runs as admin_u
(ALL privileges) - the only role allowed to UPDATE Translations.status
or DELETE anything."""
from flask import Blueprint, g, jsonify, request

from ..auth import role_required
from ..db import conn_for, exists, query, run

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

REPORTS = {
    "mantras_per_veda": """SELECT v.veda_name AS label, COUNT(m.mantra_id) AS value
        FROM Vedas v JOIN Kandas k ON k.veda_id=v.veda_id
        JOIN Suktas s ON s.kanda_id=k.kanda_id
        JOIN Mantras m ON m.sukta_id=s.sukta_id
        GROUP BY v.veda_name ORDER BY value DESC""",
    "mantras_per_rishi": """SELECT r.rishi_name AS label, COUNT(*) AS value
        FROM Rishis r JOIN Mantras m ON m.rishi_id=m.rishi_id
        GROUP BY r.rishi_name ORDER BY value DESC""",
    "mantras_per_deity": """SELECT d.deity_name AS label, COUNT(*) AS value
        FROM Deities d JOIN Mantras m ON m.deity_id=m.deity_id
        GROUP BY d.deity_name ORDER BY value DESC""",
    "translations_per_translator": """SELECT translator_name AS label,
        COUNT(*) AS value FROM Translations
        GROUP BY translator_name ORDER BY value DESC""",
    "suktas_without_translation": """SELECT s.sukta_id AS item_id,
        CONCAT(v.veda_name, ' ', k.kanda_number, '.', s.sukta_number) AS label,
        0 AS value
        FROM Suktas s
        JOIN Kandas k ON k.kanda_id=s.kanda_id
        JOIN Vedas v ON v.veda_id=k.veda_id
        JOIN Mantras m ON m.sukta_id=s.sukta_id
        LEFT JOIN Translations t ON t.mantra_id=m.mantra_id
        GROUP BY s.sukta_id, label HAVING COUNT(t.translation_id)=0""",
    "structure_per_veda": """SELECT veda_name AS label, kandas, suktas,
        mantras FROM v_admin_summary""",
}

# whitelist for the CRUD routes: table/column names never come from the
# client, values always go in as parameters
ENTITIES = {
    "vedas":   {"table": "Vedas",   "pk": "veda_id",
                "fields": {"veda_name": "s"}},
    "kandas":  {"table": "Kandas",  "pk": "kanda_id",
                "fields": {"veda_id": "i", "kanda_number": "i"}},
    "suktas":  {"table": "Suktas",  "pk": "sukta_id",
                "fields": {"kanda_id": "i", "sukta_number": "i"}},
    "rishis":  {"table": "Rishis",  "pk": "rishi_id",
                "fields": {"rishi_name": "s"}},
    "deities": {"table": "Deities", "pk": "deity_id",
                "fields": {"deity_name": "s"}},
    "themes":  {"table": "Themes",  "pk": "theme_id",
                "fields": {"theme_name": "s"}},
    "mantras": {"table": "Mantras", "pk": "mantra_id",
                "fields": {"sukta_id": "i", "rishi_id": "i", "deity_id": "i",
                           "mantra_number": "i", "metre": "s",
                           "sanskrit_text": "s", "iast_text": "s"}},
}


@bp.get("/translations")
@role_required("admin")
def translations():
    status = request.args.get("status", "pending")
    with conn_for(g.sess) as con:
        rows = query(con, "SELECT translation_id, mantra_id, translator_name, "
                          "text, status FROM Translations WHERE status=%s "
                          "ORDER BY translation_id", (status,))
    return jsonify(rows=rows)


@bp.post("/translations/<int:tid>/approve")
@role_required("admin")
def approve(tid):
    with conn_for(g.sess) as con:
        _, count = run(con, "UPDATE Translations SET status='approved' "
                            "WHERE translation_id=%s AND status='pending'",
                       (tid,))
    if not count:
        return jsonify(message="No pending translation with that id."), 404
    return jsonify(message=f"Translation {tid} approved.")


@bp.get("/reports/<key>")
@role_required("admin")
def report(key):
    if key not in REPORTS:
        return jsonify(message=f"Unknown report '{key}'."), 400
    with conn_for(g.sess) as con:
        rows = query(con, REPORTS[key])
    return jsonify(rows=rows)


@bp.get("/history")
@role_required("admin")
def history():
    mantra_id = request.args.get("mantra_id", type=int)
    clause, params = "1=1", []
    if mantra_id:
        clause, params = "h.mantra_id=%s", [mantra_id]
    with conn_for(g.sess) as con:
        rows = query(con, "SELECT h.history_id, h.mantra_id, "
                          "h.old_sanskrit_text, h.old_iast_text, "
                          "h.changed_by, h.changed_at FROM Mantra_History h "
                          f"WHERE {clause} ORDER BY h.changed_at DESC "
                          "LIMIT 200", params)
    return jsonify(rows=rows)


@bp.delete("/translations/<int:tid>")
@role_required("admin")
def translation_delete(tid):
    with conn_for(g.sess) as con:
        _, count = run(con, "DELETE FROM Translations WHERE translation_id=%s",
                       (tid,))
    if not count:
        return jsonify(message="No translation with that id."), 404
    return jsonify(message="Translation deleted.")


@bp.delete("/words/<int:mantra_id>/<int:word_order>")
@role_required("admin")
def word_delete(mantra_id, word_order):
    with conn_for(g.sess) as con:
        _, count = run(con, "DELETE FROM Word_Meanings WHERE mantra_id=%s "
                            "AND word_order=%s", (mantra_id, word_order))
    if not count:
        return jsonify(message="No word at that position."), 404
    return jsonify(message="Word deleted.")


@bp.delete("/history/<int:mantra_id>")
@role_required("admin")
def history_clear(mantra_id):
    """Remove the history rows of one Mantra (used before deleting it)."""
    with conn_for(g.sess) as con:
        _, count = run(con, "DELETE FROM Mantra_History WHERE mantra_id=%s",
                       (mantra_id,))
    return jsonify(message=f"{count} history rows removed.")


# ---------------- reference-table CRUD ----------------

def _clean_values(entity, data):
    """Keep only whitelisted fields, with the right type."""
    out = {}
    for f, typ in entity["fields"].items():
        if f in data and data[f] not in (None, ""):
            out[f] = int(data[f]) if typ == "i" else str(data[f])
    return out


@bp.get("/<entity>")
@role_required("admin")
def entity_list(entity):
    if entity not in ENTITIES:
        return jsonify(message=f"Unknown entity '{entity}'."), 400
    e = ENTITIES[entity]
    with conn_for(g.sess) as con:
        rows = query(con, f"SELECT * FROM {e['table']} ORDER BY {e['pk']}")
    return jsonify(rows=rows)


@bp.post("/<entity>")
@role_required("admin")
def entity_add(entity):
    if entity not in ENTITIES:
        return jsonify(message=f"Unknown entity '{entity}'."), 400
    e = ENTITIES[entity]
    values = _clean_values(e, request.get_json(silent=True) or {})
    if not values:
        return jsonify(message="No valid fields to insert."), 400
    cols = ", ".join(values)
    marks = ", ".join(["%s"] * len(values))
    with conn_for(g.sess) as con:
        new_id, _ = run(con, f"INSERT INTO {e['table']} ({cols}) "
                             f"VALUES ({marks})", list(values.values()))
    return jsonify(message="Added.", id=new_id)


@bp.put("/<entity>/<int:item_id>")
@role_required("admin")
def entity_update(entity, item_id):
    if entity not in ENTITIES:
        return jsonify(message=f"Unknown entity '{entity}'."), 400
    e = ENTITIES[entity]
    values = _clean_values(e, request.get_json(silent=True) or {})
    if not values:
        return jsonify(message="No valid fields to update."), 400
    sets = ", ".join(f"{c}=%s" for c in values)
    with conn_for(g.sess) as con:
        _, count = run(con, f"UPDATE {e['table']} SET {sets} "
                            f"WHERE {e['pk']}=%s",
                       list(values.values()) + [item_id])
        there = exists(con, f"SELECT 1 FROM {e['table']} WHERE {e['pk']}=%s",
                       (item_id,))
    if not count and not there:
        return jsonify(message="No row with that id."), 404
    return jsonify(message="Updated.")


@bp.delete("/<entity>/<int:item_id>")
@role_required("admin")
def entity_delete(entity, item_id):
    if entity not in ENTITIES:
        return jsonify(message=f"Unknown entity '{entity}'."), 400
    e = ENTITIES[entity]
    with conn_for(g.sess) as con:
        _, count = run(con, f"DELETE FROM {e['table']} WHERE {e['pk']}=%s",
                       (item_id,))
    if not count:
        return jsonify(message="No row with that id."), 404
    return jsonify(message="Deleted.")     # FK RESTRICT errors map to 409


# ---------------- theme tagging ----------------

@bp.get("/mantras/<int:mantra_id>/themes")
@role_required("admin")
def mantra_themes(mantra_id):
    with conn_for(g.sess) as con:
        rows = query(con, """SELECT t.theme_id, t.theme_name
                             FROM Mantra_Themes mt
                             JOIN Themes t ON t.theme_id=mt.theme_id
                             WHERE mt.mantra_id=%s ORDER BY t.theme_name""",
                     (mantra_id,))
    return jsonify(rows=rows)


@bp.post("/mantras/<int:mantra_id>/themes")
@role_required("admin")
def tag_add(mantra_id):
    d = request.get_json(silent=True) or {}
    if not d.get("theme_id"):
        return jsonify(message="theme_id is required."), 400
    with conn_for(g.sess) as con:
        run(con, "INSERT INTO Mantra_Themes (mantra_id, theme_id) "
                 "VALUES (%s,%s)", (mantra_id, d["theme_id"]))
    return jsonify(message="Theme assigned.")


@bp.delete("/mantras/<int:mantra_id>/themes/<int:theme_id>")
@role_required("admin")
def tag_remove(mantra_id, theme_id):
    with conn_for(g.sess) as con:
        _, count = run(con, "DELETE FROM Mantra_Themes WHERE mantra_id=%s "
                            "AND theme_id=%s", (mantra_id, theme_id))
    if not count:
        return jsonify(message="That theme was not assigned."), 404
    return jsonify(message="Theme removed.")
