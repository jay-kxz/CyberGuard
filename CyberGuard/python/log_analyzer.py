"""Module 7: Security Log Analyzer.

Reads a log (text or file) and counts levels, failed logins, busy IP addresses and
activity per hour. Only counts and IP addresses are returned, never the log lines.
Use synthetic demonstration logs.
"""
import ipaddress
import os
import re
from collections import Counter

MAX_BYTES = 5 * 1024 * 1024
MAX_LINES = 100000
REPEAT_THRESHOLD = 3            # this many failed logins from one IP is worth a look

LEVEL_RE = re.compile(r"\b(INFO|WARNING|WARN|ERROR)\b")
FAILED_RE = re.compile(r"failed login|failed password|authentication failure|invalid (?:user|password)", re.I)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
TIME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})[ T](\d{2}):\d{2}:\d{2}")


def _valid_ips(line):
    """Return the distinct real IPv4 addresses on a line (999.1.1.1 is ignored)."""
    found = []
    for candidate in set(IP_RE.findall(line)):
        try:
            ipaddress.IPv4Address(candidate)
            found.append(candidate)
        except ValueError:
            pass
    return found


def analyze_log_text(text):
    """Analyze log text. Raises ValueError for unusable input."""
    if not isinstance(text, str):
        raise ValueError("The log must be text.")
    if len(text.encode("utf-8", errors="replace")) > MAX_BYTES:
        raise ValueError("The log is larger than 5 MB.")
    lines = text.splitlines()
    if len(lines) > MAX_LINES:
        raise ValueError("The log has more than %d lines." % MAX_LINES)

    levels = Counter()
    ip_counts, failed_by_ip, by_hour = Counter(), Counter(), Counter()
    total = failed = 0

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        total += 1
        match = LEVEL_RE.search(line)
        level = ("WARNING" if match.group(1) == "WARN" else match.group(1)) if match else None
        levels[level or "OTHER"] += 1
        ips = _valid_ips(line)
        for ip in ips:
            ip_counts[ip] += 1
        if FAILED_RE.search(line):
            failed += 1
            for ip in ips:
                failed_by_ip[ip] += 1
        t = TIME_RE.match(line)
        if t:
            by_hour["%s %s:00" % (t.group(1), t.group(2))] += 1

    return {
        "total_entries": total,
        "info_count": levels["INFO"],
        "warning_count": levels["WARNING"],
        "error_count": levels["ERROR"],
        "unclassified_count": levels["OTHER"],
        "failed_login_count": failed,
        "top_ips": [{"ip": ip, "count": n} for ip, n in ip_counts.most_common(5)],
        "ips_with_repeated_failures": [{"ip": ip, "failed_logins": n}
                                       for ip, n in failed_by_ip.most_common() if n >= REPEAT_THRESHOLD],
        "activity_by_hour": dict(sorted(by_hour.items())),
        "note": "Counts come from simple text patterns. Treat them as a starting point, not a verdict.",
    }


def analyze_log_file(path):
    """Read a .log or .txt file from disk and analyze it (file handling)."""
    if not isinstance(path, str) or not path.lower().endswith((".log", ".txt")):
        raise ValueError("Only .log and .txt files are accepted.")
    try:
        if os.path.getsize(path) > MAX_BYTES:
            raise ValueError("The log file is larger than 5 MB.")
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return analyze_log_text(handle.read())
    except FileNotFoundError:
        raise ValueError("The log file was not found.")
    except PermissionError:
        raise ValueError("The log file cannot be opened.")
