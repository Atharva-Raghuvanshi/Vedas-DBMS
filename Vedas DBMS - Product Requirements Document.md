# Vedas DBMS - Product Requirements Document

CSBB 204 DBMS Mini-Project. Build window: 2 days. Stack: MySQL 8 + Python + Streamlit.

## 1. Goal

Build a working database for a Vedic research library that shows the five DBMS features promised in the synopsis: **security (GRANT/REVOKE and roles), concurrency control (transactions and row locks), views (external schema), SQL queries, and a clear three-level schema**. The UI exists only to demonstrate these, so it must be as simple as possible.

**Success means that in the viva you can live-demo:** (1) a student who can only read, (2) an editor adding a pending translation, (3) the admin approving it, (4) two editors colliding on one Mantra and the second one waiting, (5) the reports.

## 2. Scope

**In scope:** the 13 tables, 4 roles, 5 views, search, translation approval, bookmarks, edit history, 5 reports, and a loaded dataset of a few hundred Mantras.

**Out of scope (do not build):** user registration, password reset, fancy styling, pagination, Sanskrit font polish, importing all 59,342 rows perfectly, mobile layout.

## 3. Users and permissions

| Role | Can do | MySQL privileges |
| --- | --- | --- |
| Student | Search and read approved content, manage own bookmarks | SELECT on student views only; INSERT and DELETE on Bookmarks |
| Scholar | Add and edit word meanings | SELECT on scholar view; INSERT and UPDATE on Word\_Meanings |
| Editor | Add translations as pending, edit Mantra text | INSERT and UPDATE on Translations and Mantras; INSERT on Mantra\_History |
| Admin | Everything, approve translations, delete, reports | ALL; the only role with DELETE and with UPDATE of Translations.status |

Implementation note: create one real MySQL user per role (student\_u, scholar\_u, editor\_u, admin\_u). The app logs in by opening a connection **with that MySQL user**, so permissions are enforced by the database and not by Python code. This is the strongest demo point.

## 4. Database design

**Tables:** Vedas, Kandas, Suktas, Rishis, Deities, Mantras, Translations, Word\_Meanings, Themes, Mantra\_Themes, Bookmarks, Mantra\_History, App\_Users.

- Mantras: mantra\_id PK, sukta\_id FK, rishi\_id FK, deity\_id FK, mantra\_number, metre, sanskrit\_text, iast\_text. UNIQUE(sukta\_id, mantra\_number).
- Translations: translation\_id PK, mantra\_id FK, translator\_name, text, status ENUM('pending','approved') DEFAULT 'pending'.
- Word\_Meanings: mantra\_id FK, word\_order, sanskrit\_word, dhatu, english\_meaning. UNIQUE(mantra\_id, word\_order).
- Mantra\_Themes: composite PK (mantra\_id, theme\_id).
- Bookmarks: composite PK (user\_id, mantra\_id).
- Mantra\_History: history\_id PK, mantra\_id FK, old\_sanskrit\_text, old\_iast\_text, changed\_by, changed\_at.
- App\_Users: user\_id, username, role. Used only to identify who owns a bookmark.

Use InnoDB for all tables (required for row locks) and foreign keys with ON DELETE RESTRICT.

**Views (one per role):**

- v\_student\_mantras: Veda, Kanda, Sukta, Rishi, deity, metre, texts, themes, and approved translations only.
- v\_student\_bookmarks: the logged-in student's bookmarks.
- v\_scholar\_words: words with position, dhatu, meaning, plus Veda, Sukta and Mantra number.
- v\_editor\_mantras: Mantras with pending and approved translations.
- v\_admin\_summary: count of Kandas, Suktas and Mantras per Veda.

## 5. Functional requirements

| ID | Requirement | Role | Priority |
| --- | --- | --- | --- |
| F1 | Login by choosing role and username (connects as that MySQL user) | All | Must |
| F2 | Search Mantras by Veda, Rishi, deity, metre, or Sanskrit word (LIKE) | Student | Must |
| F3 | Bookmark and un-bookmark a Mantra, list own bookmarks | Student | Must |
| F4 | Add translation (status = pending) | Editor | Must |
| F5 | Edit Mantra text in a transaction: SELECT ... FOR UPDATE, copy old text to Mantra\_History, UPDATE, COMMIT | Editor | Must |
| F6 | Approve pending translation | Admin | Must |
| F7 | Add word meanings with order and dhatu | Scholar | Must |
| F8 | Five reports (listed below) | Admin | Must |
| F9 | Add and delete Vedas, Kandas, Suktas, Mantras | Admin | Should |
| F10 | Tag Mantras with themes and search by theme | Editor, Student | Should |
| F11 | Permission-denied demo: show the raw MySQL error when a student tries an UPDATE | Student | Should |

**Reports:** Mantras per Veda, Mantras per Rishi, Mantras per deity, translations per translator, Suktas with no translation (LEFT JOIN). Use GROUP BY and HAVING in at least one.

