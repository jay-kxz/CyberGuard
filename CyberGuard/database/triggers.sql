-- CyberGuard triggers (run as cyberguard, after schema.sql).
-- The audit trigger writes into AUDIT_LOG, which has no trigger of its own, so nothing loops.

CREATE OR REPLACE TRIGGER trg_users_audit
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
DECLARE
  v_op      VARCHAR2(10);
  v_id      NUMBER;
  v_details VARCHAR2(400);
BEGIN
  IF INSERTING THEN
    v_op := 'INSERT'; v_id := :NEW.user_id; v_details := 'username=' || :NEW.username;
  ELSIF UPDATING THEN
    v_op := 'UPDATE'; v_id := :NEW.user_id; v_details := :OLD.username || ' -> ' || :NEW.username;
  ELSE
    v_op := 'DELETE'; v_id := :OLD.user_id; v_details := 'username=' || :OLD.username;
  END IF;
  INSERT INTO audit_log (table_name, operation, record_id, details)
  VALUES ('USERS', v_op, v_id, v_details);
END trg_users_audit;
/
SHOW ERRORS

CREATE OR REPLACE TRIGGER trg_assessments_audit
AFTER UPDATE OR DELETE ON security_assessments
FOR EACH ROW
BEGIN
  IF UPDATING THEN
    INSERT INTO audit_log (table_name, operation, record_id, details)
    VALUES ('SECURITY_ASSESSMENTS', 'UPDATE', :OLD.assessment_id,
            'result ' || :OLD.assessment_result || ' -> ' || :NEW.assessment_result ||
            ', score ' || :OLD.assessment_score || ' -> ' || :NEW.assessment_score);
  ELSE
    INSERT INTO audit_log (table_name, operation, record_id, details)
    VALUES ('SECURITY_ASSESSMENTS', 'DELETE', :OLD.assessment_id,
            'result ' || :OLD.assessment_result || ', score ' || :OLD.assessment_score);
  END IF;
END trg_assessments_audit;
/
SHOW ERRORS

-- Keeps UPDATED_AT correct without the application having to remember it.
CREATE OR REPLACE TRIGGER trg_assessments_timestamp
BEFORE UPDATE ON security_assessments
FOR EACH ROW
BEGIN
  :NEW.updated_at := SYSTIMESTAMP;
END trg_assessments_timestamp;
/
SHOW ERRORS

CREATE OR REPLACE TRIGGER trg_files_audit
AFTER DELETE ON file_integrity_records
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, operation, record_id, details)
  VALUES ('FILE_INTEGRITY_RECORDS', 'DELETE', :OLD.file_id, 'file=' || :OLD.file_name);
END trg_files_audit;
/
SHOW ERRORS
