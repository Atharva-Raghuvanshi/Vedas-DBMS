-- Vedas DBMS: tracking queries (MySQL 8). Run as admin_u unless noted.
USE vedas_db;

-- 1. Mantras per Veda
SELECT v.veda_name, COUNT(m.mantra_id) AS mantras
FROM Vedas v
JOIN Kandas k ON k.veda_id = v.veda_id
JOIN Suktas s ON s.kanda_id = k.kanda_id
JOIN Mantras m ON m.sukta_id = s.sukta_id
GROUP BY v.veda_name ORDER BY mantras DESC;

-- 2. Structure summary: Kandas, Suktas, Mantras per Veda
SELECT v.veda_name,
       COUNT(DISTINCT k.kanda_id) AS kandas,
       COUNT(DISTINCT s.sukta_id) AS suktas,
       COUNT(m.mantra_id)         AS mantras
FROM Vedas v
LEFT JOIN Kandas k ON k.veda_id = v.veda_id
LEFT JOIN Suktas s ON s.kanda_id = k.kanda_id
LEFT JOIN Mantras m ON m.sukta_id = s.sukta_id
GROUP BY v.veda_name;

-- 3. Mantras per Rishi (most active first)
SELECT r.rishi_name, COUNT(m.mantra_id) AS mantras
FROM Rishis r JOIN Mantras m ON m.rishi_id = r.rishi_id
GROUP BY r.rishi_name ORDER BY mantras DESC;

-- 4. Rishis with more than 10 Mantras (HAVING)
SELECT r.rishi_name, COUNT(*) AS mantras
FROM Rishis r JOIN Mantras m ON m.rishi_id = r.rishi_id
GROUP BY r.rishi_name HAVING COUNT(*) > 10;

-- 5. Mantras per deity
SELECT d.deity_name, COUNT(m.mantra_id) AS mantras
FROM Deities d JOIN Mantras m ON m.deity_id = d.deity_id
GROUP BY d.deity_name ORDER BY mantras DESC;

-- 6. Which deities each Rishi addresses
SELECT r.rishi_name, d.deity_name, COUNT(*) AS mantras
FROM Mantras m
JOIN Rishis r ON r.rishi_id = m.rishi_id
JOIN Deities d ON d.deity_id = m.deity_id
GROUP BY r.rishi_name, d.deity_name ORDER BY r.rishi_name, mantras DESC;

-- 7. Which Vedas does a given Rishi appear in
SELECT DISTINCT v.veda_name
FROM Rishis r
JOIN Mantras m ON m.rishi_id = r.rishi_id
JOIN Suktas s ON s.sukta_id = m.sukta_id
JOIN Kandas k ON k.kanda_id = s.kanda_id
JOIN Vedas v ON v.veda_id = k.veda_id
WHERE r.rishi_name LIKE '%Vasistha%';

-- 8. Full details of one Mantra (location + Rishi + deity)
SELECT v.veda_name, k.kanda_number, s.sukta_number, m.mantra_number,
       r.rishi_name, d.deity_name, m.metre, m.sanskrit_text, m.iast_text
FROM Mantras m
JOIN Suktas s ON s.sukta_id = m.sukta_id
JOIN Kandas k ON k.kanda_id = s.kanda_id
JOIN Vedas v ON v.veda_id = k.veda_id
JOIN Rishis r ON r.rishi_id = m.rishi_id
JOIN Deities d ON d.deity_id = m.deity_id
WHERE m.mantra_id = 1;

-- 9. Search by Rishi, deity or Sanskrit word
SELECT m.mantra_id, r.rishi_name, d.deity_name, m.sanskrit_text
FROM Mantras m
JOIN Rishis r ON r.rishi_id = m.rishi_id
JOIN Deities d ON d.deity_id = m.deity_id
WHERE r.rishi_name LIKE '%Madhuchchhandas%'
   OR d.deity_name LIKE '%Agni%'
   OR m.sanskrit_text LIKE '%agni%';

-- 10. Mantras per metre
SELECT metre, COUNT(*) AS mantras FROM Mantras GROUP BY metre ORDER BY mantras DESC;

-- 11. Word meanings of one Mantra, in order
SELECT word_order, sanskrit_word, dhatu, english_meaning
FROM Word_Meanings WHERE mantra_id = 1 ORDER BY word_order;

-- 12. Translations per translator
SELECT translator_name, COUNT(*) AS translations
FROM Translations GROUP BY translator_name;

-- 13. Suktas with no translation yet (LEFT JOIN)
SELECT s.sukta_id, s.sukta_number
FROM Suktas s
JOIN Mantras m ON m.sukta_id = s.sukta_id
LEFT JOIN Translations t ON t.mantra_id = m.mantra_id
GROUP BY s.sukta_id, s.sukta_number
HAVING COUNT(t.translation_id) = 0;

-- 14. Pending translations waiting for admin
SELECT t.translation_id, t.mantra_id, t.translator_name, t.text
FROM Translations t WHERE t.status = 'pending';

-- 15. Rishis and deities with no Mantras (LEFT JOIN)
SELECT r.rishi_name FROM Rishis r LEFT JOIN Mantras m ON m.rishi_id = r.rishi_id WHERE m.mantra_id IS NULL;
SELECT d.deity_name FROM Deities d LEFT JOIN Mantras m ON m.deity_id = d.deity_id WHERE m.mantra_id IS NULL;

-- 16. Mantras by theme
SELECT th.theme_name, m.mantra_id, m.sanskrit_text
FROM Themes th
JOIN Mantra_Themes mt ON mt.theme_id = th.theme_id
JOIN Mantras m ON m.mantra_id = mt.mantra_id
WHERE th.theme_name = 'fire';

-- 17. A student's bookmarks
SELECT b.user_id, m.mantra_id, m.sanskrit_text
FROM Bookmarks b JOIN Mantras m ON m.mantra_id = b.mantra_id
WHERE b.user_id = 1;

-- 18. Edit history of a Mantra
SELECT history_id, old_sanskrit_text, changed_by, changed_at
FROM Mantra_History WHERE mantra_id = 1 ORDER BY changed_at DESC;

-- 19. Safe edit with history (concurrency): run in TWO sessions to demo locking
START TRANSACTION;
SELECT sanskrit_text, iast_text FROM Mantras WHERE mantra_id = 1 FOR UPDATE;
INSERT INTO Mantra_History (mantra_id, old_sanskrit_text, old_iast_text, changed_by)
  SELECT mantra_id, sanskrit_text, iast_text, 'editor1' FROM Mantras WHERE mantra_id = 1;
UPDATE Mantras SET sanskrit_text = 'new text' WHERE mantra_id = 1;
COMMIT;
