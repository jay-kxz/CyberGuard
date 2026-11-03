-- CyberGuard PL/SQL functions (run as cyberguard, after schema.sql).

-- Finds a user id. Returns NULL if the user does not exist.
CREATE OR REPLACE FUNCTION get_user_id (p_username IN VARCHAR2) RETURN NUMBER IS
  v_id users.user_id%TYPE;
BEGIN
  SELECT user_id INTO v_id FROM users WHERE username = p_username;
  RETURN v_id;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    RETURN NULL;
  WHEN TOO_MANY_ROWS THEN
    RAISE_APPLICATION_ERROR(-20010, 'More than one user is named ' || p_username || '.');
END get_user_id;
/
SHOW ERRORS

-- Finds a user, or creates the user when it is new.
CREATE OR REPLACE FUNCTION get_or_create_user (p_username IN VARCHAR2) RETURN NUMBER IS
  v_id NUMBER;
BEGIN
  v_id := get_user_id(p_username);
  IF v_id IS NULL THEN
    BEGIN
      INSERT INTO users (username) VALUES (p_username) RETURNING user_id INTO v_id;
    EXCEPTION
      WHEN DUP_VAL_ON_INDEX THEN          -- someone created it a moment ago
        v_id := get_user_id(p_username);
    END;
  END IF;
  RETURN v_id;
END get_or_create_user;
/
SHOW ERRORS

-- For the three functions below, a NULL user id means "all users".
CREATE OR REPLACE FUNCTION get_total_analyses (p_user_id IN NUMBER DEFAULT NULL) RETURN NUMBER IS
  v_total NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_total
    FROM analysis_history
   WHERE p_user_id IS NULL OR user_id = p_user_id;
  RETURN v_total;
END get_total_analyses;
/
SHOW ERRORS

CREATE OR REPLACE FUNCTION get_average_assessment_score (p_user_id IN NUMBER DEFAULT NULL) RETURN NUMBER IS
  v_average NUMBER;
BEGIN
  SELECT NVL(ROUND(AVG(assessment_score), 2), 0) INTO v_average
    FROM security_assessments
   WHERE p_user_id IS NULL OR user_id = p_user_id;
  RETURN v_average;
END get_average_assessment_score;
/
SHOW ERRORS

CREATE OR REPLACE FUNCTION get_total_file_verifications (p_user_id IN NUMBER DEFAULT NULL) RETURN NUMBER IS
  v_total NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_total
    FROM file_integrity_records
   WHERE p_user_id IS NULL OR user_id = p_user_id;
  RETURN v_total;
END get_total_file_verifications;
/
SHOW ERRORS

-- Returns the newest analyses as a cursor (the Python service reads it in Phase 8).
CREATE OR REPLACE FUNCTION get_recent_history (p_limit IN NUMBER DEFAULT 20) RETURN SYS_REFCURSOR IS
  v_cursor SYS_REFCURSOR;
BEGIN
  IF p_limit IS NULL OR p_limit < 1 OR p_limit > 200 THEN
    RAISE_APPLICATION_ERROR(-20011, 'The limit must be between 1 and 200.');
  END IF;
  OPEN v_cursor FOR
    SELECT h.analysis_id, u.username, h.module_name, h.analysis_timestamp, h.result_summary, h.status
      FROM analysis_history h
      JOIN users u ON u.user_id = h.user_id
     ORDER BY h.analysis_timestamp DESC, h.analysis_id DESC
     FETCH FIRST p_limit ROWS ONLY;
  RETURN v_cursor;
END get_recent_history;
/
SHOW ERRORS
