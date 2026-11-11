"""Scholar endpoints - word meanings through v_scholar_words."""
from flask import Blueprint, g, jsonify, request

from ..auth import role_required
from ..db import conn_for, exists, query, run

bp = Blueprint("scholar", __name__, url_prefix="/api/scholar")


@bp.get("/words")
@role_required("scholar")
def words():
    mantra_id = request.args.get("mantra_id", type=int)
    if not mantra_id:
        return jsonify(message="mantra_id is required."), 400
    with conn_for(g.sess) as con:
        rows = query(con, """SELECT mantra_id, word_order, sanskrit_word,
                                    dhatu, english_meaning, veda_name,
                                    sukta_number, mantra_number
                             FROM v_scholar_words WHERE mantra_id=%s
                             ORDER BY word_order""", (mantra_id,))
    return jsonify(rows=rows)


@bp.post("/words")
@role_required("scholar")
def word_add():
    d = request.get_json(silent=True) or {}
    required = ("mantra_id", "word_order", "sanskrit_word")
    if not all(d.get(k) for k in required):
        return jsonify(message="mantra_id, word_order and sanskrit_word "
                               "are required."), 400
    with conn_for(g.sess) as con:
        run(con, """INSERT INTO Word_Meanings
                    (mantra_id, word_order, sanskrit_word, dhatu,
                     english_meaning) VALUES (%s,%s,%s,%s,%s)""",
            (d["mantra_id"], d["word_order"], d["sanskrit_word"],
             d.get("dhatu") or None, d.get("english_meaning")))
    return jsonify(message="Word added.")


@bp.put("/words")
@role_required("scholar")
def word_edit():
    """Edit a word's content; word_order itself stays fixed (it is the key)."""
    d = request.get_json(silent=True) or {}
    if not (d.get("mantra_id") and d.get("word_order")):
        return jsonify(message="mantra_id and word_order are required."), 400
    with conn_for(g.sess) as con:
        _, count = run(con, """UPDATE Word_Meanings SET sanskrit_word=%s,
                               dhatu=%s, english_meaning=%s
                               WHERE mantra_id=%s AND word_order=%s""",
                       (d.get("sanskrit_word"), d.get("dhatu") or None,
                        d.get("english_meaning"), d["mantra_id"],
                        d["word_order"]))
        there = exists(con, "SELECT 1 FROM Word_Meanings WHERE mantra_id=%s "
                            "AND word_order=%s",
                       (d["mantra_id"], d["word_order"]))
    if not count and not there:
        return jsonify(message="No word at that position."), 404
    return jsonify(message="Word updated.")
