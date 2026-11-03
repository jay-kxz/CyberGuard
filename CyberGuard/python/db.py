"""Module 10: Database connectivity (Oracle Database Free, thin driver).

WHY THIS FILE EXISTS
The browser never talks to Oracle. The C++ server never talks to Oracle either.
This module is the single place where a connection is opened, so the connection
string, the password and the PL/SQL calls have exactly one home.

WHY THE PL/SQL IS CALLED INSTEAD OF WRITING INSERTS HERE
database/install_all.sql creates the procedures and functions the application
uses (insert_analysis_record, insert_file_integrity_record, get_recent_history,
get_total_analyses, ...). Calling them keeps the validation rules - valid status
values, the 64-character hash rule, the report-code uniqueness check - inside the
database, where they cannot be bypassed. The application and the coursework
database therefore agree by construction.

CONFIGURATION
Environment variables, optionally supplied by a .env file in the project folder:

    CYBERGUARD_DB            on | off              (default: on)
    CYBERGUARD_DB_USER       cyberguard            (created by 00_create_user.sql)
    CYBERGUARD_DB_PASSWORD   -                    (required; never written in code)
    CYBERGUARD_DB_DSN        localhost:1521/FREEPDB1
    CYBERGUARD_DB_APP_USER   web_user             (recorded in users.username)
    CYBERGUARD_DB_TIMEOUT    connect timeout in seconds, thin mode (default: 3)

WHAT HAPPENS WHEN ORACLE IS NOT RUNNING
Nothing crashes. status() reports the reason, and every save/read function raises
DatabaseOffline. The API turns that into "persisted": false, so the web page keeps
working and the Overview panel says the numbers are not connected yet.
Use it like this:

    try:
        db.save_analysis("Password", "rating Very Strong, score 94")
        saved = True
    except db.DatabaseOffline:
        saved = False
"""
import os
import threading
import time
from datetime import date, datetime

# The analysis names the database accepts (see ck_history_module in schema.sql).
MODULES = ("Identifier", "Score", "Pointer", "Assessment",
           "File integrity", "Password", "Log", "IP address")

DEFAULT_DSN = "localhost:1521/FREEPDB1"
DEFAULT_APP_USER = "web_user"
DEFAULT_TIMEOUT = 2            # seconds per connection attempt
ERROR_BACKOFF = 5.0           # after a failure, answer instantly for this long
ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

_lock = threading.Lock()       # the Flask dev server can answer on several threads
_pool = None
_last_error = None
_driver = None                 # the imported python-oracledb module, once it is needed
_retry_after = 0.0             # monotonic time before which no new attempt is made


class DatabaseOffline(Exception):
    """Raised when Oracle is switched off, not installed or not reachable."""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
