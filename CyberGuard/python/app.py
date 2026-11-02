"""CyberGuard Python service (Flask). Listens on 127.0.0.1 only; the C++ server calls it.

Every reply is {"ok": true, "data": ...} or {"ok": false, "error": "..."}.
Request bodies (which may hold a sample password or a log) are never logged.
"""
import os
import sys

from flask import Flask, jsonify, request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

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


@app.errorhandler(ValueError)
def bad_input(error):
    return fail(str(error), 400)


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
    return ok({"status": "up", "service": "python"})


@app.post("/api/password-strength")
def password_strength():
    return ok(analyze_password(json_body().get("password")))


@app.post("/api/log-analysis")
def log_analysis():
    body = json_body()
    name = body.get("filename", "")
    if name and not (isinstance(name, str) and name.lower().endswith((".log", ".txt"))):
        raise ValueError("Only .log and .txt files are accepted.")
    return ok(analyze_log_text(body.get("content")))


@app.post("/api/ip-validation")
def ip_validation():
    return ok(validate_ip(json_body().get("address")))


@app.post("/api/report")
def report():
    body = json_body()
    out = generate_report(body.get("analysis_type"), body.get("input_summary", {}),
                          body.get("results", {}), body.get("format", "TXT"), REPORT_DIR)
    out["saved_to"] = "reports_output/" + out["filename"]      # relative, no full path
    return ok(out)


if __name__ == "__main__":
    print("CyberGuard Python service on http://%s:%d  (Ctrl+C to stop)" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=False)
