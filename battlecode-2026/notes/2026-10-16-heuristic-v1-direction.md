# Battlecode Autumn 2026 — heuristic-v1 direction
Date: **2026-10-16** (Asia/Singapore)
Status: **implementation in progress**; no ladder claim.

## Baseline evidence
Repository: `kyle-nguyennn/rl-lab/battlecode-2026`, SDK 2.1.6.
Official starter reference: `bots/starter-python`. Baseline control: `bots/baseline`. Both contain identical starter code; never modify them during experiments.
Existing `replays/baseline-vs-starter-stats.json`: round 1863; bot faults [0, 0]; team A 894 submitted gems, 50 deaths, 486 unspent gold; team B 1038 submitted gems, 65 deaths, 1334 unspent gold. **This is one random-draft match, not a policy A/B test.** Team B drafted Cassi & Issac, which generates two playable champions for one draft slot. Both sides report zero champion damage. The existing artifact is aggregate statistics, not a frame-by-frame replay. Python exceptions are caught in the original starter, so zero botFaults does not imply zero Python exceptions.

## Objective
Maximize **submitted gems per match**, subject to champion survival, action/CPU limits, and submission validity. Preserve a working baseline before trying reinforcement learning, model-based planning, or rewriting the game engine. Quantities of interest: win rate with confidence bounds, gem differential, gems per round, deaths, wasted gold, champion mix, and errors.

## v1 hypotheses (to ablate individually)
1. **Reward-aware camp selection:** select camp groups using their known gem and gold rewards, distance, and a small contention penalty. Ignore groups known to be respawning; do not assume hidden group state is observable.
2. **Threshold banking:** avoid trips to an altar after each single gem; bank earlier at low health, when opponents are nearby, near an altar, or when a match is ending. The threshold must be tuned; carrying too many gems increases death exposure.
3. **Deterministic builds:** remove random strength/focus/health stat purchases. Choose a build from the champion's SDK stats and skill profile; subsequently tune per-champion builds.
4. **Basic ability utilization:** use safe offensive abilities against visible camps and self-healing where legal. Respect cooldown, casting rights, target kinds and position.
5. **Legal movement goals:** navigate to *unoccupied attack-range/altar-range approach tiles*, rather than trying to enter the camp/altar tile itself.
6. **Reproducibility:** deterministic draft for candidate and testing across maps, seeds and swapped sides. Treat different drafts/side as confounders.

## Implementation boundaries
- New candidate under `bots/heuristic-v1/src/` with the same `main.py`/draft/game loop entry points as the Python starter.
- Split pure decision functions into `policy.py`; unit-test without importing the native SDK.
- Add `tools/summarize_stats.py` to reduce `*-stats.json` files into per-match and comparative metrics.
- Add a repeatable match wrapper only once actual Autumn 2026 CLI flags have been checked with `cambc run --help`; do **not** reuse Spring 2026 flags unverified.
- Use `cambc==2.1.6` for actual integration runs. The local coding environment may lack the native CLI; Python compile/unit checks are not equivalent to a played match.
- Track engine-side faults **and** printed Python exception lines.

## Acceptance criteria
- Code compiles and pure policy/stat tests pass.
- Candidate starts, finishes matches on multiple bundled maps without bot faults and without `bot error` in logs.
- At least 10 seed/side-controlled matches per ablation before trusting a leaderboard claim; report exact match configuration.
- Compare candidate against identical reference controls, then against stronger field opponents.
- Submit only a verified artifact; document CLI command, game build, map, seed, and stats paths.

## Next tests
1. `heuristic-v1` against unchanged `baseline`, both sides, at least three maps.
2. A/B disable threshold banking, then reward-aware camp selection, then abilities and deterministic build.
3. Profile fuel, turn cost and failed actions before considering native C++ or RL.
4. After scoring gains plateau, consider opponent modeling, coordinated camp allocation, lane roles, ability combinations and learned policies.

## Unknowns / risk
The available GitHub repo lacks turn-by-turn replays and actual command logs; verify draft balance and latency with real runs. The current match's Team B victory is not evidence of candidate skill. A fixed score threshold or champion lineup should not be treated as optimal without controlled experiments.
