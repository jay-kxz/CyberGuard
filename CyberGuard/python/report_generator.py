"""Module 9: Security Report Generator (TXT and CSV).

A report holds: ID, analysis type, date and time, input summary, results,
observations, recommendations and a conclusion. Sensitive fields (passwords, raw
log text, file contents) are withheld, and files are only written inside the
folder you pass in, under a name this module creates.
"""
import csv
import io
import os
import uuid
from datetime import datetime

SUPPORTED_TYPES = ("Identifier", "Score", "Pointer", "Assessment", "File integrity", "Password", "Log", "IP address")
SUPPORTED_FORMATS = ("TXT", "CSV")
SENSITIVE_KEYS = {"password", "passwords", "content", "file_content", "raw", "text"}


def scrub(value):
    """Return a copy with sensitive fields withheld and very long text shortened."""
    if isinstance(value, dict):
        return {k: ("[withheld]" if str(k).lower() in SENSITIVE_KEYS else scrub(v)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [scrub(v) for v in value]
    if isinstance(value, str) and len(value) > 300:
        return value[:300] + "..."
    return value


def _flatten(data, prefix=""):
    """Turn nested dictionaries and lists into simple (name, text) pairs."""
    rows = []
    items = data.items() if isinstance(data, dict) else enumerate(data, 1)
    for key, value in items:
        name = "%s.%s" % (prefix, key) if prefix else str(key)
        if isinstance(value, dict) or (isinstance(value, list) and value and isinstance(value[0], dict)):
            rows += _flatten(value, name)
        elif isinstance(value, list):
            rows.append((name, ", ".join(map(str, value))))
        else:
            rows.append((name, str(value)))
    return rows


def _csv_safe(cell):
    """Stop spreadsheet programs from running a cell that starts like a formula."""
    cell = str(cell)
    return "'" + cell if cell[:1] in ("=", "+", "-", "@") else cell


def _notes(kind, r):
    """Observations and recommendations for each analysis type."""
    obs, rec = [], []
    if kind == "Password":
        obs.append("The heuristic rating is %s (score %s out of 100)." % (r.get("rating", "unknown"), r.get("score", "?")))
        obs += ["%s: %s." % (f["factor"], f["detail"]) for f in r.get("factors", []) if f.get("points", 0) < 0 or f["factor"] == "Common password"]
        rec = list(r.get("suggestions", []))
    elif kind == "Log":
        obs.append("%s entries were read: %s errors, %s warnings, %s failed logins." % (
            r.get("total_entries", 0), r.get("error_count", 0), r.get("warning_count", 0), r.get("failed_login_count", 0)))
        repeated = r.get("ips_with_repeated_failures", [])
        if repeated:
            obs.append("%d address(es) had repeated failed logins." % len(repeated))
            rec.append("Investigate the addresses with repeated failed logins.")
        if r.get("failed_login_count", 0):
            rec.append("Review the failed-login entries and check for guessing attempts.")
        rec.append("Keep logs protected and rotate them regularly.")
    elif kind == "IP address":
        if r.get("valid"):
            obs.append("The address is IPv%s and is classified as: %s." % (r.get("version"), r.get("classification")))
            if r.get("is_private"):
                rec.append("A private address is only meaningful inside a local network.")
        else:
            obs.append("The input was not a valid IP address.")
            rec.append("Check the address for typing mistakes.")
    elif kind == "File integrity":
        status = r.get("verification", "NO REFERENCE GIVEN")
        obs.append("Verification status: %s." % status)
        if status == "MISMATCH":
            rec.append("Do not trust this file. Download it again from the original source.")
        rec.append("A matching hash shows the file is identical to the reference. It does not prove who made it.")
    else:
        obs = ["%s: %s." % (k.replace("_", " "), v) for k, v in r.items() if not isinstance(v, (dict, list))][:6]
        rec.append("Compare these values with what you expected.")
    return obs, rec


class SecurityReport:
    """One report. Build it, then call to_txt(), to_csv() or save()."""

    def __init__(self, analysis_type, input_summary, results):
        match = [t for t in SUPPORTED_TYPES if t.lower() == str(analysis_type).strip().lower()]
        if not match:
            raise ValueError("Unknown analysis type. Use one of: " + ", ".join(SUPPORTED_TYPES) + ".")
        if not isinstance(input_summary, dict) or not isinstance(results, dict):
            raise ValueError("The input summary and the results must be dictionaries.")
        now = datetime.now()
        self.analysis_type = match[0]
        self.report_id = "CG-%s-%s" % (now.strftime("%Y%m%d-%H%M%S"), uuid.uuid4().hex[:6].upper())
        self.generated_at = now.strftime("%Y-%m-%d %H:%M:%S")
        self.input_summary = scrub(input_summary)
        self.results = scrub(results)
        self.observations, self.recommendations = _notes(self.analysis_type, self.results)
        self.conclusion = ("The %s analysis finished. This report comes from CyberGuard, an educational tool, "
                           "and is not a professional security assessment." % self.analysis_type)

    def to_txt(self):
        line = "=" * 60
        out = [line, "CYBERGUARD SECURITY REPORT", line, "Report ID   : " + self.report_id,
               "Analysis    : " + self.analysis_type, "Generated   : " + self.generated_at, "", "INPUT SUMMARY"]
        out += ["  %s: %s" % pair for pair in _flatten(self.input_summary)] or ["  (none)"]
        out += ["", "RESULTS"] + ["  %s: %s" % pair for pair in _flatten(self.results)]
        out += ["", "OBSERVATIONS"] + ["  %d. %s" % (i, o) for i, o in enumerate(self.observations, 1)]
        out += ["", "RECOMMENDATIONS"] + ["  %d. %s" % (i, r) for i, r in enumerate(self.recommendations, 1)]
        out += ["", "CONCLUSION", "  " + self.conclusion, line]
        return "\n".join(out) + "\n"

    def to_csv(self):
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\r\n")
        writer.writerow(["Section", "Field", "Value"])
        for field, value in (("Report ID", self.report_id), ("Analysis type", self.analysis_type),
                             ("Generated", self.generated_at)):
            writer.writerow(["Report", field, _csv_safe(value)])
        for name, value in _flatten(self.input_summary):
            writer.writerow(["Input", name, _csv_safe(value)])
        for name, value in _flatten(self.results):
            writer.writerow(["Result", name, _csv_safe(value)])
        for i, text in enumerate(self.observations, 1):
            writer.writerow(["Observation", i, _csv_safe(text)])
        for i, text in enumerate(self.recommendations, 1):
            writer.writerow(["Recommendation", i, _csv_safe(text)])
        writer.writerow(["Conclusion", "", _csv_safe(self.conclusion)])
        return buffer.getvalue()

    def save(self, fmt, out_dir):
        """Write the report into out_dir. The file name is made here, never taken from a user."""
        fmt = str(fmt).upper()
        if fmt not in SUPPORTED_FORMATS:
            raise ValueError("Format must be TXT or CSV.")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "%s.%s" % (self.report_id, fmt.lower()))
        content = self.to_txt() if fmt == "TXT" else self.to_csv()
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        return path


def generate_report(analysis_type, input_summary, results, fmt="TXT", out_dir=None):
    """Build a report and return its text. If out_dir is given, also save it there."""
    fmt = str(fmt).upper()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError("Format must be TXT or CSV.")
    report = SecurityReport(analysis_type, input_summary, results)
    saved = report.save(fmt, out_dir) if out_dir else None
    return {"report_id": report.report_id, "analysis_type": report.analysis_type, "format": fmt,
            "filename": "%s.%s" % (report.report_id, fmt.lower()),
            "content": report.to_txt() if fmt == "TXT" else report.to_csv(), "saved_to": saved}
