-- ============================================================
-- Vedas DBMS - 07_react_migration.sql
-- Add-ons for the React + Flask UI (run AFTER 01..03):
--   v_filter_options : dropdown/filter data for all roles
--   v_app_users      : minimal App_Users listing so login can
--                      resolve the user_id without touching the
--                      App_Users base table (students have no
--                      SELECT on it)
-- No existing table/view/role is changed - this file only adds.
-- Run as root:  mysql -u root -p < sql/07_react_migration.sql
-- ============================================================
USE vedas_db;

CREATE OR REPLACE VIEW v_filter_options AS
SELECT 'veda'   AS kind, veda_id AS item_id, veda_name AS label FROM Vedas
UNION ALL
SELECT 'kanda', kanda_id, CONCAT('Kanda ', kanda_number) FROM Kandas
UNION ALL
SELECT 'sukta', s.sukta_id,
       CONCAT(v.veda_name, ' ', k.kanda_number, '.', s.sukta_number)
FROM Suktas s
JOIN Kandas k ON k.kanda_id = s.kanda_id
JOIN Vedas v  ON v.veda_id  = k.veda_id
UNION ALL
SELECT 'rishi', rishi_id, rishi_name FROM Rishis
UNION ALL
SELECT 'deity', deity_id, deity_name FROM Deities
UNION ALL
SELECT 'theme', theme_id, theme_name FROM Themes
UNION ALL
SELECT 'metre', NULL, metre FROM Mantras WHERE metre IS NOT NULL
GROUP BY metre;

CREATE OR REPLACE VIEW v_app_users AS
SELECT user_id, username, role FROM App_Users;

-- read access for the three limited roles (admin already has ALL)
GRANT SELECT ON vedas_db.v_filter_options TO
  'student_u'@'localhost', 'student_u'@'%',
  'scholar_u'@'localhost', 'scholar_u'@'%',
  'editor_u'@'localhost',  'editor_u'@'%';
GRANT SELECT ON vedas_db.v_app_users TO
  'student_u'@'localhost', 'student_u'@'%',
  'scholar_u'@'localhost', 'scholar_u'@'%',
  'editor_u'@'localhost',  'editor_u'@'%';
