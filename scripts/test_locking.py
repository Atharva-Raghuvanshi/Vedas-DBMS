"""Prove that a second editor session WAITS on SELECT ... FOR UPDATE
until the first session commits (CSBB 204 concurrency demo, PRD section 6).

Single process, two editor_u connections, two phases:
  Phase 1: A locks mantra 1 and holds it. B tries the same locking read
           with a 5 s lock timeout -> B blocks and fails with ERROR 1205
           after ~5 s. That wait IS the row lock doing its job.
  Phase 2: A updates the row and commits. B retries the same locking read
           -> returns immediately and sees A's NEW text.

Run:  ./venv/Scripts/python.exe scripts/test_locking.py
"""
import os
import sys
import time
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

HOST = os.getenv("DB_HOST", "localhost")
DB = os.getenv("DB_NAME", "vedas_db")
PW = os.getenv("DB_PASSWORD", "changeme")
MANTRA_ID = 1
NEW_TEXT = "अग्निमीळे पुरोहितं (lock test edit)"

sys.exit_code = 0


def connect():
    return mysql.connector.connect(host=HOST, user="editor_u", password=PW,
                                   database=DB, charset="utf8mb4")


def fail(msg):
    print(f"  FAIL: {msg}")
    sys.exit_code = 1


def main():
    a, b = connect(), connect()
    cur_a, cur_b = a.cursor(), b.cursor()

    cur_a.execute("SELECT sanskrit_text FROM Mantras WHERE mantra_id=%s",
                  (MANTRA_ID,))
    original = cur_a.fetchone()[0]
    cur_a.fetchall()
    a.commit()   # close the implicit transaction opened by the SELECT

    # ---------- Phase 1: B must WAIT while A holds the lock ----------
    print(f"PHASE 1: A locks mantra {MANTRA_ID} with SELECT ... FOR UPDATE")
    a.start_transaction()
    cur_a.execute("SELECT sanskrit_text FROM Mantras WHERE mantra_id=%s "
                  "FOR UPDATE", (MANTRA_ID,))
    cur_a.fetchall()

    cur_b.execute("SET SESSION innodb_lock_wait_timeout = 5")
    b.start_transaction()
    print("         B tries the same locking read (5 s lock timeout) ...")
    t0 = time.time()
    waited = False
    try:
        cur_b.execute("SELECT sanskrit_text FROM Mantras WHERE mantra_id=%s "
                      "FOR UPDATE", (MANTRA_ID,))
        cur_b.fetchall()
        fail("B was NOT blocked - row lock did not work")
    except mysql.connector.Error as e:
        elapsed = time.time() - t0
        if e.errno == 1205:
            waited = True
            print(f"         B blocked for {elapsed:.1f} s then got "
                  f"ERROR 1205 (lock wait timeout) -> B waited on the lock")
            if elapsed < 3:
                fail(f"B failed too fast ({elapsed:.1f}s) - it never waited")
        else:
            fail(f"unexpected error: {e}")
    b.rollback()

    # ---------- Phase 2: A commits, B proceeds and sees the new text ----------
    print("PHASE 2: A updates the row and COMMITS (releases the lock)")
    cur_a.execute("UPDATE Mantras SET sanskrit_text=%s WHERE mantra_id=%s",
                  (NEW_TEXT, MANTRA_ID))
    a.commit()

    print("         B retries the same locking read ...")
    t0 = time.time()
    b.start_transaction()
    cur_b.execute("SELECT sanskrit_text FROM Mantras WHERE mantra_id=%s "
                  "FOR UPDATE", (MANTRA_ID,))
    row = cur_b.fetchone()
    cur_b.fetchall()
    b.commit()
    elapsed = time.time() - t0
    print(f"         B got the row in {elapsed:.2f} s and sees A's new text: "
          f"{row[0][:30]}...")
    if elapsed > 2:
        fail(f"B was slow ({elapsed:.2f}s) even though A had committed")
    if row[0] != NEW_TEXT:
        fail("B did not see A's committed text")

    # ---------- restore ----------
    restore = connect()
    rc = restore.cursor()
    rc.execute("UPDATE Mantras SET sanskrit_text=%s WHERE mantra_id=%s",
               (original, MANTRA_ID))
    restore.commit()
    restore.close()
    a.close(); b.close()

    verdict = ("PASS - second editor waits until the first commits"
               if waited and sys.exit_code == 0 else
               "FAIL - see messages above")
    print(f"\nRESULT: {verdict}")
    print("(mantra 1 text restored, no history rows written)")
    sys.exit(sys.exit_code)


if __name__ == "__main__":
    main()
