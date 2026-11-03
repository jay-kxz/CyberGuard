-- Run as cyberguard:  @"C:\path\to\CyberGuard\database\install_all.sql"
-- Builds the whole database in the right order.
SET DEFINE OFF
SET SQLBLANKLINES ON
SET SERVEROUTPUT ON SIZE UNLIMITED
SET LINESIZE 120
@@schema.sql
@@functions.sql
@@procedures.sql
@@triggers.sql
@@sample_data.sql
PROMPT
PROMPT ===== Objects created (expected: TABLE 7, FUNCTION 6, PROCEDURE 6, TRIGGER 4; all VALID) =====
SELECT object_type, COUNT(*) AS total, SUM(CASE WHEN status = 'VALID' THEN 1 ELSE 0 END) AS valid
  FROM user_objects
 WHERE object_type IN ('TABLE', 'FUNCTION', 'PROCEDURE', 'TRIGGER')
 GROUP BY object_type
 ORDER BY object_type;
PROMPT ===== Compile errors (expected: no rows selected) =====
SELECT name, type, line, text FROM user_errors ORDER BY name, sequence;
