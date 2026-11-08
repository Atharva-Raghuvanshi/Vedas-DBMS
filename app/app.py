import os
from pathlib import Path

import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# load .env from the project root (one level above app/)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

st.set_page_config(page_title="Vedas DBMS", layout="wide")

HOST = os.getenv("DB_HOST", "localhost")
DB = os.getenv("DB_NAME", "vedas_db")
PW = os.getenv("DB_PASSWORD", "changeme")   # same password for all demo users


def connect(role):
    return mysql.connector.connect(host=HOST, user=f"{role}_u", password=PW,
                                   database=DB, charset="utf8mb4")


def query(role, sql, params=None):
    con = connect(role)
    try:
        return pd.read_sql(sql, con, params=params)
    finally:
        con.close()


def run(role, sql, params=None):
    con = connect(role)
    try:
        cur = con.cursor()
        cur.execute(sql, params)
        con.commit()
    finally:
        con.close()


REPORTS = {
    "Mantras per Veda": """SELECT v.veda_name, COUNT(m.mantra_id) AS mantras FROM Vedas v
        JOIN Kandas k ON k.veda_id=v.veda_id JOIN Suktas s ON s.kanda_id=k.kanda_id
        JOIN Mantras m ON m.sukta_id=s.sukta_id GROUP BY v.veda_name""",
    "Mantras per Rishi": """SELECT r.rishi_name, COUNT(*) AS mantras FROM Rishis r
        JOIN Mantras m ON m.rishi_id=r.rishi_id GROUP BY r.rishi_name ORDER BY mantras DESC""",
    "Mantras per deity": """SELECT d.deity_name, COUNT(*) AS mantras FROM Deities d
        JOIN Mantras m ON m.deity_id=d.deity_id GROUP BY d.deity_name ORDER BY mantras DESC""",
    "Translations per translator": """SELECT translator_name, COUNT(*) AS translations
        FROM Translations GROUP BY translator_name""",
    "Suktas with no translation": """SELECT s.sukta_id, s.sukta_number FROM Suktas s
        JOIN Mantras m ON m.sukta_id=s.sukta_id LEFT JOIN Translations t ON t.mantra_id=m.mantra_id
        GROUP BY s.sukta_id, s.sukta_number HAVING COUNT(t.translation_id)=0""",
    "Structure per Veda": "SELECT * FROM v_admin_summary",
}

# ---------------- sidebar login ----------------
st.sidebar.title("Vedas DBMS")
role = st.sidebar.selectbox("Login as", ["student", "scholar", "editor", "admin"])
user_id = st.sidebar.number_input("User ID", min_value=1, value=1)
st.title(f"{role.capitalize()} panel")

