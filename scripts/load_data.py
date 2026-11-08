"""Load a SUBSET of the Hugging Face dataset siddharthjadhav6565/vedas
(Rigveda, Griffith 1895 English translation) into vedas_db.

Mapping (the dump is a converted book, so its "Mantra N" headings are
hymns and its numbered verses are the actual mantras):
  mandala -> Kanda of Rigveda
  hymn    -> Sukta
  verse   -> Mantra (mantra_number = verse number)
The dump has English only, so each loaded Mantra row gets a Translations
row (translator 'Ralph T.H. Griffith (dataset)', status 'approved') and
sanskrit_text/iast_text stay NULL. Seed data is never touched: INSERT
IGNORE + UNIQUE(sukta_id, mantra_number) make the load idempotent.

Run:  ./venv/Scripts/python.exe scripts/load_data.py
"""
import os
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
from veda_parser import parse, validate

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

RAW = ROOT / "data" / "raw" / "veda.txt"
MAX_MANTRAS = 300          # the subset cap required by the PRD
VEDA_NAME = "Rigveda"      # the dump IS the Rigveda (Griffith translation)
TRANSLATOR = "Ralph T.H. Griffith (dataset)"


def main():
    records = parse(RAW, max_mantras=MAX_MANTRAS)[:MAX_MANTRAS]
    gaps = validate(records)
    print(f"parsed subset: {len(records)} mantras, "
          f"{gaps} verses skipped by the parser (source formatting)")

    con = mysql.connector.connect(
        host=os.getenv("DB_HOST"), user="root",
        password=os.getenv("MYSQL_ROOT_PASSWORD"),
        database=os.getenv("DB_NAME"), charset="utf8mb4")
    cur = con.cursor()

    # veda + kanda (Rigveda mandala 1 already exists from the seed)
    cur.execute("SELECT veda_id FROM Vedas WHERE veda_name=%s", (VEDA_NAME,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO Vedas (veda_name) VALUES (%s)", (VEDA_NAME,))
        veda_id = cur.lastrowid
    else:
        veda_id = row[0]
    mandalas = sorted({r["mandala"] for r in records})
    kanda_ids = {}
    for m in mandalas:
        cur.execute("SELECT kanda_id FROM Kandas WHERE veda_id=%s AND kanda_number=%s",
                    (veda_id, m))
        row = cur.fetchone()
        if row:
            kanda_ids[m] = row[0]
        else:
            cur.execute("INSERT INTO Kandas (veda_id, kanda_number) VALUES (%s,%s)",
                        (veda_id, m))
            kanda_ids[m] = cur.lastrowid

    mantras_loaded = mantras_existing = translations_added = 0
    con.commit()   # close the implicit transaction opened by the SELECTs
    con.start_transaction()
    try:
        for r in records:
            # rishi + deity (INSERT IGNORE: names are UNIQUE)
            cur.execute("INSERT IGNORE INTO Rishis (rishi_name) VALUES (%s)",
                        (r["rishi"],))
            cur.execute("SELECT rishi_id FROM Rishis WHERE rishi_name=%s",
                        (r["rishi"],))
            rishi_id = cur.fetchone()[0]
            cur.execute("INSERT IGNORE INTO Deities (deity_name) VALUES (%s)",
                        (r["deity"],))
            cur.execute("SELECT deity_id FROM Deities WHERE deity_name=%s",
                        (r["deity"],))
            deity_id = cur.fetchone()[0]

            # sukta (hymn)
            kanda_id = kanda_ids[r["mandala"]]
            cur.execute("INSERT IGNORE INTO Suktas (kanda_id, sukta_number) "
                        "VALUES (%s,%s)", (kanda_id, r["hymn"]))
            cur.execute("SELECT sukta_id FROM Suktas WHERE kanda_id=%s AND sukta_number=%s",
                        (kanda_id, r["hymn"]))
            sukta_id = cur.fetchone()[0]

            # mantra (verse); UNIQUE(sukta_id, mantra_number) guards reruns
            cur.execute("""INSERT IGNORE INTO Mantras
                           (sukta_id, rishi_id, deity_id, mantra_number,
                            metre, sanskrit_text, iast_text)
                           VALUES (%s,%s,%s,%s,NULL,NULL,NULL)""",
                        (sukta_id, rishi_id, deity_id, r["verse"]))
            if cur.rowcount:
                mantra_id = cur.lastrowid
                mantras_loaded += 1
                # the dump's text is the Griffith translation
                cur.execute("""INSERT INTO Translations
                               (mantra_id, translator_name, text, status)
                               VALUES (%s,%s,%s,'approved')""",
                            (mantra_id, TRANSLATOR, r["text"]))
                translations_added += 1
            else:
                mantras_existing += 1
        con.commit()
    except Exception as e:
        con.rollback()
        sys.exit(f"load failed, rolled back: {e}")

    print(f"mantras loaded: {mantras_loaded}  "
          f"(already present: {mantras_existing})")
    print(f"translations added ({TRANSLATOR}, approved): {translations_added}")

    # final state
    cur.execute("""SELECT v.veda_name, COUNT(m.mantra_id) FROM Vedas v
                   JOIN Kandas k ON k.veda_id=v.veda_id
                   JOIN Suktas s ON s.kanda_id=k.kanda_id
                   JOIN Mantras m ON m.sukta_id=s.sukta_id
                   GROUP BY v.veda_name""")
    print("\nmantras per veda now:")
    for name, n in cur.fetchall():
        print(f"  {name}: {n}")
    cur.execute("SELECT COUNT(*) FROM Mantras WHERE mantra_id <= 42")
    seed_intact = cur.fetchone()[0] == 42
    print(f"seed mantras intact (ids 1-42 all present): {seed_intact}")
    con.close()
    sys.exit(0 if seed_intact else 1)


if __name__ == "__main__":
    main()
