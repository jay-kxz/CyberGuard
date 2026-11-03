"""Runs each Python module once so you can see real output (good for screenshots)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from ip_validator import validate_ip
from log_analyzer import analyze_log_file
from password_analyzer import analyze_password
from report_generator import generate_report


def show(title, data):
    print("\n=== %s ===" % title)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    pw = analyze_password("Zx9$kLm2#Qp7wR4!vN")          # a made-up sample, not a real password
    show("Password (sample)", {k: pw[k] for k in ("rating", "score", "length", "suggestions")})
    log = analyze_log_file(os.path.join(ROOT, "sample_data", "sample_logs", "sample.log"))
    show("Log analysis", {k: v for k, v in log.items() if k != "note"})
    for address in ("192.168.1.10", "8.8.8.8", "::1", "999.1.1.1"):
        show("IP " + address, validate_ip(address))
    out = generate_report("Log", {"file": "sample.log"}, log, "TXT", os.path.join(ROOT, "reports_output"))
    print("\nReport saved to:", out["saved_to"])
