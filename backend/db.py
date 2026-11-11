"""Vedas DBMS Flask backend - database helpers.

One MySQL connection per request, opened as the logged-in role's own
MySQL user ({role}_u). MySQL verifies the password against its hashed
storage at connect time, and every statement then runs with exactly
that role's GRANTs - permissions are enforced by the database.
"""
import os
from contextlib import contextmanager
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

# the credentials live in the project-root .env (same file the Streamlit app used)
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

HOST = os.getenv("DB_HOST", "localhost")
DB = os.getenv("DB_NAME", "vedas_db")

ROLES = ("student", "scholar", "editor", "admin")


def get_conn(role, password):
    """Connect as {role}_u; wrong password raises mysql error 1045."""
    return mysql.connector.connect(
        host=HOST, user=f"{role}_u", password=password,
        database=DB, charset="utf8mb4")


def exists(con, sql, params=None):
    """True if any row matches - used to tell 'no such row' (404) apart
    from 'UPDATE matched the row but changed nothing' (rowcount 0)."""
    return bool(query(con, sql, params))


@contextmanager
def conn_for(sess):
    """Connection scoped to one request (sess = login session dict)."""
    con = get_conn(sess["role"], sess["password"])
    try:
        yield con
    finally:
        con.close()


def query(con, sql, params=None):
    """Run a SELECT and return a list of row dicts (parameterized only)."""
    cur = con.cursor()
    cur.execute(sql, params or ())
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    return rows


def run(con, sql, params=None):
    """Run an INSERT/UPDATE/DELETE, commit, return (lastrowid, rowcount)."""
    cur = con.cursor()
    cur.execute(sql, params or ())
    con.commit()
    last, count = cur.lastrowid, cur.rowcount
    cur.close()
    return last, count
