import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "python"))

try:
    import flask  # noqa: F401
    HAVE_FLASK = True
except ImportError:
    HAVE_FLASK = False

import json
import tempfile

if HAVE_FLASK:
    import app as service


@unittest.skipUnless(HAVE_FLASK, "Flask is not installed (run setup_python.bat)")
class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        service.REPORT_DIR = self.tmp.name
        self.client = service.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def post(self, path, body):
        r = self.client.post(path, json=body)
        return r.status_code, r.get_json()

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual((r.status_code, r.get_json()["ok"]), (200, True))

    def test_password(self):
        status, j = self.post("/api/password-strength", {"password": "Zx9$kLm2#Qp7wR4!vN"})
        self.assertEqual((status, j["data"]["rating"]), (200, "Very Strong"))
        self.assertNotIn("Zx9$kLm2#Qp7wR4!vN", json.dumps(j))

    def test_password_errors(self):
        for body in ({}, {"password": ""}, {"password": 5}, {"password": "x" * 200}):
            status, j = self.post("/api/password-strength", body)
            self.assertEqual((status, j["ok"]), (400, False), body)

    def test_log(self):
        text = "2026-01-01 10:00:00 ERROR Failed login from 10.0.0.5\n"
        status, j = self.post("/api/log-analysis", {"filename": "a.log", "content": text})
        self.assertEqual((status, j["data"]["error_count"], j["data"]["failed_login_count"]), (200, 1, 1))

    def test_log_errors(self):
        self.assertEqual(self.post("/api/log-analysis", {"content": 5})[0], 400)
        self.assertEqual(self.post("/api/log-analysis", {"filename": "a.exe", "content": "x"})[0], 400)

    def test_ip(self):
        status, j = self.post("/api/ip-validation", {"address": "192.168.1.10"})
        self.assertTrue(j["data"]["valid"] and j["data"]["classification"].startswith("Private"))
        status, j = self.post("/api/ip-validation", {"address": "999.1.1.1"})
        self.assertEqual((status, j["data"]["valid"]), (200, False))

    def test_report(self):
        status, j = self.post("/api/report", {"analysis_type": "Password", "format": "TXT",
                                              "input_summary": {"length": 18},
                                              "results": {"rating": "Strong", "score": 80}})
        self.assertEqual(status, 200)
        self.assertTrue(j["data"]["saved_to"].startswith("reports_output/"))
        self.assertTrue(os.listdir(self.tmp.name))
        self.assertEqual(self.post("/api/report", {"analysis_type": "Weather"})[0], 400)
        self.assertEqual(self.post("/api/report", {"analysis_type": "Log", "format": "PDF"})[0], 400)

    def test_bad_requests(self):
        r = self.client.post("/api/ip-validation", data="not json", content_type="application/json")
        self.assertEqual((r.status_code, r.get_json()["ok"]), (400, False))
        self.assertEqual(self.client.get("/api/nothing").status_code, 404)
        self.assertEqual(self.client.get("/api/password-strength").status_code, 405)


if __name__ == "__main__":
    unittest.main()