## 6. Concurrency demo (the important one)

Open two editor sessions. Session A begins a transaction and runs SELECT ... FOR UPDATE on one Mantra and does not commit. Session B tries the same and waits. After A commits, B continues and sees A's new text.

Keep a small Lock Demo page with a Start edit button (acquires the lock) and a Commit button (releases it) so you can show this with two browser tabs without typing SQL. Also keep the same commands in a concurrency\_demo.sql file as a backup for the viva.

## 7. Simplest UI (Streamlit)

Use **Streamlit** in a single app.py file. No HTML, CSS or JavaScript. Every screen is a title, a few inputs, and a table.

- **Sidebar:** a role dropdown and a Login button. After login, the sidebar shows only the pages for that role.
- **Student:** Search page (4 text boxes and a results table), My Bookmarks page.
- **Scholar:** one page with a Mantra ID box, an editable word table, and a Save button.
- **Editor:** Add Translation form, Edit Mantra form, Lock Demo page.
- **Admin:** Pending Translations list with an Approve button per row, a Reports page (dropdown of 5 reports that shows the table), a Manage Data page.

Do not make it prettier than this. Spend the time on the SQL.

## 8. Data plan

The Hugging Face dataset is raw text, so full parsing is the biggest risk. Timebox it.

1. Download the dataset and look at 50 rows to see the pattern (headings, verse numbers, translation lines).
2. Write a Python script that parses a **subset**: roughly 2 Vedas, 3 to 5 Kandas, about 20 Suktas, 200 to 500 Mantras. Anything that fails to parse is skipped.
3. If parsing is not working within 2 hours, **stop and use seed data** (about 30 Mantras plus 10 Rishis and deities, 15 translations, 40 word meanings). The project is graded on database features, not data volume.
4. In the report, say that the 59,342-row dataset is the source and the loaded set is a cleaned sample.

## 9. Phases and timeline (2 days)

| Phase | Work | Time | Done when |
| --- | --- | --- | --- |
| 0. Setup | Install MySQL and Streamlit, create DB, git repo, split work | 1 hr | SELECT 1 works from Python |
| 1. Schema | All CREATE TABLE statements with keys and UNIQUE constraints | 2 hrs | Tables exist, FK inserts work |
| 2. Data | Parser or seed script, load sample | 3 hrs | 200+ Mantras (or 30 seeded) in DB |
| 3. Security | Four roles, GRANT/REVOKE, five views, test each role in the MySQL CLI | 2 hrs | Student UPDATE fails, editor approve fails |
| 4. Transactions | Edit-with-history procedure, FOR UPDATE test in two terminals | 2 hrs | Second session waits, history row saved |
| 5. Queries | Search queries and five report queries | 2 hrs | All return correct output |
| 6. UI | Streamlit pages in order: login, student search, editor, admin approve, reports, scholar, lock demo | 4 hrs | Full demo path runs |
| 7. Test and polish | Run the demo end to end, fix bugs, take screenshots | 2 hrs | Rehearsed twice |
| 8. Docs | Final report, SQL files, README, ER diagram screenshot | 2 hrs | Submission folder ready |

**Suggested split for 3 people:**

- **Person 1 (Database):** phases 1, 3, 4. Schema, roles, views, locking.
- **Person 2 (Data and queries):** phases 2, 5. Loading script, search and report SQL.
- **Person 3 (App and docs):** phases 6, 8. Streamlit and the report.

Everyone joins for phase 7. Person 3 can start the UI with dummy tables on day 1 while the others finish the schema.

**Cut order if time runs out:** F10 themes, then F9 manage data, then F11 denied screen. Never cut F4, F5, F6 or the views.

## 10. Deliverables

- schema.sql (tables, views, roles, grants)
- load\_data.py and seed.sql
- queries.sql (search and reports) and concurrency\_demo.sql
- app.py (Streamlit)
- ER diagram image and screenshots
- Final report and a one-page viva demo script listing the click order

## 11. Risks

| Risk | Mitigation |
| --- | --- |
| Dataset parsing eats the schedule | Hard 2-hour limit, then use seed data |
| Role permissions work in SQL but fail in the app | Test every role from the MySQL CLI first |
| Wrong engine breaks locking | Declare ENGINE=InnoDB on every table |
| Sanskrit text shows as boxes | Use utf8mb4 for the database and the connection |
| Demo breaks in the viva | Keep the SQL scripts as a fallback and rehearse |

## 12. Acceptance checklist

- Student can SELECT from views and cannot UPDATE or DELETE anything
- Editor translation is saved as pending and is invisible to students
- Admin approves it and it appears for students
- Two editors on the same Mantra: second one waits, then sees the new text
- Mantra\_History has the old text after an edit
- Duplicate (sukta\_id, mantra\_number) is rejected
- All five reports run
- Passwords are stored hashed by MySQL
