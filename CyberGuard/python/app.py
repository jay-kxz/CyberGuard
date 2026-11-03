"""CyberGuard Python service (Flask). Listens on 127.0.0.1 only; the C++ server calls it.

Every reply is {"ok": true, "data": ...} or {"ok": false, "error": "..."}.
Request bodies (which may hold a sample password or a log) are never logged.

This service owns three things:
    1. The password, log, IP and report modules (Modules 6-9)
    2. The connection to Oracle (Module 10, db.py) - the only place Oracle is used
    3. Best-effort saving: if the database is offline the analysis still works and
       the reply simply says "persisted": false. Nothing crashes.
"""
import os
import sys

from flask import Flask, jsonify, request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import db
from ip_validator import validate_ip
from log_analyzer import analyze_log_text
from password_analyzer import analyze_password
from report_generator import generate_report

HOST, PORT = "127.0.0.1", 5001
REPORT_DIR = os.path.join(os.path.dirname(HERE), "reports_output")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 7 * 1024 * 1024      # a 5 MB log plus JSON overhead


def ok(data):
    return jsonify({"ok": True, "data": data})


def fail(message, status=400):
    return jsonify({"ok": False, "error": message}), status


def json_body():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ValueError("The request body must be a JSON object.")
    return body


def remember(module_name, summary, status="SUCCESS"):
    """Save one analysis row if the database is reachable.

    Returns True when it was written and False when Oracle is offline. A save
    never fails the analysis itself - the tool already produced its result.
    """
    try:
        db.save_analysis(module_name, summary, status)
        return True
    except db.DatabaseOffline as error:
        app.logger.info("Not saved (%s): %s", module_name, error)
        return False


@app.errorhandler(ValueError)
def bad_input(error):
    return fail(str(error), 400)


@app.errorhandler(db.DatabaseOffline)
def database_offline(error):
    return fail("The database is not connected yet. " + str(error), 503)


@app.errorhandler(404)
def not_found(_):
    return fail("Unknown API address.", 404)


@app.errorhandler(405)
def wrong_method(_):
    return fail("That method is not allowed here.", 405)


@app.errorhandler(413)
def too_large(_):
    return fail("The request is too large.", 413)


@app.errorhandler(Exception)
def unexpected(_):
    return fail("Internal server error.", 500)      # details stay out of the reply


@app.get("/api/health")
def health():
    """Health of this service and of the database connection."""
    database = db.status()
    return ok({"status": "up", "service": "python",
               "database": database["available"],
               "database_detail": database["error"] or "connected"})


# ---------------------------------------------------------------------------
# Modules 6-9: the analyses. Each one is saved when the database is reachable.
# ---------------------------------------------------------------------------
@app.post("/api/password-strength")
def password_strength():
    result = analyze_password(json_body().get("password"))
    saved = remember("Password", "rating %s, score %s" % (result["rating"], result["score"]))
    result["persisted"] = saved
    return ok(result)


@app.post("/api/log-analysis")
def log_analysis():
    body = json_body()
    name = body.get("filename", "")
    if name and not (isinstance(name, str) and name.lower().endswith((".log", ".txt"))):
        raise ValueError("Only .log and .txt files are accepted.")
    result = analyze_log_text(body.get("content"))
    saved = remember("Log", "%s entries, %s errors, %s failed logins" % (
        result["total_entries"], result["error_count"], result["failed_login_count"]))
    result["persisted"] = saved
    return ok(result)


@app.post("/api/ip-validation")
def ip_validation():
    result = validate_ip(json_body().get("address"))
    summary = ("%s is %s" % (result["address"], result["classification"])
               if result.get("valid") else "invalid address")
    saved = remember("IP address", summary, "SUCCESS" if result.get("valid") else "FAILED")
    result["persisted"] = saved
    return ok(result)


