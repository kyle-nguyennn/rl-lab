# Cambridge Battlecode Autumn 2026 (CAMBC 2026a)

Bot experiments under `rl-lab/battlecode-2026`. The pinned CLI/SDK is `cambc==2.1.6`.

## Layout

- `bots/starter-python/`: untouched official Python starter.
- `bots/baseline/`: untouched experimental control (initially an identical copy of the starter).
- `bots/heuristic-v1/`: first **experimental** candidate. `src/main.py` is the entrypoint, `draft.py` reproduces the starter RNG/draft choices, `bot.py` uses the game API, and `policy.py` has pure policy functions.
- `tools/eval_matches.py`: produce side-swapped match manifest, and optionally run it.
- `tools/summarize_stats.py`: compare stats including gem throughput, deaths and economy.
- `tools/inspect_replay.py`: inspect stdout/errors inside .repl26a ZIP bundles.
- `tools/validate_runtime.py`: reject engine faults, caught Python exceptions or zero-scoring candidates.
- `tests/`: offline policy and statistics regression tests.
- `notes/2026-10-16-heuristic-v1-direction.md`: dated hypotheses, constraints and measured evidence.

## Setup and offline checks

Run from repository root:

```sh
python -m compileall -q battlecode-2026/bots/heuristic-v1/src battlecode-2026/tools battlecode-2026/tests
python -m unittest discover -v -s battlecode-2026/tests -p 'test_*.py'
```

Install the pinned CLI and run games **from battlecode-2026/**:

```sh
python -m pip install 'cambc==2.1.6'
cambc run --help
mkdir -p replays/eval-local
cambc run heuristic-v1 baseline --map ambush --statistics replays/eval-local/A.json
cambc run baseline heuristic-v1 --map ambush --statistics replays/eval-local/B.json
```

In the Autumn 2.1.6 CLI, `cambc run BOT_A BOT_B --map MAP --statistics FILE` is supported. **There is no `test-run` command or `--seed` flag**. The `run-batch` command supports four-column manifests, but its format is different from the stats evaluation CSV. Do not assume repeated runs are independent RNG samples.

## Multi-map comparisons

From `battlecode-2026/`:

```sh
# Six trials: three maps x both sides. Inspect manifest before execution.
python tools/eval_matches.py --maps lanes ambush pilgrimage
python tools/eval_matches.py --maps lanes ambush pilgrimage --execute
python tools/summarize_stats.py --manifest replays/eval-v1/manifest.csv
```

`--trials 1 2 3` labels repeated matches; **trial indices do not control random seeds**. Use map diversity, side swapping and explicitly matched drafts for validity.

Native match output `replays/*.repl26a` is a ZIP containing `team-a.stdout` and `team-b.stdout`. `HEURISTIC_V1_ERROR` markers report Python exceptions that were caught in `main.py`; these do *not* necessarily increment `botFaults`.

Example diagnostic commands:

```sh
python tools/inspect_replay.py replays/*.repl26a
python tools/validate_runtime.py --statistics replays/eval-local/A.json \
  --replay-glob 'replays/heuristic-v1-vs-baseline-*.repl26a' --side teamA --min-gems 1
```

## Validation status — 2026-10-16

- [x] Original kit, SDK and game maps imported; starter-vs-starter saved stats.
- [x] Dated experiment note and isolated `heuristic-v1` candidate created.
- [x] Unit tests, static Python compilation, metrics analyzer and CI checks passing.
- [x] Actual `cambc run` matches on `ambush`, both sides, with zero engine faults and zero caught Python exceptions.
- [x] Replay ZIP exception inspection and minimum-scoring validity gate.
- [ ] Demonstrate candidate improvement over the untouched control (current v1 **loses**).
- [ ] Extend to several maps, then component ablations, profiling and ladder validation.

### Measured side-swapped `ambush` games

| Candidate side | Candidate gems | Control gems | Outcome |
| --- | ---: | ---: | --- |
| Team A | 504 | 1,038 | Candidate loss |
| Team B | 696 | 966 | Candidate loss |

Source: [successful actual-match integration run](https://github.com/kyle-nguyennn/rl-lab/actions/runs/38861308987). **This proves runtime integration, not strategic improvement.** Avoid submitting the new heuristic in place of the baseline until an ablation shows an actual edge. Full analysis and next steps are in [the dated note](notes/2026-10-16-heuristic-v1-direction.md).
