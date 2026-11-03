-- DEMONSTRATION DATA. Users named demo_* are examples, not real activity.
-- Remove them any time with remove_sample_data.sql.
SET DEFINE OFF
SET SERVEROUTPUT ON
DECLARE
  v_id  NUMBER;
  v_ver VARCHAR2(30);
BEGIN
  insert_analysis_record('demo_student', 'Identifier', '7 digits, 3 letters, 4 other', 'SUCCESS', v_id);
  insert_analysis_record('demo_student', 'Score', 'sum 247, average 82.33', 'SUCCESS', v_id);
  insert_analysis_record('demo_student', 'Password', 'rating Very Strong, score 94', 'SUCCESS', v_id);
  insert_analysis_record('demo_student', 'Log', '22 entries, 7 failed logins', 'SUCCESS', v_id);
  insert_analysis_record('demo_student', 'IP address', '192.168.1.10 is private', 'SUCCESS', v_id);
  insert_analysis_record('demo_admin', 'Pointer', 'sum 4, absolute difference 10', 'SUCCESS', v_id);
  insert_analysis_record('demo_admin', 'IP address', 'invalid address', 'FAILED', v_id);

  insert_security_assessment('demo_student', 'Five-score assessment', 75, 'PASS', v_id);
  insert_security_assessment('demo_admin', 'Five-score assessment', 30, 'BELOW BASELINE', v_id);

  insert_file_integrity_record('demo_student', 'abc.txt', 3,
    'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
    'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', v_id, v_ver);
  insert_file_integrity_record('demo_student', 'empty.txt', 0,
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', v_id, v_ver);
  insert_file_integrity_record('demo_admin', 'notes.txt', 120,
    'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', NULL, v_id, v_ver);

  insert_report_record('demo_student', 'CG-DEMO-0001', 'Password', 'reports_output/CG-DEMO-0001.txt', v_id);
  COMMIT;
  DBMS_OUTPUT.PUT_LINE('Demonstration data loaded.');
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    DBMS_OUTPUT.PUT_LINE('Sample data was NOT loaded: ' || SQLERRM);
END;
/
