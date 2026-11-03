-- CyberGuard PL/SQL procedures (run as cyberguard, after functions.sql).
-- None of them COMMIT. The caller decides whether to COMMIT or ROLLBACK.

-- 1. Saves one analysis in the history and in the activity log.
CREATE OR REPLACE PROCEDURE insert_analysis_record (
  p_username        IN  VARCHAR2,
  p_module_name     IN  VARCHAR2,
  p_result_summary  IN  VARCHAR2,
  p_status          IN  VARCHAR2 DEFAULT 'SUCCESS',
  p_analysis_id     OUT NUMBER
) IS
  e_invalid_status EXCEPTION;               -- a custom exception
  v_user_id NUMBER;
BEGIN
  IF p_status IS NULL OR p_status NOT IN ('SUCCESS', 'FAILED') THEN
    RAISE e_invalid_status;
  END IF;
  v_user_id := get_or_create_user(p_username);
  INSERT INTO analysis_history (user_id, module_name, result_summary, status)
  VALUES (v_user_id, p_module_name, SUBSTR(p_result_summary, 1, 500), p_status)
  RETURNING analysis_id INTO p_analysis_id;
  INSERT INTO activity_logs (user_id, activity_type, activity_status)
  VALUES (v_user_id, 'Analysis: ' || p_module_name, p_status);
EXCEPTION
  WHEN e_invalid_status THEN
    RAISE_APPLICATION_ERROR(-20001, 'The status must be SUCCESS or FAILED.');
  WHEN OTHERS THEN
    RAISE;                                   -- pass any other error to the caller
END insert_analysis_record;
/
SHOW ERRORS

-- 2. Changes the result (and optionally the score) of an assessment.
CREATE OR REPLACE PROCEDURE update_assessment_result (
  p_assessment_id  IN NUMBER,
  p_new_result     IN VARCHAR2,
  p_new_score      IN NUMBER DEFAULT NULL
) IS
  e_not_found EXCEPTION;
BEGIN
  UPDATE security_assessments
     SET assessment_result = p_new_result,
         assessment_score  = NVL(p_new_score, assessment_score)
   WHERE assessment_id = p_assessment_id;
  IF SQL%ROWCOUNT = 0 THEN
    RAISE e_not_found;
  END IF;
EXCEPTION
  WHEN e_not_found THEN
    RAISE_APPLICATION_ERROR(-20002, 'There is no assessment with id ' || p_assessment_id || '.');
  WHEN OTHERS THEN
    RAISE;
END update_assessment_result;
/
SHOW ERRORS

-- 3. Saves a file check. The status (MATCH, MISMATCH, NO REFERENCE GIVEN) is worked out here.
CREATE OR REPLACE PROCEDURE insert_file_integrity_record (
  p_username      IN  VARCHAR2,
  p_file_name     IN  VARCHAR2,
  p_file_size     IN  NUMBER,
  p_sha256        IN  VARCHAR2,
  p_reference     IN  VARCHAR2 DEFAULT NULL,
  p_file_id       OUT NUMBER,
  p_verification  OUT VARCHAR2
) IS
  e_bad_hash EXCEPTION;
  v_user_id NUMBER;
  v_hash    VARCHAR2(64) := LOWER(p_sha256);
  v_ref     VARCHAR2(64) := LOWER(p_reference);
BEGIN
  IF v_hash IS NULL OR LENGTH(v_hash) <> 64 THEN
    RAISE e_bad_hash;
  END IF;
  IF v_ref IS NULL THEN
    p_verification := 'NO REFERENCE GIVEN';
  ELSIF v_ref = v_hash THEN
    p_verification := 'MATCH';
  ELSE
    p_verification := 'MISMATCH';
  END IF;
  v_user_id := get_or_create_user(p_username);
  INSERT INTO file_integrity_records
         (user_id, file_name, file_size, sha256_hash, reference_hash, verification_status)
  VALUES (v_user_id, SUBSTR(p_file_name, 1, 200), p_file_size, v_hash, v_ref, p_verification)
  RETURNING file_id INTO p_file_id;
EXCEPTION
  WHEN e_bad_hash THEN
    RAISE_APPLICATION_ERROR(-20004, 'A SHA-256 hash has exactly 64 characters.');
  WHEN OTHERS THEN
    RAISE;
END insert_file_integrity_record;
/
SHOW ERRORS

-- 4. Builds a text summary of one user. It uses an explicit parameterized cursor.
CREATE OR REPLACE PROCEDURE generate_user_summary (
  p_username  IN  VARCHAR2,
  p_summary   OUT VARCHAR2
) IS
  v_user_id NUMBER;
  v_line    VARCHAR2(200);
  CURSOR c_modules (cp_user_id NUMBER) IS
    SELECT module_name, COUNT(*) AS runs
      FROM analysis_history
     WHERE user_id = cp_user_id
     GROUP BY module_name
     ORDER BY runs DESC, module_name;
BEGIN
  SELECT user_id INTO v_user_id FROM users WHERE username = p_username;
  p_summary := 'User ' || p_username || ': '
            || get_total_analyses(v_user_id) || ' analyses, '
            || get_total_file_verifications(v_user_id) || ' file checks, average assessment score '
            || TO_CHAR(get_average_assessment_score(v_user_id), 'FM990.00') || '.';
  FOR r IN c_modules(v_user_id) LOOP
    v_line := ' ' || r.module_name || ' x' || r.runs || ';';
    IF LENGTH(p_summary) + LENGTH(v_line) <= 3900 THEN
      p_summary := p_summary || v_line;
    END IF;
  END LOOP;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    p_summary := 'There is no user named ' || p_username || '.';
END generate_user_summary;
/
SHOW ERRORS

-- Extra procedures the application needs (not in the syllabus list).
CREATE OR REPLACE PROCEDURE insert_security_assessment (
  p_username         IN  VARCHAR2,
  p_assessment_type  IN  VARCHAR2,
  p_score            IN  NUMBER,
  p_result           IN  VARCHAR2,
  p_assessment_id    OUT NUMBER
) IS
  v_user_id NUMBER;
BEGIN
  v_user_id := get_or_create_user(p_username);
  INSERT INTO security_assessments (user_id, assessment_type, assessment_score, assessment_result)
  VALUES (v_user_id, p_assessment_type, p_score, p_result)
  RETURNING assessment_id INTO p_assessment_id;
END insert_security_assessment;
/
SHOW ERRORS

CREATE OR REPLACE PROCEDURE insert_report_record (
  p_username     IN  VARCHAR2,
  p_report_code  IN  VARCHAR2,
  p_report_type  IN  VARCHAR2,
  p_location     IN  VARCHAR2,
  p_report_id    OUT NUMBER
) IS
  v_user_id NUMBER;
BEGIN
  v_user_id := get_or_create_user(p_username);
  INSERT INTO reports (report_code, user_id, report_type, report_location)
  VALUES (p_report_code, v_user_id, p_report_type, p_location)
  RETURNING report_id INTO p_report_id;
EXCEPTION
  WHEN DUP_VAL_ON_INDEX THEN
    RAISE_APPLICATION_ERROR(-20003, 'A report with the code ' || p_report_code || ' already exists.');
END insert_report_record;
/
SHOW ERRORS
