-- Deletes all demonstration data (users whose names start with demo_) and their records.
DELETE FROM activity_logs WHERE user_id IN (SELECT user_id FROM users WHERE username LIKE 'demo\_%' ESCAPE '\');
DELETE FROM analysis_history WHERE user_id IN (SELECT user_id FROM users WHERE username LIKE 'demo\_%' ESCAPE '\');
DELETE FROM file_integrity_records WHERE user_id IN (SELECT user_id FROM users WHERE username LIKE 'demo\_%' ESCAPE '\');
DELETE FROM security_assessments WHERE user_id IN (SELECT user_id FROM users WHERE username LIKE 'demo\_%' ESCAPE '\');
DELETE FROM reports WHERE user_id IN (SELECT user_id FROM users WHERE username LIKE 'demo\_%' ESCAPE '\');
DELETE FROM users WHERE username LIKE 'demo\_%' ESCAPE '\';
COMMIT;
PROMPT Demonstration data removed.
