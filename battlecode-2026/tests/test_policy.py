"""Offline policy tests: do not require the native cambc module."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bots" / "heuristic-v1" / "src"))
from policy import should_bank, camp_score, choose_purchase_stat


class PolicyTests(unittest.TestCase):
    def test_no_gems_no_banking(self):
        self.assertFalse(should_bank(0, 1.0, 2, False, 400, 100))

    def test_bank_if_winning(self):
        self.assertTrue(should_bank(5, 1.0, 15, False, 400, 5))

    def test_bank_when_near_and_not_tiny(self):
        self.assertTrue(should_bank(4, 1.0, 2, False, 400, 100))
        self.assertFalse(should_bank(1, 1.0, 2, False, 400, 100))

    def test_bank_at_risk(self):
        self.assertTrue(should_bank(3, 0.4, 12, False, 400, 100))
        self.assertTrue(should_bank(3, 1.0, 12, True, 400, 100))

    def test_bank_at_end(self):
        self.assertTrue(should_bank(2, 1.0, 10, False, 10, 100))

    def test_camp_value(self):
        self.assertGreater(camp_score(25, 10, 4, 2),
                           camp_score(10, 10, 4, 2))
        self.assertGreater(camp_score(25, 10, 4, 2),
                           camp_score(25, 10, 15, 2))
        self.assertGreater(camp_score(25, 10, 4, 2),
                           camp_score(25, 10, 4, 2, nearby_allies=3))

    def test_build_not_random(self):
        self.assertEqual(choose_purchase_stat(10, 3, True), 0)
        self.assertEqual(choose_purchase_stat(3, 10, False), 1)


if __name__ == "__main__":
    unittest.main()