def _load_env_file(path=ENV_FILE):
    """Read KEY=VALUE lines into os.environ. Existing variables win.

    A tiny substitute for python-dotenv, so the service works with no extra
    package. Real values are never printed or returned by this module.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except (FileNotFoundError, PermissionError, OSError):
        pass


def settings():
    """Return the current configuration (the password is never included)."""
    _load_env_file()
    try:
        timeout = max(1, int(os.environ.get("CYBERGUARD_DB_TIMEOUT", DEFAULT_TIMEOUT)))
    except ValueError:
        timeout = DEFAULT_TIMEOUT
    return {
        "enabled": os.environ.get("CYBERGUARD_DB", "on").strip().lower() not in ("off", "0", "false", "no"),
        "user": os.environ.get("CYBERGUARD_DB_USER", "cyberguard"),
        "password": os.environ.get("CYBERGUARD_DB_PASSWORD", ""),
        "dsn": os.environ.get("CYBERGUARD_DB_DSN", DEFAULT_DSN),
        "app_user": os.environ.get("CYBERGUARD_DB_APP_USER", DEFAULT_APP_USER),
        "timeout": timeout,
    }


def reset():
    """Close the pool so the next call re-reads the configuration (used by tests)."""
    global _pool, _last_error, _retry_after
    with _lock:
        if _pool is not None:
            try:
                _pool.close(force=True)
            except Exception:
                pass
        _pool = None
        _last_error = None
        _retry_after = 0.0


def driver():
    """Return the python-oracledb module, importing it the first time it is needed.

    Importing it here (and not at the top of the file) means the Flask service
    still starts - and every other tool still works - when the package has not
    been installed yet.
    """
    global _driver
    if _driver is None:
        try:
            import oracledb
        except ImportError:
            raise DatabaseOffline(
                "The python-oracledb package is not installed (run setup_python.bat).")
        _driver = oracledb
    return _driver


# ---------------------------------------------------------------------------
# Connection pool
# ---------------------------------------------------------------------------
def _connect():
    """Return the shared connection pool, creating it on first use."""
    global _pool, _last_error, _retry_after
    config = settings()
    if not config["enabled"]:
        raise DatabaseOffline("The database is switched off (CYBERGUARD_DB=off).")
    if not config["password"]:
        raise DatabaseOffline(
            "No database password is configured. Copy .env.example to .env and set "
            "CYBERGUARD_DB_PASSWORD.")
    with _lock:
        if _pool is not None:
            return _pool
        # A refused or unplugged host costs a few seconds to discover. The page asks
        # for the connection on every load, so a recent failure is remembered and
        # reported instantly instead of being re-tested each time.
        if time.monotonic() < _retry_after:
            raise DatabaseOffline("Oracle is not reachable (%s)." % (_last_error or "connection failed"))
        oracledb = driver()                      # raises DatabaseOffline if it is not installed
        try:
            _pool = _create_pool(oracledb, config)
            _last_error = None
        except Exception as error:               # bad password, no listener, unknown service...
            _last_error = "%s: %s" % (type(error).__name__, error)
            _retry_after = time.monotonic() + ERROR_BACKOFF
            raise DatabaseOffline("Oracle is not reachable (%s)." % _last_error)
        # Creating a pool does not prove a usable connection, so check one now.
        try:
            with _pool.acquire() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM dual")
                    cursor.fetchone()
        except Exception as error:
            try:
                _pool.close(force=True)
            except Exception:
                pass
            _pool = None
            _last_error = "%s: %s" % (type(error).__name__, error)
            _retry_after = time.monotonic() + ERROR_BACKOFF
            raise DatabaseOffline("Oracle is not reachable (%s)." % _last_error)
        _retry_after = 0.0
        return _pool


def _create_pool(oracledb, config):
    """Create the pool. tcp_connect_timeout stops a dead host from hanging a request."""
    settings_kwargs = {"user": config["user"], "password": config["password"], "dsn": config["dsn"],
                       "min": 1, "max": 4, "increment": 1, "getmode": oracledb.POOL_GETMODE_WAIT}
    try:
        return oracledb.create_pool(tcp_connect_timeout=config["timeout"], **settings_kwargs)
    except TypeError:
        # Very old driver versions do not know the timeout keyword; connect anyway.
        return oracledb.create_pool(**settings_kwargs)


def status():
    """Describe the connection without raising. Used by /api/health and the page."""
    config = settings()
    info = {"enabled": config["enabled"], "user": config["user"], "dsn": config["dsn"],
            "app_user": config["app_user"], "available": False, "error": None}
    try:
        _connect()                     # creating the pool also proves one live connection
        info["available"] = True
    except DatabaseOffline as error:
        info["error"] = str(error)
    except Exception as error:
        info["error"] = "%s: %s" % (type(error).__name__, error)
    return info


def is_available():
    return status()["available"]


def _run(callback):
    """Run callback(cursor) in one committed transaction, inside its own connection."""
    pool = _connect()
    try:
        with pool.acquire() as connection:
            with connection.cursor() as cursor:
                result = callback(cursor)
            connection.commit()                  # the PL/SQL never commits; the caller decides
            return result
    except DatabaseOffline:
        raise
    except Exception as error:
        raise DatabaseOffline("The database call failed (%s: %s)." % (type(error).__name__, error))


def _check_module(module_name):
    """Reject a module name the database would refuse anyway (ck_history_module)."""
    match = [m for m in MODULES if m.lower() == str(module_name).strip().lower()]
    if not match:
        raise ValueError("Unknown analysis type. Use one of: " + ", ".join(MODULES) + ".")
    return match[0]


def _text(value, limit=40):
    """Keep summary text inside the column widths declared in schema.sql."""
    return str(value)[:limit]


def _scalar(row, index=0, default=0):
    value = row[index] if row else default
    return default if value is None else value


# ---------------------------------------------------------------------------
# Writes - each one calls a PL/SQL procedure
# ---------------------------------------------------------------------------
def save_analysis(module_name, summary, status="SUCCESS", username=None):
    """Record one analysis with insert_analysis_record(). Returns the new analysis id."""
    module_name = _check_module(module_name)
    if str(status).upper() not in ("SUCCESS", "FAILED"):
        raise ValueError("The status must be SUCCESS or FAILED.")
    who = _text(username or settings()["app_user"])

    def work(cursor):
        oracledb = driver()
        new_id = cursor.var(oracledb.NUMBER)
        cursor.callproc("insert_analysis_record",
                        [who, module_name, _text(summary, 500), str(status).upper(), new_id])
        return int(new_id.getvalue() or 0)

    return _run(work)


def save_file_check(file_name, file_size, sha256_hash, reference_hash=None, username=None):
    """Record a file check with insert_file_integrity_record().

    The procedure decides the verification status, so the answer stored in the
    database and the answer shown on the page come from the same rule.
    Returns {"file_id": int, "verification": "MATCH" | "MISMATCH" | "NO REFERENCE GIVEN"}.
    """
    who = _text(username or settings()["app_user"])

    def work(cursor):
        oracledb = driver()
        new_id = cursor.var(oracledb.NUMBER)
        verification = cursor.var(oracledb.STRING, 20)
        cursor.callproc("insert_file_integrity_record",
                        [who, _text(file_name, 200), int(file_size), sha256_hash,
                         reference_hash or None, new_id, verification])
        return {"file_id": int(new_id.getvalue() or 0), "verification": verification.getvalue()}

    return _run(work)


def save_assessment(assessment_type, score, result, username=None):
    """Record one assessment with insert_security_assessment()."""
    who = _text(username or settings()["app_user"])
    if str(result).upper() not in ("PASS", "BELOW BASELINE"):
        raise ValueError("The result must be PASS or BELOW BASELINE.")
    score = max(0.0, min(100.0, float(score)))

    def work(cursor):
        oracledb = driver()
        new_id = cursor.var(oracledb.NUMBER)
        cursor.callproc("insert_security_assessment",
                        [who, _text(assessment_type), score, str(result).upper(), new_id])
        return int(new_id.getvalue() or 0)

    return _run(work)


def save_report(report_code, report_type, location, username=None):
    """Record a generated report with insert_report_record()."""
    who = _text(username or settings()["app_user"])

    def work(cursor):
        oracledb = driver()
        new_id = cursor.var(oracledb.NUMBER)
        cursor.callproc("insert_report_record",
                        [who, _text(report_code), _text(report_type), _text(location, 200), new_id])
        return int(new_id.getvalue() or 0)

    return _run(work)


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------
def recent_history(limit=20):
    """Newest analyses first, read through the get_recent_history() cursor function."""
    limit = max(1, min(200, int(limit)))     # the function itself allows 1..200

    def work(cursor):
        oracledb = driver()
        ref_cursor = cursor.var(oracledb.CURSOR)
        cursor.execute("BEGIN :1 := get_recent_history(:2); END;", [ref_cursor, limit])
        rows = ref_cursor.getvalue()
        return [{"analysis_id": r[0], "username": r[1], "module_name": r[2],
                 "analysis_timestamp": _as_text(r[3]), "result_summary": r[4], "status": r[5]}
                for r in rows]

    return _run(work)


def dashboard():
    """The four numbers on the Overview page, using the functions from functions.sql."""
    def work(cursor):
        cursor.execute(
            "SELECT get_total_analyses(NULL), get_total_file_verifications(NULL), "
            "       (SELECT COUNT(*) FROM security_assessments), "
            "       (SELECT COUNT(*) FROM reports) "
            "  FROM dual")
        row = cursor.fetchone() or (0, 0, 0, 0)
        return {"analyses": int(_scalar(row, 0)), "files": int(_scalar(row, 1)),
                "assessments": int(_scalar(row, 2)), "reports": int(_scalar(row, 3))}

    return _run(work)


def recent_reports(limit=20):
    """Newest reports first (the reports table has no cursor function)."""
    limit = max(1, min(200, int(limit)))

    def work(cursor):
        cursor.execute(
            "SELECT report_code, report_type, generated_at, report_location FROM reports "
            " ORDER BY generated_at DESC, report_id DESC FETCH FIRST :1 ROWS ONLY", [limit])
        return [{"report_code": r[0], "report_type": r[1], "generated_at": _as_text(r[2]),
                 "report_location": r[3]} for r in cursor.fetchall()]

    return _run(work)


def _as_text(value):
    """Turn Oracle DATE/TIMESTAMP values into readable text (JSON has no dates)."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return value
