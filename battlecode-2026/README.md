# Cambridge Battlecode 2026 Autumn (CAMBC 2026a)

Competition code in `rl-lab`, with a pinned `cambc` SDK version in `cambc.toml`.

## Bot directories

- `bots/starter-python/`: pristine starter from the official CLI.
- `bots/baseline/`: control bot copied from starter; do not modify during A/B tests.
- `bots/heuristic-v1/`: first candidate (Python). Same `src/main.py` entrypoint convention.

Architecture in v1: `src/draft.py` deterministic champion draft; `src/bot.py` game interaction; `src/policy.py` pure banking, resource scoring and stat choice. No ML training or C++ migration yet.

## Evidence and plan

Read [notes/2026-10-16-heuristic-v1-direction.md](notes/2026-10-16-heuristic-v1-direction.md).
Preserved fixture: `replays/baseline-vs-starter-stats.json` (one *starter vs starter* game, not an improvement score). The current saved file is aggregate statistics, not a replay timeline.

## Offline validation (no native SDK install needed)

From the repository root:

```sh
python -m compileall -q battlecode-2026/bots/heuristic-v1/src battlecode-2026/tools battlecode-2026/tests
python -m unittest discover -v -s battlecode-2026/tests -p 'test_*.py'
python battlecode-2026/tools/summarize_stats.py battlecode-2026/replays/baseline-vs-starter-stats.json --candidate-side teamA
```

## Actual-match validation (requires cambc CLI)

From `battlecode-2026/`:

```sh
python -m pip install 'cambc==2.1.6'
cambc run --help
cambc run-batch --help
```

The **Autumn 2026a** CLI syntax was verified on Linux in GitHub Actions. It supports \`cambc run BOT_A BOT_B --map MAP --statistics FILE\`; **there is no \`test-run\` or \`--seed\` command/flag in 2.1.6**.

Create a side-swapped evaluation manifest for multiple seeds/maps:

```sh
python tools/eval_matches.py --maps lanes ambush pilgrimage
python tools/eval_matches.py --maps lanes ambush pilgrimage --execute
```

This creates `replays/eval-v1/manifest.csv` with 30 planned games (candidate vs baseline in both team positions). To execute, provide a locally verified `--run-template` using placeholders `{team_a}`, `{team_b}`, `{map}`, `{seed}`, `{stats}` and add `--execute`. The runner **requires** that each completed match writes the named stats JSON file, and fails if it does not.

After collecting stats:

```sh
python tools/summarize_stats.py --manifest replays/eval-v1/manifest.csv
```

The reports contain per-match and overall win fraction, score differential, gems/round, deaths, unspent gold fraction and engine fault count. Inspect runner logs for `HEURISTIC_V1_ERROR`; this marker identifies caught Python exceptions which can otherwise be invisible in engine fault counters.

## Current status (2026-10-16)

- [x] Original SDK, maps and starter code committed
- [x] Starter-vs-starter stats recorded; zero engine-reported bot faults
- [x] Dated direction note and isolated heuristic-v1 candidate created
- [x] Offline test/CI definitions and stats evaluator added
- [ ] Actual `cambc run` and `test-run` on the new candidate, on several seeds/maps
- [ ] Inspect exception logs, fuel/runtime, and frame-by-frame replay
- [ ] Controlled ablations and validated ladder submission

Competition objective is to deposit gems at altars. Do not confuse this Autumn game with the older 2026 mining/base-defense Battlecode edition.
