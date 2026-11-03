import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "python"))

from ip_validator import validate_ip


class IPTests(unittest.TestCase):
    def check(self, text, version, label):
        r = validate_ip(text)
        self.assertTrue(r["valid"], text)
        self.assertEqual(r["version"], version)
        self.assertTrue(r["classification"].startswith(label), r["classification"])
        return r

    def test_kinds_of_address(self):
        self.check("192.168.1.10", 4, "Private")
        self.check("10.0.0.1", 4, "Private")
        self.check("8.8.8.8", 4, "Public")
        self.check("127.0.0.1", 4, "Loopback")
        self.check("169.254.10.1", 4, "Link-local")
        self.check("224.0.0.1", 4, "Multicast")
        self.check("0.0.0.0", 4, "Unspecified")

    def test_ipv6(self):
        self.check("::1", 6, "Loopback")
        self.check("fe80::1", 6, "Link-local")
        r = self.check("2001:4860:4860::8888", 6, "Public")
        self.assertIn("exploded", r)

    def test_flags(self):
        r = validate_ip("127.0.0.1")
        self.assertTrue(r["is_loopback"] and not r["is_multicast"])

    def test_spaces_are_trimmed(self):
        self.assertEqual(validate_ip("  8.8.8.8  ")["address"], "8.8.8.8")

    def test_invalid_input_is_graceful(self):
        for bad in ("999.1.1.1", "abc", "", "   ", None, 42, "1.2.3", "x" * 200):
            r = validate_ip(bad)
            self.assertFalse(r["valid"], bad)
            self.assertIn("error", r)


if __name__ == "__main__":
    unittest.main()
