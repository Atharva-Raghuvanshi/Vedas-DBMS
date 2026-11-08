"""Vedas DBMS one-shot setup: rebuild vedas_db from the sql/ scripts.

Reads DB credentials from the project .env, runs the SQL files in the
correct order as root, then prints row counts and role grants.

Usage (from the project root, with the venv active):
    python scripts/setup_db.py
"""
import os
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

HOST = os.getenv("DB_HOST", "localhost")
DB = os.getenv("DB_NAME", "vedas_db")
ROOT_PW = os.getenv("MYSQL_ROOT_PASSWORD")

# Views must exist before 03_roles.sql grants on them, so the run order
# is: schema -> seed -> views -> roles (not the file numbering).
FILES = [
    "01_schema.sql",
    "04_seed.sql",
    "02_views.sql",
    "03_roles.sql",
]


def split_statements(sql_text):
    """Split a script on ';' at statement ends, dropping -- comments."""
    statements, buf = [], []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or stripped.startswith("#"):
            continue
        buf.append(line)
    joined = "\n".join(buf)
    for stmt in joined.split(";"):
        stmt = stmt.strip()
        if stmt:
            statements.append(stmt)
    return statements


def consume(cur):
    """Drain any result sets (SHOW/SELECT) so the next statement can run."""
    while True:
        try:
            cur.fetchall()
        except mysql.connector.Error:
            pass
        if not cur.nextset():
            break


def main():
    if not ROOT_PW:
        sys.exit("MYSQL_ROOT_PASSWORD not set - check the .env file")

    con = mysql.connector.connect(host=HOST, user="root", password=ROOT_PW,
                                  charset="utf8mb4")
    cur = con.cursor()
    for fname in FILES:
        path = ROOT / "sql" / fname
        print(f"Running {fname} ...")
        for stmt in split_statements(path.read_text(encoding="utf-8")):
            cur.execute(stmt)
            consume(cur)
        con.commit()
        print(f"  done.")

    # verify: row counts
    print("\nRow counts:")
    for table in ["Vedas", "Kandas", "Suktas", "Rishis", "Deities", "Mantras",
                  "Translations", "Word_Meanings", "Themes", "Mantra_Themes",
                  "Bookmarks", "App_Users", "Mantra_History"]:
        cur.execute(f"SELECT COUNT(*) FROM {DB}.{table}")
        print(f"  {table:15s} {cur.fetchone()[0]}")

    # verify: role grants
    print("\nRole grants:")
    for user in ["student_u", "scholar_u", "editor_u", "admin_u"]:
        cur.execute(f"SHOW GRANTS FOR '{user}'@'localhost'")
        for (grant,) in cur.fetchall():
            print(f"  {grant}")

    con.close()
    print("\nSetup complete. Start the app with:")
    print("  streamlit run app/app.py")


if __name__ == "__main__":
    main()