@app.post("/api/report")
def report():
    body = json_body()
    out = generate_report(body.get("analysis_type"), body.get("input_summary", {}),
                          body.get("results", {}), body.get("format", "TXT"), REPORT_DIR)
    out["saved_to"] = "reports_output/" + out["filename"]      # relative, no full path
    try:
        db.save_report(out["report_id"], out["analysis_type"], out["saved_to"])
        out["persisted"] = True
    except db.DatabaseOffline as error:
        app.logger.info("Report not recorded in the database: %s", error)
        out["persisted"] = False
    return ok(out)


# ---------------------------------------------------------------------------
# Module 10: the database, used by the C++ server
# ---------------------------------------------------------------------------
@app.post("/api/record")
def record():
    """Save one analysis that the C++ modules performed.

    Body: {"module": "Score", "summary": "sum 247, average 82.33", "status": "SUCCESS"}
    """
    body = json_body()
    module = body.get("module")
    summary = body.get("summary", "")
    status = body.get("status", "SUCCESS")
    if not isinstance(module, str) or not isinstance(summary, str):
        raise ValueError("'module' and 'summary' must be text.")
    if not isinstance(status, str):
        raise ValueError("'status' must be text.")
    try:
        analysis_id = db.save_analysis(module, summary, status)
        return ok({"persisted": True, "analysis_id": analysis_id})
    except db.DatabaseOffline as error:
        app.logger.info("Analysis not saved: %s", error)
        return ok({"persisted": False, "analysis_id": None})


@app.post("/api/file-check")
def file_check():
    """Save one file integrity result. Body: {"filename", "size", "sha256", "reference"}"""
    body = json_body()
    name = body.get("filename", "")
    digest = body.get("sha256", "")
    reference = body.get("reference") or None
    if not isinstance(name, str) or not name:
        raise ValueError("'filename' must be text.")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("'sha256' must be 64 hexadecimal characters.")
    try:
        size = int(body.get("size", 0))
    except (TypeError, ValueError):
        raise ValueError("'size' must be a whole number.")
    if size < 0:
        raise ValueError("'size' must not be negative.")
    if reference is not None and (not isinstance(reference, str) or len(reference) != 64):
        raise ValueError("'reference' must be 64 hexadecimal characters.")
    try:
        stored = db.save_file_check(name, size, digest.lower(), reference.lower() if reference else None)
        return ok({"persisted": True, "file_id": stored["file_id"],
                   "verification": stored["verification"]})
    except db.DatabaseOffline as error:
        app.logger.info("File check not saved: %s", error)
        return ok({"persisted": False, "file_id": None, "verification": None})


@app.post("/api/assessment")
def assessment_record():
    """Save one assessment row (security_assessments) for a C++ assessment."""
    body = json_body()
    kind = body.get("type", "Five-score assessment")
    result = body.get("result", "")
    if not isinstance(kind, str) or not isinstance(result, str):
        raise ValueError("'type' and 'result' must be text.")
    try:
        score = float(body.get("score", 0))
    except (TypeError, ValueError):
        raise ValueError("'score' must be a number.")
    try:
        assessment_id = db.save_assessment(kind, score, result)
        return ok({"persisted": True, "assessment_id": assessment_id})
    except db.DatabaseOffline as error:
        app.logger.info("Assessment not saved: %s", error)
        return ok({"persisted": False, "assessment_id": None})


@app.get("/api/history")
def history():
    """Newest analyses first. Returns 503 when Oracle is not reachable."""
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        raise ValueError("'limit' must be a whole number.")
    return ok(db.recent_history(limit))


@app.get("/api/dashboard")
def dashboard():
    """The four numbers shown on the Overview page."""
    return ok(db.dashboard())


@app.get("/api/reports")
def reports():
    """Newest generated reports first."""
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        raise ValueError("'limit' must be a whole number.")
    return ok(db.recent_reports(limit))


if __name__ == "__main__":
    print("CyberGuard Python service on http://%s:%d  (Ctrl+C to stop)" % (HOST, PORT))
    if not db.status()["available"]:
        print("Database: not connected yet - analyses will still work, they just will not be saved.")
    app.run(host=HOST, port=PORT, debug=False)
