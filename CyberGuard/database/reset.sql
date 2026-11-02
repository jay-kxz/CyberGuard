-- Deletes EVERY CyberGuard table, procedure and function in this account, so install_all.sql can run again.
BEGIN
  FOR o IN (SELECT object_name, object_type FROM user_objects
             WHERE object_type IN ('TABLE', 'PROCEDURE', 'FUNCTION')) LOOP
    IF o.object_type = 'TABLE' THEN
      EXECUTE IMMEDIATE 'DROP TABLE "' || o.object_name || '" CASCADE CONSTRAINTS PURGE';
    ELSE
      EXECUTE IMMEDIATE 'DROP ' || o.object_type || ' "' || o.object_name || '"';
    END IF;
  END LOOP;
END;
/
PROMPT Everything was removed.
