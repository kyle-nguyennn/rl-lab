#!/usr/bin/env python3
"""Produce reproducible side-swapped evaluation plans, optionally execute them.

Example (from battlecode-2026/):
 python tools/eval_matches.py --maps contest lanes --seeds 1 2 3
 # Inspect `cambc run --help` for your installed Autumn 2026 version.
 python tools/eval_matches.py --maps contest lanes --seeds 1 2 3 \
   --run-template 'cambc run {team_a} {team_b} {map} --seed {seed} <verified-stats-option> {stats}' \
   --execute

No CLI flags beyond those supplied in --run-template are assumed.
"""
import argparse
import csv
from pathlib import Path
import shlex
import subprocess


def matrix(maps, seeds, candidate="bots/heuristic-v1", control="bots/baseline"):
    """Yield symmetric side-swapped match configurations."""
    for map_name in maps:
        for seed in seeds:
            for side in ("teamA", "teamB"):
                a = candidate if side == "teamA" else control
                b = control if side == "teamA" else candidate
                filename = f"{map_name}-seed{seed}-{side}-stats.json"
                yield {
                    "map": map_name,
                    "seed": str(seed),
                    "candidate_side": side,
                    "team_a": a,
                    "team_b": b,
                    "map_file": f"maps/{map_name}.map26a",
                    "stats": filename,
                }


def execute(rows, template, output_dir):
    if not template:
        raise ValueError("--execute requires --run-template from verified cambc --help")
    for row in rows:
        args = {
            "team_a": row["team_a"], "team_b": row["team_b"],
            "map": row["map_file"], "seed": row["seed"],
            "stats": str((output_dir / row["stats"]).resolve()),
        }
        command = [part.format(**args) for part in shlex.split(template)]
        print("RUN:", shlex.join(command), flush=True)
        subprocess.run(command, check=True)
        if not (output_dir / row["stats"]).exists():
            raise FileNotFoundError(
                f"runner completed but stats missing: {output_dir / row['stats']}. "
                "Check your CLI's statistics-output option."
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maps", nargs="+", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--candidate", default="bots/heuristic-v1")
    parser.add_argument("--control", default="bots/baseline")
    parser.add_argument("--out", type=Path, default=Path("replays/eval-v1/manifest.csv"))
    parser.add_argument("--run-template",
                        help="explicitly verified CLI command template; placeholders: "
                             "{team_a}, {team_b}, {map}, {seed}, {stats}")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    rows = list(matrix(args.maps, args.seeds, args.candidate, args.control))
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
