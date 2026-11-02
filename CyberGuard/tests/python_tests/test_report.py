import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "python"))

import csv
import io
import tempfile
from report_generator import SecurityReport, generate_report, scrub


class ReportTests(unittest.TestCase):
    def test_txt_has_all_sections(self):
        text = SecurityReport("Log", {"file": "a.log"}, {"total_entries": 3, "error_count": 1}).to_txt()
        for part in ("Report ID", "Analysis", "Generated", "INPUT SUMMARY", "RESULTS",
                     "OBSERVATIONS", "RECOMMENDATIONS", "CONCLUSION"):
            self.assertIn(part, text)

    def test_type_is_case_insensitive_and_validated(self):
        self.assertEqual(SecurityReport("password", {}, {}).analysis_type, "Password")
        with self.assertRaises(ValueError):
            SecurityReport("Weather", {}, {})
        with self.assertRaises(ValueError):
            SecurityReport("Log", "not a dict", {})

    def test_sensitive_fields_are_withheld(self):
        r = SecurityReport("Password", {"password": "hunter2hunter2"}, {"rating": "Weak", "score": 40, "content": "RAWDATA"})
        out = r.to_txt() + r.to_csv()
        self.assertNotIn("hunter2hunter2", out)
        self.assertNotIn("RAWDATA", out)
        self.assertIn("[withheld]", out)

    def test_scrub_works_on_nested_data_and_long_text(self):
        data = scrub({"a": [{"password": "x"}], "b": "y" * 500})
        self.assertEqual(data["a"][0]["password"], "[withheld]")
        self.assertTrue(len(data["b"]) < 400)

    def test_csv_is_valid_and_formula_safe(self):
        text = SecurityReport("IP address", {"input": "=cmd|' /C calc'!A0"}, {"valid": False}).to_csv()
        rows = list(csv.reader(io.StringIO(text)))
        self.assertEqual(rows[0], ["Section", "Field", "Value"])
        self.assertTrue(any(r[2].startswith("'=") for r in rows))

    def test_save_and_format_rules(self):
        with tempfile.TemporaryDirectory() as folder:
            out = generate_report("Score", {"count": 3}, {"sum": 247}, "csv", folder)
            self.assertTrue(out["saved_to"].startswith(folder))
            self.assertTrue(out["saved_to"].endswith(".csv"))
            with open(out["saved_to"], encoding="utf-8") as handle:
                self.assertIn(out["report_id"], handle.read())
            with self.assertRaises(ValueError):
                generate_report("Score", {}, {}, "PDF", folder)

    def test_file_integrity_mismatch_advice(self):
        r = SecurityReport("File integrity", {}, {"verification": "MISMATCH"})
        self.assertTrue(any("Do not trust" in x for x in r.recommendations))


if __name__ == "__main__":
    unittest.main()
