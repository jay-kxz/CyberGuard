-- CyberGuard schema (run as cyberguard). Tables, keys, constraints and indexes.
CREATE TABLE users (
  user_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  username    VARCHAR2(40) NOT NULL,
  created_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  CONSTRAINT uq_users_username UNIQUE (username),
  CONSTRAINT ck_users_username CHECK (REGEXP_LIKE(username, '^[A-Za-z0-9_.-]{1,40}$'))
);

CREATE TABLE analysis_history (
  analysis_id         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id             NUMBER NOT NULL,
  module_name         VARCHAR2(40) NOT NULL,
  analysis_timestamp  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  result_summary      VARCHAR2(500),
  status              VARCHAR2(10) DEFAULT 'SUCCESS' NOT NULL,
  CONSTRAINT fk_history_user FOREIGN KEY (user_id) REFERENCES users (user_id),
  CONSTRAINT ck_history_status CHECK (status IN ('SUCCESS', 'FAILED')),
  CONSTRAINT ck_history_module CHECK (module_name IN ('Identifier', 'Score', 'Pointer', 'Assessment',
                                                       'File integrity', 'Password', 'Log', 'IP address'))
);

CREATE TABLE file_integrity_records (
  file_id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id              NUMBER NOT NULL,
  file_name            VARCHAR2(200) NOT NULL,
  file_size            NUMBER(12) NOT NULL,
  sha256_hash          CHAR(64) NOT NULL,
  reference_hash       CHAR(64),
  verification_status  VARCHAR2(20) NOT NULL,
  created_at           TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  CONSTRAINT fk_files_user FOREIGN KEY (user_id) REFERENCES users (user_id),
  CONSTRAINT ck_files_size CHECK (file_size >= 0),
  CONSTRAINT ck_files_hash CHECK (REGEXP_LIKE(sha256_hash, '^[0-9a-f]{64}$')),
  CONSTRAINT ck_files_ref CHECK (reference_hash IS NULL OR REGEXP_LIKE(reference_hash, '^[0-9a-f]{64}$')),
  CONSTRAINT ck_files_status CHECK (verification_status IN ('MATCH', 'MISMATCH', 'NO REFERENCE GIVEN'))
);

CREATE TABLE security_assessments (
  assessment_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id            NUMBER NOT NULL,
  assessment_type    VARCHAR2(40) NOT NULL,
  assessment_score   NUMBER(5,2) NOT NULL,
  assessment_result  VARCHAR2(20) NOT NULL,
  created_at         TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  updated_at         TIMESTAMP,
  CONSTRAINT fk_assess_user FOREIGN KEY (user_id) REFERENCES users (user_id),
  CONSTRAINT ck_assess_score CHECK (assessment_score BETWEEN 0 AND 100),
  CONSTRAINT ck_assess_result CHECK (assessment_result IN ('PASS', 'BELOW BASELINE'))
);

CREATE TABLE activity_logs (
  log_id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id             NUMBER NOT NULL,
  activity_type       VARCHAR2(60) NOT NULL,
  activity_timestamp  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  activity_status     VARCHAR2(10) DEFAULT 'SUCCESS' NOT NULL,
  CONSTRAINT fk_activity_user FOREIGN KEY (user_id) REFERENCES users (user_id),
  CONSTRAINT ck_activity_status CHECK (activity_status IN ('SUCCESS', 'FAILED'))
);

CREATE TABLE reports (
  report_id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  report_code      VARCHAR2(40) NOT NULL,
  user_id          NUMBER NOT NULL,
  report_type      VARCHAR2(40) NOT NULL,
  generated_at     TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  report_location  VARCHAR2(200),
  CONSTRAINT uq_reports_code UNIQUE (report_code),
  CONSTRAINT fk_reports_user FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE audit_log (
  audit_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  table_name  VARCHAR2(30) NOT NULL,
  operation   VARCHAR2(10) NOT NULL,
  record_id   NUMBER,
  details     VARCHAR2(400),
  changed_by  VARCHAR2(60) DEFAULT USER NOT NULL,
  changed_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE INDEX idx_history_user_time ON analysis_history (user_id, analysis_timestamp);
CREATE INDEX idx_files_user ON file_integrity_records (user_id);
CREATE INDEX idx_assess_user ON security_assessments (user_id);
CREATE INDEX idx_activity_user ON activity_logs (user_id);
CREATE INDEX idx_reports_user ON reports (user_id);
