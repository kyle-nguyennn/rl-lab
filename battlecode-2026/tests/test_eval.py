"""Regression tests against the committed starter-vs-starter stats fixture."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from summarize_stats import summarize_match, candidate_results, report
from eval_matches import matrix


class StatisticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "replays" / "baseline-vs-starter-stats.json").open() as file:
            cls.stats = json.load(file)

    def test_replay_totals(self):
        summary = summarize_match(self.stats)
        self.assertEqual(summary["round"], 1863)
        self.assertEqual(summary["outcome"], "teamB")
        self.assertEqual(summary["faults"], [0, 0])
        self.assertEqual(summary["teams"][0]["submittedGems"], 894)
        self.assertEqual(summary["teams"][1]["submittedGems"], 1038)
        self.assertEqual(summary["teams"][0]["deaths"], 50)
        self.assertEqual(summary["teams"][1]["deaths"], 65)
        self.assertEqual(summary["teams"][1]["champion_count"], 6)

    def test_candidate_side_is_explicit(self):
        summary = summarize_match(self.stats)
        games = candidate_results([(summary, "teamA", "contest", 1),
                                   (summary, "teamB", "contest", 1)])
        self.assertEqual([g["win"] for g in games], [0.0, 1.0])
        self.assertEqual([g["gem_diff"] for g in games], [-144, 144])
        self.assertEqual(report(games)["mean_win"], 0.5)

    def test_evaluation_matrix_swaps_sides(self):
        rows = list(matrix(["contest", "lanes"], [1, 2]))
        self.assertEqual(len(rows), 8)
        self.assertEqual([r["candidate_side"] for r in rows[:2]],
                         ["teamA", "teamB"])
        self.assertNotEqual(rows[0]["team_a"], rows[1]["team_a"])
        self.assertEqual(rows[0]["map_file"], "maps/contest.map26a")


if __name__ == "__main__":
    unittest.main()
