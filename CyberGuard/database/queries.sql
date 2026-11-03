-- Example queries for the PL/SQL report. Run as cyberguard after install_all.sql.
SET DEFINE OFF
SET SERVEROUTPUT ON SIZE UNLIMITED
SET LINESIZE 150
SET PAGESIZE 40
COLUMN username FORMAT A14
COLUMN module_name FORMAT A15
COLUMN result_summary FORMAT A38
COLUMN status FORMAT A8
COLUMN details FORMAT A55
COLUMN table_name FORMAT A22

PROMPT === 1. JOIN: analyses with the user who ran them ===
SELECT h.analysis_id, u.username, h.module_name, h.status, h.result_summary
  FROM analysis_history h
  JOIN users u ON u.user_id = h.user_id
 ORDER BY h.analysis_id DESC;

PROMPT === 2. GROUP BY and ORDER BY: runs per module ===
SELECT module_name, COUNT(*) AS runs
  FROM analysis_history
 GROUP BY module_name
 ORDER BY runs DESC, module_name;

PROMPT === 3. HAVING: users with at least 2 analyses ===
SELECT u.username, COUNT(*) AS analyses
  FROM users u
  JOIN analysis_history h ON h.user_id = u.user_id
 GROUP BY u.username
HAVING COUNT(*) >= 2
 ORDER BY analyses DESC;

PROMPT === 4. Aggregates: file checks and matches ===
SELECT COUNT(*) AS file_checks,
       SUM(CASE WHEN verification_status = 'MATCH' THEN 1 ELSE 0 END) AS matches
  FROM file_integrity_records;

PROMPT === 5. The three functions (NULL = all users) ===
SELECT get_total_analyses(NULL) AS analyses,
       get_average_assessment_score(NULL) AS average_score,
       get_total_file_verifications(NULL) AS file_checks
  FROM dual;

PROMPT === 6. Cursor-based summary (generate_user_summary) ===
DECLARE
  v_text VARCHAR2(4000);
BEGIN
  generate_user_summary('demo_student', v_text);
  DBMS_OUTPUT.PUT_LINE(v_text);
END;
/

PROMPT === 7. UPDATE through a procedure, then the triggers (audit log and updated_at) ===
DECLARE
  v_id NUMBER;
BEGIN
  SELECT MIN(assessment_id) INTO v_id FROM security_assessments WHERE assessment_result = 'BELOW BASELINE';
  update_assessment_result(v_id, 'PASS', 55);
END;
/
SELECT assessment_id, assessment_result, assessment_score, updated_at FROM security_assessments ORDER BY assessment_id;
SELECT table_name, operation, record_id, details FROM audit_log ORDER BY audit_id DESC FETCH FIRST 3 ROWS ONLY;
ROLLBACK;
PROMPT (Rolled back: the demonstration data is unchanged.)

PROMPT === 8. Transaction with SAVEPOINT, ROLLBACK and COMMIT ===
INSERT INTO users (username) VALUES ('demo_temp');
SAVEPOINT after_insert;
DELETE FROM users WHERE username = 'demo_temp';
SELECT COUNT(*) AS temp_users_after_delete FROM users WHERE username = 'demo_temp';
ROLLBACK TO after_insert;
SELECT COUNT(*) AS temp_users_after_rollback FROM users WHERE username = 'demo_temp';
COMMIT;
DELETE FROM users WHERE username = 'demo_temp';
COMMIT;

PROMPT === 9. Exceptions: custom error, DUP_VAL_ON_INDEX, NO_DATA_FOUND ===
DECLARE
  v_id   NUMBER;
  v_text VARCHAR2(4000);
BEGIN
  BEGIN
    insert_analysis_record('demo_student', 'Score', 'x', 'MAYBE', v_id);
  EXCEPTION
    WHEN OTHERS THEN
      DBMS_OUTPUT.PUT_LINE('Custom error caught: ' || SQLERRM);
  END;
  BEGIN
    INSERT INTO users (username) VALUES ('demo_student');
  EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
      DBMS_OUTPUT.PUT_LINE('DUP_VAL_ON_INDEX caught: that username already exists.');
  END;
  generate_user_summary('nobody', v_text);
  DBMS_OUTPUT.PUT_LINE(v_text);
END;
/

PROMPT === 10. Function that returns a cursor ===
VARIABLE rc REFCURSOR
EXEC :rc := get_recent_history(3)
PRINT rc
