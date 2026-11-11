"""Map MySQL errors to readable JSON messages - the UI must never show a
stack trace. friendly(e) -> (message, http_status)."""
import mysql.connector


def friendly(e):
    errno = getattr(e, "errno", None)
    text = str(e)

    if errno == 1045:
        return "Login failed: wrong role or password.", 401
    if errno == 1062:                      # duplicate key
        if "word_order" in text:
            return ("Duplicate: this Mantra already has a word at that "
                    "position (UNIQUE mantra_id+word_order)."), 409
        if "sukta_id" in text:
            return ("Duplicate: this Sukta already has a Mantra with that "
                    "number (UNIQUE sukta_id+mantra_number)."), 409
        if "bookmarks" in text.lower() or "PRIMARY" in text:
            return "Already bookmarked.", 409
        return "Duplicate value rejected by a UNIQUE constraint.", 409
    if errno in (1142, 1143):              # GRANT/REVOKE denial
        return f"MySQL permission denied ({errno}): {text}", 403
    if errno == 1205:
        return ("Row is locked by another editor - wait a moment and retry "
                "(lock wait timeout)."), 409
    if errno == 1213:
        return "Deadlock detected - please retry.", 409
    if errno == 1451:
        return ("Cannot delete: other records reference this row "
                "(foreign key RESTRICT)."), 409
    if errno in (1452, 1216, 1217):
        return ("The referenced row does not exist - choose a valid value "
                "from the dropdown."), 400
    if errno in (2003, 2005, 1049):
        return "Cannot reach the MySQL server - is it running?", 503

    return text or "Unexpected error", 500
