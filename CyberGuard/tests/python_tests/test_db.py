"""Tests for Module 10 (db.py) and for the endpoints that use it.

Oracle is not needed: the first half switches the connection off and checks that
everything degrades cleanly, the second half replaces the driver with a stand-in
so the PL/SQL call code is exercised without a real database. Tests that need a
live database are skipped unless CYBERGUARD_DB_TEST=1 is set.
"""
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "python"))

import db

try:
    import flask  # noqa: F401
    HAVE_FLASK = True
except ImportError:
    HAVE_FLASK = False

if HAVE_FLASK:
    import app as service


class OfflineTests(unittest.TestCase):
    """With CYBERGUARD_DB=off nothing connects and every save reports the problem."""

    def setUp(self):
        self._saved = dict(os.environ)
        os.environ["CYBERGUARD_DB"] = "off"
        db.reset()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._saved)
        db.reset()

    def test_status_is_honest(self):
        info = db.status()
        self.assertFalse(info["available"])
        self.assertFalse(info["enabled"])
        self.assertIn("switched off", info["error"])
        self.assertNotIn("password", info)                  # the password is never reported

    def test_saves_raise_database_offline(self):
        with self.assertRaises(db.DatabaseOffline):
            db.save_analysis("Score", "sum 247")
        with self.assertRaises(db.DatabaseOffline):
            db.save_file_check("abc.txt", 3, "ba7816bf" * 8)
        with self.assertRaises(db.DatabaseOffline):
            db.save_assessment("Five-score assessment", 75, "PASS")
        with self.assertRaises(db.DatabaseOffline):
            db.save_report("CG-TEST", "Score", "reports_output/CG-TEST.txt")
        with self.assertRaises(db.DatabaseOffline):
            db.recent_history(5)
        with self.assertRaises(db.DatabaseOffline):
            db.dashboard()
        with self.assertRaises(db.DatabaseOffline):
            db.recent_reports(5)

    def test_bad_arguments_are_rejected_before_connecting(self):
        with self.assertRaises(ValueError):
            db.save_analysis("Weather", "x")                # not one of the eight modules
        with self.assertRaises(ValueError):
            db.save_analysis("Score", "x", "MAYBE")         # ck_history_status allows two values
        with self.assertRaises(ValueError):
            db.save_assessment("type", 50, "UNKNOWN")       # ck_assess_result allows two values


@unittest.skipUnless(HAVE_FLASK, "Flask is not installed (run setup_python.bat)")
class OfflineApiTests(unittest.TestCase):
    """The API keeps working when the database is off; it just does not persist."""

    def setUp(self):
        self._saved = dict(os.environ)
        os.environ["CYBERGUARD_DB"] = "off"
        db.reset()
        self.client = service.app.test_client()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._saved)
        db.reset()

    def test_health_reports_the_database(self):
        body = self.client.get("/api/health").get_json()
        self.assertTrue(body["ok"])
        self.assertTrue(body["data"]["service"] == "python")
        self.assertFalse(body["data"]["database"])
        self.assertTrue(body["data"]["database_detail"])

    def test_analysis_still_answers_and_says_unsaved(self):
        r = self.client.post("/api/password-strength", json={"password": "Zx9$kLm2#Qp7wR4!vN"})
        body = r.get_json()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(body["data"]["rating"], "Very Strong")
        self.assertIs(body["data"]["persisted"], False)

    def test_record_and_file_check_say_unsaved(self):
        r = self.client.post("/api/record", json={"module": "Score", "summary": "sum 247"})
        self.assertEqual((r.status_code, r.get_json()["data"]["persisted"]), (200, False))
        digest = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        r = self.client.post("/api/file-check", json={"filename": "abc.txt", "size": 3, "sha256": digest})
        self.assertEqual((r.status_code, r.get_json()["data"]["persisted"]), (200, False))

    def test_record_rejects_unknown_module(self):
        self.assertEqual(self.client.post("/api/record", json={"module": "Weather", "summary": "x"}).status_code, 400)
        self.assertEqual(self.client.post("/api/record", json=["not", "an", "object"]).status_code, 400)

    def test_reads_report_503_with_a_clear_message(self):
        for path in ("/api/history", "/api/dashboard", "/api/reports"):
            r = self.client.get(path)
            body = r.get_json()
            self.assertEqual((r.status_code, body["ok"]), (503, False), path)
            self.assertIn("database is not connected yet", body["error"].lower())

    def test_file_check_validates_the_hash(self):
        r = self.client.post("/api/file-check", json={"filename": "a.txt", "size": 1, "sha256": "short"})
        self.assertEqual(r.status_code, 400)


class FakeCursor:
    """A stand-in cursor that records what the module asked Oracle to do."""

    def __init__(self):
        self.calls = []
        self.binds = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def var(self, kind, size=None):
        return FakeVar(len(self.binds))

    def callproc(self, name, params):
        self.calls.append((name, params))
        self.binds = params
        return params

    def execute(self, sql, params=None):
        self.calls.append((sql.split()[0].upper() if sql else "SQL", params))
        self.rows = []
        return self

    def fetchone(self):
        return (7, 3, 2, 1)

    def fetchall(self):
        return []


