-- ============================================================
-- Vedas DBMS (CSBB 204) - 03_roles.sql
-- 4 real MySQL users, one per role. The app connects AS the
-- role user, so the database itself enforces every permission.
-- Run as root AFTER 02_views.sql (grants name the views):
--   mysql -u root -p < sql/03_roles.sql
-- Password for all four demo users: the DB_PASSWORD from .env
-- (stored hashed by MySQL as caching_sha2_password).
-- ============================================================
USE vedas_db;

-- ---------- recreate users cleanly ----------
DROP USER IF EXISTS 'student_u'@'localhost';
DROP USER IF EXISTS 'scholar_u'@'localhost';
DROP USER IF EXISTS 'editor_u'@'localhost';
DROP USER IF EXISTS 'admin_u'@'localhost';
DROP USER IF EXISTS 'student_u'@'%';
DROP USER IF EXISTS 'scholar_u'@'%';
DROP USER IF EXISTS 'editor_u'@'%';
DROP USER IF EXISTS 'admin_u'@'%';

CREATE USER 'student_u'@'localhost' IDENTIFIED BY 'changeme';
CREATE USER 'student_u'@'%'        IDENTIFIED BY 'changeme';
CREATE USER 'scholar_u'@'localhost' IDENTIFIED BY 'changeme';
CREATE USER 'scholar_u'@'%'         IDENTIFIED BY 'changeme';
CREATE USER 'editor_u'@'localhost'  IDENTIFIED BY 'changeme';
CREATE USER 'editor_u'@'%'          IDENTIFIED BY 'changeme';
CREATE USER 'admin_u'@'localhost'   IDENTIFIED BY 'changeme';
CREATE USER 'admin_u'@'%'           IDENTIFIED BY 'changeme';

-- ============================================================
-- STUDENT: read the catalogue through views, manage bookmarks.
-- ============================================================
GRANT SELECT ON vedas_db.v_student_mantras   TO 'student_u'@'localhost', 'student_u'@'%';
GRANT SELECT ON vedas_db.v_student_bookmarks TO 'student_u'@'localhost', 'student_u'@'%';
-- SELECT is included because DELETE/UPDATE ... WHERE needs read
-- access to the WHERE columns (otherwise MySQL error 1143).
GRANT SELECT, INSERT, DELETE ON vedas_db.Bookmarks TO 'student_u'@'localhost', 'student_u'@'%';

-- ============================================================
-- SCHOLAR: read the word view, add and fix word meanings.
-- ============================================================
GRANT SELECT ON vedas_db.v_scholar_words             TO 'scholar_u'@'localhost', 'scholar_u'@'%';
-- SELECT added so UPDATE ... WHERE can read the WHERE columns.
GRANT SELECT, INSERT, UPDATE ON vedas_db.Word_Meanings TO 'scholar_u'@'localhost', 'scholar_u'@'%';

-- ============================================================
-- EDITOR: add pending translations, edit Mantra text with history.
-- UPDATE on Translations is COLUMN-LEVEL: status is excluded,
-- so only admin can approve.
-- ============================================================
GRANT SELECT ON vedas_db.v_editor_mantras            TO 'editor_u'@'localhost', 'editor_u'@'%';
GRANT SELECT ON vedas_db.Mantras                     TO 'editor_u'@'localhost', 'editor_u'@'%';
GRANT SELECT ON vedas_db.Translations                TO 'editor_u'@'localhost', 'editor_u'@'%';
GRANT INSERT, UPDATE ON vedas_db.Mantras             TO 'editor_u'@'localhost', 'editor_u'@'%';
GRANT INSERT ON vedas_db.Translations                TO 'editor_u'@'localhost', 'editor_u'@'%';
GRANT UPDATE (mantra_id, translator_name, `text`) ON vedas_db.Translations
                                                     TO 'editor_u'@'localhost', 'editor_u'@'%';
GRANT INSERT ON vedas_db.Mantra_History              TO 'editor_u'@'localhost', 'editor_u'@'%';

-- ============================================================
-- ADMIN: everything, including DELETE and Translations.status.
-- ============================================================
GRANT ALL PRIVILEGES ON vedas_db.* TO 'admin_u'@'localhost', 'admin_u'@'%';

-- Show the effective grants (visible in the viva)
SHOW GRANTS FOR 'student_u'@'localhost';
SHOW GRANTS FOR 'scholar_u'@'localhost';
SHOW GRANTS FOR 'editor_u'@'localhost';
SHOW GRANTS FOR 'admin_u'@'localhost';
