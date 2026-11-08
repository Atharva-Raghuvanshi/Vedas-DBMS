# Master prompt for Claude Code

You are building a college DBMS mini-project called "Vedas Database Management System" (course CSBB 204). Deadline is 2 days, so keep everything SIMPLE and working. Read `docs/PRD.md` first and follow it.

## Stack
MySQL 8 (InnoDB, utf8mb4), Python 3.11, Streamlit, mysql-connector-python, pandas. No other frameworks.

## Folder structure (create exactly this)
vedas-dbms/
  CLAUDE.md                 short project rules (copy the Rules section below)
  README.md                 setup and demo steps
  requirements.txt
  .env.example              DB_HOST, DB_NAME, DB_PASSWORD
  data/raw/                 downloaded dataset (git-ignored)
  data/processed/           parsed CSVs ready to load
  sql/
    01_schema.sql           database + 13 tables
    02_views.sql            5 views
    03_roles.sql            4 MySQL users + GRANT/REVOKE
    04_seed.sql             hand-made sample data (fallback)
    05_queries.sql          tracking and report queries (already written)
    06_concurrency_demo.sql two-session FOR UPDATE demo
  scripts/
    download_dataset.py     Hugging Face: siddharthjadhav6565/vedas
    load_data.py            parse + insert a SUBSET (200-500 mantras)
  app/
    app.py                  single-file Streamlit UI (already written)
  docs/
    PRD.md, er_diagram.png, screenshots/

## Database
Tables: Vedas, Kandas, Suktas, Rishis, Deities, Mantras, Translations, Word_Meanings, Themes, Mantra_Themes, Bookmarks, Mantra_History, App_Users.
Column names must match `sql/05_queries.sql` and `app/app.py`:
- Vedas(veda_id, veda_name), Kandas(kanda_id, veda_id, kanda_number), Suktas(sukta_id, kanda_id, sukta_number)
- Rishis(rishi_id, rishi_name), Deities(deity_id, deity_name), Themes(theme_id, theme_name)
- Mantras(mantra_id, sukta_id, rishi_id, deity_id, mantra_number, metre, sanskrit_text, iast_text), UNIQUE(sukta_id, mantra_number)
- Translations(translation_id, mantra_id, translator_name, text, status ENUM('pending','approved') DEFAULT 'pending')
- Word_Meanings(mantra_id, word_order, sanskrit_word, dhatu, english_meaning), UNIQUE(mantra_id, word_order)
- Mantra_Themes(mantra_id, theme_id), Bookmarks(user_id, mantra_id), App_Users(user_id, username, role)
- Mantra_History(history_id, mantra_id, old_sanskrit_text, old_iast_text, changed_by, changed_at)
Views: v_student_mantras (approved translations only; columns mantra_id, veda_name, kanda_name, sukta_number, mantra_number, rishi_name, deity_name, metre, sanskrit_text, iast_text, themes, translation), v_student_bookmarks (user_id, mantra_id, sanskrit_text), v_scholar_words (mantra_id, word_order, sanskrit_word, dhatu, english_meaning, veda_name, sukta_number, mantra_number), v_editor_mantras, v_admin_summary (veda_name, kandas, suktas, mantras).
Roles: student_u (SELECT on student views, INSERT/DELETE on Bookmarks), scholar_u (SELECT scholar view, INSERT/UPDATE Word_Meanings), editor_u (INSERT/UPDATE Translations and Mantras, INSERT Mantra_History), admin_u (ALL, only one who can UPDATE Translations.status and DELETE).

## Work in these phases. Stop after each and tell me what to run to verify.
1. Setup: folders, requirements.txt, .env.example, git init, .gitignore.
2. Schema: 01_schema.sql, run it, confirm tables exist.
3. Roles and views: 02_views.sql, 03_roles.sql. Test: student UPDATE must fail, editor approving a translation must fail.
4. Data: download_dataset.py, then inspect 50 rows and show me the pattern BEFORE writing the parser. Parse a subset only. If parsing is not working in 2 hours of effort, write 04_seed.sql with about 30 Mantras instead.
5. Queries: run every query in 05_queries.sql and fix column mismatches.
6. UI: run app/app.py, fix errors. Keep the UI minimal: sidebar role login, tabs, tables, buttons.
7. Concurrency: write 06_concurrency_demo.sql and verify the second session waits.
8. Docs: README with setup and a click-by-click viva demo script.

## Rules
- Simple over clever. No ORMs, no extra pages, no styling work.
- Every table ENGINE=InnoDB, CHARSET utf8mb4.
- Permissions are enforced by real MySQL users, not by Python if-statements.
- Never delete or rewrite files I wrote unless I ask. Ask before adding any new dependency.
- After each phase, give me the exact commands to test it.
