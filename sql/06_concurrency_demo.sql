-- ============================================================
-- Vedas DBMS (CSBB 204) - 06_concurrency_demo.sql
-- Two-editor row-lock demo (SELECT ... FOR UPDATE).
--
-- How to run in the viva (two terminal windows):
--   Terminal A:  mysql -u editor_u -p vedas_db      (password: changeme)
--   Terminal B:  mysql -u editor_u -p vedas_db
-- Follow the SESSION A / SESSION B steps alternately.
-- The Streamlit "Lock demo" page does the same thing with two
-- browser tabs, in case the CLI is not available.
-- ============================================================
USE vedas_db;

-- ================= SESSION A (first editor) =================
-- 1. A starts a transaction and locks mantra 1. Do NOT commit yet.
START TRANSACTION;
SELECT mantra_id, sanskrit_text FROM Mantras WHERE mantra_id = 1 FOR UPDATE;

-- 2. A edits the text. The row is still locked.
UPDATE Mantras SET sanskrit_text = 'अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम् (सम्पादित)।'
WHERE mantra_id = 1;

-- ================= SESSION B (second editor) =================
-- 3. B tries to lock the SAME row. It WAITS (blocks) here
--    until session A commits or rolls back. With the default
--    innodb_lock_wait_timeout = 50 it eventually fails with:
--    ERROR 1205: Lock wait timeout exceeded.
--    Run this while A is uncommitted and watch it hang:
-- START TRANSACTION;
-- SELECT mantra_id, sanskrit_text FROM Mantras WHERE mantra_id = 1 FOR UPDATE;

-- ================= SESSION A again =================
-- 4. A copies the old text into Mantra_History and commits.
--    This releases the lock and B unblocks immediately.
INSERT INTO Mantra_History (mantra_id, old_sanskrit_text, old_iast_text, changed_by)
  SELECT mantra_id, sanskrit_text, iast_text, 'editor1'
  FROM Mantras WHERE mantra_id = 1;
COMMIT;

-- ================= SESSION B again =================
-- 5. B's FOR UPDATE now returns at once and shows A's NEW text
--    (InnoDB READ COMMITTED / REPEATABLE READ: the locking read
--    always sees the latest committed version).
START TRANSACTION;
SELECT mantra_id, sanskrit_text FROM Mantras WHERE mantra_id = 1 FOR UPDATE;
COMMIT;

-- ================= proof =================
-- 6. The history row proves the edit-with-history transaction worked.
SELECT history_id, mantra_id, LEFT(old_sanskrit_text, 30) AS old_text,
       changed_by, changed_at
FROM Mantra_History WHERE mantra_id = 1 ORDER BY changed_at DESC;

-- Restore the original text after the demo (as admin):
-- UPDATE Mantras SET sanskrit_text =
-- 'अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम्। होतारं रत्नधातमम्॥' WHERE mantra_id = 1;