try:
    # ---------------- STUDENT ----------------
    if role == "student":
        tab1, tab2 = st.tabs(["Search", "My bookmarks"])
        with tab1:
            c = st.columns(4)
            veda = c[0].text_input("Veda")
            rishi = c[1].text_input("Rishi")
            deity = c[2].text_input("Deity")
            word = c[3].text_input("Sanskrit word")
            where = """WHERE veda_name LIKE %s AND rishi_name LIKE %s
                       AND deity_name LIKE %s
                       AND COALESCE(sanskrit_text, '') LIKE %s"""
            args = [f"%{veda}%", f"%{rishi}%", f"%{deity}%", f"%{word}%"]
            # --- pagination: 50 rows per page, Prev / 1 2 3 ... / Next ---
            PAGE_SIZE = 50
            n_total = int(query("student",
                f"SELECT COUNT(*) AS n FROM v_student_mantras {where}",
                args).iloc[0, 0])
            total_pages = max(1, (n_total + PAGE_SIZE - 1) // PAGE_SIZE)
            if "page" not in st.session_state:
                st.session_state.page = 1
            st.session_state.page = min(st.session_state.page, total_pages)
            pc = st.columns(total_pages + 2 if total_pages <= 10 else 2)
            # keyed buttons: detect the click BEFORE rendering so the
            # current-page highlight is never one step behind
            for p in range(1, total_pages + 1):
                if st.session_state.get(f"pg{p}"):
                    st.session_state.page = p
            if pc[0].button("Prev") and st.session_state.page > 1:
                st.session_state.page -= 1
            if total_pages <= 10:
                for p in range(1, total_pages + 1):
                    pc[p].button(str(p), key=f"pg{p}",
                                 type="primary" if p == st.session_state.page
                                 else "secondary")
            if pc[-1].button("Next") and st.session_state.page < total_pages:
                st.session_state.page += 1
            st.caption(f"Page {st.session_state.page} of {total_pages} - "
                       f"{n_total} mantras match")
            offset = (st.session_state.page - 1) * PAGE_SIZE
            sql = f"""SELECT mantra_id, veda_name, sukta_number, mantra_number, rishi_name,
                            deity_name, metre, sanskrit_text, iast_text, translation
                     FROM v_student_mantras {where}
                     ORDER BY mantra_id LIMIT %s OFFSET %s"""
            st.dataframe(query("student", sql, args + [PAGE_SIZE, offset]))
            mid = st.number_input("Mantra ID to bookmark", min_value=1, value=1)
            if st.button("Bookmark"):
                run("student", "INSERT INTO Bookmarks (user_id, mantra_id) VALUES (%s, %s)", [user_id, mid])
                st.success("Bookmarked")
            if st.button("Try to edit a Mantra (should fail)"):
                try:
                    run("student", "UPDATE Mantras SET metre='x' WHERE mantra_id=1")
                except Exception as e:
                    st.error(f"Blocked by MySQL: {e}")
        with tab2:
            st.dataframe(query("student", "SELECT * FROM v_student_bookmarks WHERE user_id=%s", [user_id]))

    # ---------------- SCHOLAR ----------------
    elif role == "scholar":
        mid = st.number_input("Mantra ID", min_value=1, value=1)
        st.dataframe(query("scholar", "SELECT * FROM v_scholar_words WHERE mantra_id=%s ORDER BY word_order", [mid]))
        st.subheader("Add word meaning")
        a, b, c, d = st.columns(4)
        order = a.number_input("Order", min_value=1, value=1)
        sw = b.text_input("Sanskrit word")
        dh = c.text_input("Dhatu (root)")
        en = d.text_input("English meaning")
        if st.button("Save word"):
            run("scholar", """INSERT INTO Word_Meanings (mantra_id, word_order, sanskrit_word, dhatu, english_meaning)
                              VALUES (%s,%s,%s,%s,%s)""", [mid, order, sw, dh, en])
            st.success("Saved")

    # ---------------- EDITOR ----------------
    elif role == "editor":
        tab1, tab2, tab3 = st.tabs(["Add translation", "Edit Mantra", "Lock demo"])
        with tab1:
            mid = st.number_input("Mantra ID", min_value=1, value=1, key="t_mid")
            tr = st.text_input("Translator name")
            txt = st.text_area("Translation")
            if st.button("Submit (pending)"):
                run("editor", "INSERT INTO Translations (mantra_id, translator_name, text, status) VALUES (%s,%s,%s,'pending')",
                    [mid, tr, txt])
                st.success("Added as pending")
            st.dataframe(query("editor", "SELECT * FROM v_editor_mantras LIMIT 50"))
        with tab2:
            mid = st.number_input("Mantra ID", min_value=1, value=1, key="e_mid")
            new = st.text_area("New Sanskrit text")
            if st.button("Save edit (transaction)"):
                con = connect("editor")
                try:
                    cur = con.cursor()
                    con.start_transaction()
                    cur.execute("SELECT sanskrit_text FROM Mantras WHERE mantra_id=%s FOR UPDATE", [mid])
                    cur.fetchall()
                    cur.execute("""INSERT INTO Mantra_History (mantra_id, old_sanskrit_text, old_iast_text, changed_by)
                                   SELECT mantra_id, sanskrit_text, iast_text, %s FROM Mantras WHERE mantra_id=%s""",
                                [f"editor{user_id}", mid])
                    cur.execute("UPDATE Mantras SET sanskrit_text=%s WHERE mantra_id=%s", [new, mid])
                    con.commit()
                    st.success("Updated, old text saved in history")
                except Exception as e:
                    con.rollback()
                    st.error(e)
                finally:
                    con.close()
        with tab3:
            st.caption("Open this app in two browser tabs. Start edit in tab 1, then in tab 2: the second waits until Commit.")
            mid = st.number_input("Mantra ID", min_value=1, value=1, key="l_mid")
            if st.button("Start edit (lock row)"):
                con = connect("editor")
                con.start_transaction()
                cur = con.cursor()
                cur.execute("SELECT * FROM Mantras WHERE mantra_id=%s FOR UPDATE", [mid])
                cur.fetchall()
                st.session_state["lock_con"] = con
                st.warning("Row locked. Other editors must wait.")
            if st.button("Commit (release lock)") and "lock_con" in st.session_state:
                st.session_state.pop("lock_con").commit()
                st.success("Released")

    # ---------------- ADMIN ----------------
    else:
        tab1, tab2 = st.tabs(["Approve translations", "Reports"])
        with tab1:
            pend = query("admin", "SELECT translation_id, mantra_id, translator_name, text FROM Translations WHERE status='pending'")
            st.dataframe(pend)
            tid = st.number_input("Translation ID to approve", min_value=1, value=1)
            if st.button("Approve"):
                run("admin", "UPDATE Translations SET status='approved' WHERE translation_id=%s", [tid])
                st.success("Approved")
        with tab2:
            name = st.selectbox("Report", list(REPORTS))
            st.dataframe(query("admin", REPORTS[name]))

except Exception as e:
    st.error(f"Database error: {e}")
