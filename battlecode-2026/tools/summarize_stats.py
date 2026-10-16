#!/usr/bin/env python3
"""Summarize CAMBC 2026a *-stats.json files.

Optional CSV manifest columns: stats,candidate_side,map,trial.
Without a manifest, --candidate-side applies to every supplied JSON path.
This is post-match analysis, not a replacement for the native cambc runner.
"""
import argparse
import csv
import json
from pathlib import Path
from statistics import mean


METRICS = ("submittedGems", "collectedGems", "deaths", "earnedGold",
           "spentGold", "gold", "monsterDamageDone", "monsterDamageTaken",
           "championDamageDone", "championDamageTaken", "kills")


def summarize_match(stats):
    result = []
    for team in (0, 1):
        champions = [c for c in stats["champions"] if c["team"] == team]
        row = {"team": team, "champion_count": len(champions)}
        for metric in METRICS:
            row[metric] = sum(c.get(metric, 0) for c in champions)
        row["gems_per_round"] = (row["submittedGems"] /
                                 max(1, stats.get("round", 0)))
        row["gold_idle_fraction"] = (row["gold"] /
                                     max(1, row["earnedGold"]))
        result.append(row)
    return {
        "round": stats.get("round"),
        "outcome": stats.get("outcome"),
        "faults": stats.get("botFaults", []),
        "teams": result,
    }


def candidate_results(records):
    """Records of (match_summary, candidate_side, map, seed)."""
    games = []
    for summary, side, map_name, trial in records:
        if side not in ("teamA", "teamB"):
            raise ValueError("candidate_side must be teamA or teamB")
        index = 0 if side == "teamA" else 1
        own, opponent = summary["teams"][index], summary["teams"][1 - index]
        outcome = summary["outcome"]
        games.append({
            "map": map_name, "trial": trial, "side": side,
            "win": 1.0 if outcome == side else (0.5 if outcome in ("draw", "tie") else 0.0),
            "gem_diff": own["submittedGems"] - opponent["submittedGems"],
            "gems": own["submittedGems"], "deaths": own["deaths"],
            "gems_per_round": own["gems_per_round"],
            "gold_idle_fraction": own["gold_idle_fraction"],
            "faults": (summary["faults"][index] if len(summary["faults"]) > index else None),
        })
    return games


def report(games):
    if not games:
        raise ValueError("no matches to summarize")
    keys = ("win", "gem_diff", "gems", "deaths", "gems_per_round", "gold_idle_fraction")
    result = {"games": len(games)}
    for key in keys:
        result["mean_" + key] = round(mean(g[key] for g in games), 4)
    result["faults"] = sum(g["faults"] or 0 for g in games)
    result["by_side"] = {}
    for side in ("teamA", "teamB"):
        subset = [g for g in games if g["side"] == side]
        if subset:
            result["by_side"][side] = {
                "games": len(subset),
                "win_rate": round(mean(g["win"] for g in subset), 4),
                "mean_gem_diff": round(mean(g["gem_diff"] for g in subset), 2),
            }
    return result


def load_records(paths, side, manifest=None):
    if manifest is None:
        for path in paths:
            with open(path, encoding="utf8") as f:
                yield summarize_match(json.load(f)), side, "", ""
        return
    with open(manifest, newline="", encoding="utf8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        path = Path(row["stats"])
        if not path.is_absolute():
            path = Path(manifest).parent / path
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open(encoding="utf8") as file:
            yield (summarize_match(json.load(file)),
                   row["candidate_side"], row.get("map", ""), row.get("trial", ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--candidate-side", choices=("teamA", "teamB"), default="teamA")
    args = parser.parse_args()
    if not args.paths and not args.manifest:
        parser.error("provide stats files or --manifest")
    games = candidate_results(load_records(args.paths, args.candidate_side, args.manifest))
    print(json.dumps({"summary": report(games), "matches": games}, indent=2))


if __name__ == "__main__":
    main()
