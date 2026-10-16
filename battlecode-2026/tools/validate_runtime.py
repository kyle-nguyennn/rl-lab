#!/usr/bin/env python3
"""Enforce basic validity gates using a completed Autumn 2026 match and ZIP replay.

This catches errors that main.py deliberately handles without engine botFaults.
"""
import argparse
import glob
import json
from pathlib import Path
from zipfile import ZipFile


def validate(stats, replay, side="teamA", min_gems=0):
    index = {"teamA": 0, "teamB": 1}[side]
    faults = stats.get("botFaults", [])
    if len(faults) > index and faults[index] != 0:
        raise AssertionError(f"{side} engine faults: {faults[index]}")
    gems = sum(c.get("submittedGems", 0) for c in stats["champions"]
               if c["team"] == index)
    if gems < min_gems:
        raise AssertionError(f"{side} scored {gems} gems < required {min_gems}")
    member = ("team-a.stdout" if index == 0 else "team-b.stdout")
    with ZipFile(replay) as z:
        stdout = z.read(member)
    error_count = stdout.count(b"HEURISTIC_V1_ERROR")
    if error_count:
        raise AssertionError(f"{side} has {error_count} caught Python errors in {replay}")
    return {"side": side, "gems": gems, "errors": 0, "engine_faults": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--statistics", type=Path, required=True)
    parser.add_argument("--replay-glob", required=True)
    parser.add_argument("--side", choices=("teamA", "teamB"), required=True)
    parser.add_argument("--min-gems", type=int, default=0)
    args = parser.parse_args()
    paths = sorted(glob.glob(args.replay_glob))
    if len(paths) != 1:
        parser.error(f"expected exactly one replay matching pattern, got {paths}")
    with args.statistics.open(encoding="utf8") as f:
        data = json.load(f)
    print(json.dumps(validate(data, paths[0], args.side, args.min_gems), indent=2))


if __name__ == "__main__":
    main()
