import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "python"))

import json
from password_analyzer import analyze_password


class PasswordTests(unittest.TestCase):
    def test_common_password_is_capped(self):
        r = analyze_password("password")
        self.assertEqual(r["rating"], "Very Weak")
        self.assertLessEqual(r["score"], 10)
        self.assertTrue(any(f["factor"] == "Common password" for f in r["factors"]))

    def test_short_password_is_very_weak(self):
        self.assertEqual(analyze_password("abc")["rating"], "Very Weak")

    def test_repeated_characters_are_penalised(self):
        r = analyze_password("aaaaaaaa")
        self.assertEqual(r["rating"], "Very Weak")
        self.assertTrue(any(f["factor"] == "Repeated pattern" for f in r["factors"]))

    def test_sequence_is_penalised(self):
        r = analyze_password("Abcd1234!xyZ")
        self.assertTrue(any(f["factor"] == "Predictable sequence" for f in r["factors"]))

    def test_long_mixed_password_is_very_strong(self):
        r = analyze_password("Zx9$kLm2#Qp7wR4!vN")
        self.assertEqual(r["rating"], "Very Strong")
        self.assertEqual(r["score"], 94)
        self.assertEqual(r["character_types_present"], 4)

    def test_boundary_scores_stay_between_0_and_100(self):
        for pw in ("a", "A" * 128, "!" * 5, "Aa1!" * 32):
            self.assertTrue(0 <= analyze_password(pw)["score"] <= 100)

    def test_invalid_input_raises(self):
        for bad in ("", None, 123, "x" * 129):
            with self.assertRaises(ValueError):
                analyze_password(bad)

    def test_password_is_never_returned(self):
        secret = "Zx9$kLm2#Qp7wR4!vN"
        self.assertNotIn(secret, json.dumps(analyze_password(secret)))


if __name__ == "__main__":
    unittest.main()