class FakeVar:
    def __init__(self, position):
        self.position = position

    def getvalue(self):
        return 42

    def setvalue(self, value):
        pass


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True


class FakePool:
    def __init__(self, connection):
        self._connection = connection

    def acquire(self):
        return self._connection


class WiredTests(unittest.TestCase):
    """The PL/SQL call code, with a stand-in driver standing in for Oracle.

    No database and no python-oracledb package are needed: db._driver and
    db._connect are replaced, and the cursor records what was asked of it.
    """

    def setUp(self):
        self._saved = dict(os.environ)
        os.environ["CYBERGUARD_DB"] = "on"
        os.environ["CYBERGUARD_DB_PASSWORD"] = "secret"
        db.reset()
        self.cursor = FakeCursor()
        self.connection = FakeConnection(self.cursor)
        self.pool = FakePool(self.connection)
        self.patch = mock.patch.object(db, "_connect", return_value=self.pool)
        self.patch.start()
        self.fake_driver = SimpleNamespace(NUMBER="NUMBER", STRING="STRING", CURSOR="CURSOR")
        self.driver_patch = mock.patch.object(db, "_driver", self.fake_driver)
        self.driver_patch.start()

    def tearDown(self):
        self.driver_patch.stop()
        self.patch.stop()
        os.environ.clear()
        os.environ.update(self._saved)
        db.reset()

    def test_analysis_calls_the_procedure_and_commits(self):
        db.save_analysis("Score", "sum 247")
        name, params = self.cursor.calls[0]
        self.assertEqual(name, "insert_analysis_record")
        self.assertEqual(params[1], "Score")                 # module name
        self.assertEqual(params[2], "sum 247")               # summary
        self.assertEqual(params[3], "SUCCESS")               # status
        self.assertTrue(self.connection.committed)           # the caller commits, not the procedure

    def test_file_check_calls_the_procedure(self):
        digest = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        db.save_file_check("abc.txt", 3, digest)
        name, params = self.cursor.calls[0]
        self.assertEqual(name, "insert_file_integrity_record")
        self.assertEqual(params[1], "abc.txt")
        self.assertEqual(params[2], 3)
        self.assertEqual(params[3], digest)

    def test_dashboard_reads_the_four_numbers(self):
        self.assertEqual(db.dashboard(), {"analyses": 7, "files": 3, "assessments": 2, "reports": 1})

    def test_summary_text_stays_inside_the_column(self):
        db.save_analysis("Log", "x" * 900)                   # result_summary is VARCHAR2(500)
        self.assertEqual(len(self.cursor.calls[0][1][2]), 500)

    def test_pool_is_built_from_the_configuration(self):
        seen = {}

        class Driver:
            POOL_GETMODE_WAIT = "WAIT"

            @staticmethod
            def create_pool(**kwargs):
                seen.update(kwargs)
                return "pool"

        config = {"user": "cyberguard", "password": "secret", "dsn": "localhost:1521/FREEPDB1",
                  "timeout": 4}
        self.assertEqual(db._create_pool(Driver, config), "pool")
        self.assertEqual(seen["user"], "cyberguard")
        self.assertEqual(seen["dsn"], "localhost:1521/FREEPDB1")
        self.assertEqual(seen["tcp_connect_timeout"], 4)     # a dead host must not hang the page
        self.assertEqual(seen["max"], 4)


class BackoffTests(unittest.TestCase):
    """A dead host is not re-tested on every single request."""

    def setUp(self):
        self._saved = dict(os.environ)
        os.environ["CYBERGUARD_DB"] = "on"
        os.environ["CYBERGUARD_DB_PASSWORD"] = "secret"
        db.reset()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._saved)
        db.reset()

    def test_one_failure_is_remembered(self):
        attempts = []

        def refuse(*args, **kwargs):
            attempts.append(1)
            raise RuntimeError("no listener")

        with mock.patch.object(db, "_driver", SimpleNamespace(POOL_GETMODE_WAIT="WAIT")), \
                mock.patch.object(db, "_create_pool", refuse):
            first = db.status()
            second = db.status()
        self.assertFalse(first["available"])
        self.assertIn("not reachable", second["error"])
        self.assertEqual(len(attempts), 1)                   # the second call used the memory


@unittest.skipUnless(os.environ.get("CYBERGUARD_DB_TEST") == "1",
                     "set CYBERGUARD_DB_TEST=1 with Oracle running to test a live connection")
class LiveOracleTests(unittest.TestCase):
    """Only runs against a real database that install_all.sql has been applied to."""

    def test_round_trip(self):
        self.assertTrue(db.is_available(), db.status()["error"])
        new_id = db.save_analysis("Score", "sum 247, average 82.33")
        self.assertGreater(new_id, 0)
        self.assertTrue(any(row["analysis_id"] == new_id for row in db.recent_history(20)))
        numbers = db.dashboard()
        self.assertGreaterEqual(numbers["analyses"], 1)


if __name__ == "__main__":
    unittest.main()
