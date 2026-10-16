#!/usr/bin/env python3
"""Inspect team stdout captured inside a cambc .repl26a ZIP bundle."""
import argparse
from pathlib import Path
from zipfile import ZipFile, is_zipfile

ERROR_TOKENS = ("HEURISTIC_V1_ERROR", "Traceback", "bot error:", "Error:", "Exception:")


def inspect(path, max_lines=15):
    if not is_zipfile(path):
        raise ValueError(f"not a ZIP replay bundle: {path}")
    print(f"REPLAY {path}")
    with ZipFile(path) as archive:
        for side in ("team-a", "team-b"):
            filename = side + ".stdout"
            if filename not in archive.namelist():
                print(f"{side}: stdout not found")
                continue
            text = archive.read(filename).decode("utf-8", "replace")
            lines = text.splitlines()
            problems = [line for line in lines if any(p in line for p in ERROR_TOKENS)]
            print(f"{side}: {len(lines)} stdout lines; {len(problems)} exception-like lines")
            for line in problems[:max_lines]:
                print("  ERROR", line[:700])
            if not problems:
                for line in lines[:min(max_lines, 5)]:
                    print("  SAMPLE", line[:300])
    return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--max-lines", type=int, default=15)
    args = parser.parse_args()
    for path in args.paths:
        inspect(path, args.max_lines)


if __name__ == "__main__":
    main()
