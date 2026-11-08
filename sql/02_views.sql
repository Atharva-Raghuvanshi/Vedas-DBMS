-- ============================================================
-- Vedas DBMS (CSBB 204) - 02_views.sql
-- 5 views, one per role (the "external schema" level).
-- Views are created by root/admin, so they run with definer
-- privileges: role users only need SELECT on the view itself.
-- Run as root after 01_schema.sql (and 04_seed.sql):
--   mysql -u root -p < sql/02_views.sql
-- ============================================================
USE vedas_db;

-- ---------- Student: read-only catalogue, APPROVED translations only ----------
CREATE OR REPLACE VIEW v_student_mantras AS
SELECT m.mantra_id,
       v.veda_name,
       CONCAT('Kanda ', k.kanda_number)          AS kanda_name,
       s.sukta_number,
       m.mantra_number,
       r.rishi_name,
       d.deity_name,
       m.metre,
       m.sanskrit_text,
       m.iast_text,
       GROUP_CONCAT(DISTINCT th.theme_name ORDER BY th.theme_name SEPARATOR ', ') AS themes,
       GROUP_CONCAT(DISTINCT t.text SEPARATOR ' | ')                              AS translation
FROM Mantras m
JOIN Suktas s        ON s.sukta_id  = m.sukta_id
JOIN Kandas k        ON k.kanda_id  = s.kanda_id
JOIN Vedas v         ON v.veda_id   = k.veda_id
JOIN Rishis r        ON r.rishi_id  = m.rishi_id
JOIN Deities d       ON d.deity_id  = m.deity_id
LEFT JOIN Mantra_Themes mt ON mt.mantra_id = m.mantra_id
LEFT JOIN Themes th        ON th.theme_id  = mt.theme_id
LEFT JOIN Translations t   ON t.mantra_id  = m.mantra_id AND t.status = 'approved'
GROUP BY m.mantra_id, v.veda_name, k.kanda_number, s.sukta_number,
         m.mantra_number, r.rishi_name, d.deity_name, m.metre,
         m.sanskrit_text, m.iast_text;

-- ---------- Student: own bookmarks ----------
CREATE OR REPLACE VIEW v_student_bookmarks AS
SELECT b.user_id,
       b.mantra_id,
       m.sanskrit_text
FROM Bookmarks b
JOIN Mantras m ON m.mantra_id = b.mantra_id;

-- ---------- Scholar: word list with location ----------
CREATE OR REPLACE VIEW v_scholar_words AS
SELECT w.mantra_id,
       w.word_order,
       w.sanskrit_word,
       w.dhatu,
       w.english_meaning,
       v.veda_name,
       s.sukta_number,
       m.mantra_number
FROM Word_Meanings w
JOIN Mantras m ON m.mantra_id = w.mantra_id
JOIN Suktas s  ON s.sukta_id  = m.sukta_id
JOIN Kandas k  ON k.kanda_id  = s.kanda_id
JOIN Vedas v   ON v.veda_id   = k.veda_id;

-- ---------- Editor: mantras with pending/approved translation counts ----------
CREATE OR REPLACE VIEW v_editor_mantras AS
SELECT m.mantra_id,
       v.veda_name,
       s.sukta_number,
       m.mantra_number,
       r.rishi_name,
       d.deity_name,
       m.metre,
       m.sanskrit_text,
       m.iast_text,
       COALESCE(SUM(t.status = 'pending'), 0)   AS pending_translations,
       COALESCE(SUM(t.status = 'approved'), 0)  AS approved_translations
FROM Mantras m
JOIN Suktas s   ON s.sukta_id  = m.sukta_id
JOIN Kandas k   ON k.kanda_id  = s.kanda_id
JOIN Vedas v    ON v.veda_id   = k.veda_id
JOIN Rishis r   ON r.rishi_id  = m.rishi_id
JOIN Deities d  ON d.deity_id  = m.deity_id
LEFT JOIN Translations t ON t.mantra_id = m.mantra_id
GROUP BY m.mantra_id, v.veda_name, s.sukta_number, m.mantra_number,
         r.rishi_name, d.deity_name, m.metre, m.sanskrit_text, m.iast_text;

-- ---------- Admin: structure summary per Veda ----------
CREATE OR REPLACE VIEW v_admin_summary AS
SELECT v.veda_name,
       COUNT(DISTINCT k.kanda_id) AS kandas,
       COUNT(DISTINCT s.sukta_id) AS suktas,
       COUNT(m.mantra_id)         AS mantras
FROM Vedas v
LEFT JOIN Kandas k ON k.veda_id  = v.veda_id
LEFT JOIN Suktas s ON s.kanda_id = k.kanda_id
LEFT JOIN Mantras m ON m.sukta_id = s.sukta_id
GROUP BY v.veda_name;
