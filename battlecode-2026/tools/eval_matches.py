#!/usr/bin/env python3
"""Run Autumn 2026 CLI matches with side swapping and a statistics manifest.

The verified cambc 2.1.6 `run` CLI has --map and --statistics, but NO --seed.
Replicates on an unchanged map may be identical; diversify across maps and
drafts rather than interpreting a trial index as an engine RNG seed.
"""
import argparse
import csv
from pathlib import Path
import shlex
import subprocess


DEFAULT_COMMAND = "cambc run {team_a} {team_b} --map {map} --statistics {stats}"


def matrix(maps, trials=(1,), candidate="heuristic-v1", control="baseline"):
    """Yield symmetric side-swapped configurations; trial is a label, NOT seed."""
    for map_name in maps:
        for trial in trials:
            for side in ("teamA", "teamB"):
                a = candidate if side == "teamA" else control
                b = control if side == "teamA" else candidate
                yield {
                    "map": map_name,
                    "trial": str(trial),
                    "candidate_side": side,
                    "team_a": a,
                    "team_b": b,
                    "stats": f"{map_name}-trial{trial}-{side}-stats.json",
                }


def execute(rows, template, output_dir):
    for row in rows:
        args = {
            "team_a": row["team_a"], "team_b": row["team_b"],
            "map": row["map"], "trial": row["trial"],
            "stats": str((output_dir / row["stats"]).resolve()),
        }
        command = [part.format(**args) for part in shlex.split(template)]
        print("RUN:", shlex.join(command), flush=True)
        subprocess.run(command, check=True)
        if not (output_dir / row["stats"]).exists():
            raise FileNotFoundError(
                f"runner finished without stats: {output_dir / row['stats']}"
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maps", nargs="+", required=True)
    parser.add_argument("--trials", nargs="+", type=int, default=[1])
    parser.add_argument("--candidate", default="heuristic-v1")
    parser.add_argument("--control", default="baseline")
    parser.add_argument("--out", type=Path, default=Path("replays/eval-v1/manifest.csv"))
    parser.add_argument("--run-template", default=DEFAULT_COMMAND,
                        help="verified default for cambc 2.1.6; placeholders: "
                             "{team_a}, {team_b}, {map}, {trial}, {stats}")
    parser.add_argument("--execute", action="store_true",
                        help="otherwise write manifest only")
    args = parser.parse_args()
    rows = list(matrix(args.maps, args.trials, args.candidate, args.control))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf8") as output:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} matches to {args.out}")
    if args.execute:
        execute(rows, args.run_template, args.out.parent)


if __name__ == "__main__":
    main()
