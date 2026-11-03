import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "python"))

from log_analyzer import analyze_log_file, analyze_log_text

SAMPLE = os.path.join(ROOT, "sample_data", "sample_logs", "sample.log")


class LogTests(unittest.TestCase):
    def test_sample_log_counts(self):
        r = analyze_log_file(SAMPLE)
        self.assertEqual(r["total_entries"], 22)
        self.assertEqual((r["info_count"], r["warning_count"], r["error_count"]), (10, 4, 7))
        self.assertEqual(r["unclassified_count"], 1)
        self.assertEqual(r["failed_login_count"], 7)

    def test_sample_log_ips_and_hours(self):
        r = analyze_log_file(SAMPLE)
        self.assertEqual(r["top_ips"][0], {"ip": "203.0.113.45", "count": 4})
        self.assertEqual(r["top_ips"][1], {"ip": "192.168.1.35", "count": 3})
        self.assertEqual(r["ips_with_repeated_failures"], [{"ip": "203.0.113.45", "failed_logins": 4}])
        self.assertEqual(r["activity_by_hour"]["2026-10-30 09:00"], 8)
        self.assertEqual(sum(r["activity_by_hour"].values()), 21)

    def test_empty_log(self):
        r = analyze_log_text("")
        self.assertEqual(r["total_entries"], 0)
        self.assertEqual(r["top_ips"], [])

    def test_impossible_ip_is_ignored_and_warn_counts_as_warning(self):
        r = analyze_log_text("2026-01-01 10:00:00 WARN bad ip 999.1.1.1\n")
        self.assertEqual(r["warning_count"], 1)
        self.assertEqual(r["top_ips"], [])

    def test_bad_input_raises(self):
        with self.assertRaises(ValueError):
            analyze_log_text(None)
        with self.assertRaises(ValueError):
            analyze_log_text("x" * (5 * 1024 * 1024 + 1))
        with self.assertRaises(ValueError):
            analyze_log_file("missing_file.log")
        with self.assertRaises(ValueError):
            analyze_log_file("notes.docx")

    def test_log_lines_are_not_returned(self):
        r = analyze_log_text("2026-01-01 10:00:00 ERROR secret-token-123 failed login\n")
        self.assertNotIn("secret-token-123", str(r))


if __name__ == "__main__":
    unittest.main()
