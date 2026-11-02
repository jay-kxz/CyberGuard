-- Run ONCE as SYS, connected to the CDB service FREE:
--   sqlplus sys@localhost:1521/FREE as sysdba
--   @"C:\path\to\CyberGuard\database\00_create_user.sql"
-- It creates the application user "cyberguard" inside the pluggable database FREEPDB1.
-- The password is typed when asked. It is never written in any file.
SET DEFINE ON
ALTER SESSION SET CONTAINER = FREEPDB1;
ACCEPT cg_pass CHAR PROMPT 'Choose a password for the cyberguard database user: ' HIDE
CREATE USER cyberguard IDENTIFIED BY "&cg_pass";
GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE, CREATE PROCEDURE, CREATE TRIGGER, CREATE VIEW TO cyberguard;
GRANT UNLIMITED TABLESPACE TO cyberguard;
PROMPT
PROMPT User cyberguard is ready. Now type EXIT, then log in as cyberguard (see the instructions).
