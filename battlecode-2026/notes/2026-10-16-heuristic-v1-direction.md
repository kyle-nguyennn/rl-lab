# Battlecode Autumn 2026 — heuristic-v1 direction
Date: **2026-10-16** (Asia/Singapore)
Status: **candidate implemented; validates at runtime but underperforms control**. No ladder submission.

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

## Execution record — 2026-10-16

- Added candidate code, pure-policy unit tests, statistical analyzer, match matrix generator, replay stdout inspector, and GitHub Actions automation on `feat/battlecode-2026-heuristic-v1`.
- Verified actual CLI 2.1.6 syntax: `cambc run BOT_A BOT_B --map MAP --statistics FILE`. There is **no `test-run` subcommand or `--seed` flag** in this release. A trial label is not a seed.
- Original v1 scored **0 gems** in both contest and ambush matches, yet `botFaults` was zero. Replay ZIPs contain `team-a.stdout`/`team-b.stdout`; captured errors identified bad `move_absolute` destinations and spells after normal movement.
- Replaced custom camp approach-tile movement with the starter's known-good occupied-camp distance-field roots; skip forbidden movement endpoints; forbid casting offensive abilities after normal movement. After these fixes, the candidate scored **504 gems** against baseline's **1038** in an ambush game with no printed Python exceptions.
- To remove the deterministic-draft confound, copied starter RNG and starter draft semantics into the candidate (champion choice remains deterministic per spawn). On `ambush`, candidate Team A scored **504 vs 1038** baseline B; candidate Team B **696 vs 966** baseline A. Both matches finished with zero engine faults and no `HEURISTIC_V1_ERROR` markers. **Win rate: 0/2; do not submit this candidate as a stronger bot yet.**
- Integration evidence: [GitHub Actions side-swapped ambush run](https://github.com/kyle-nguyennn/rl-lab/actions/runs/38861308987). Match replays and stats are available as that run's artifacts.

### Interpretation / next measured ablation

The runtime issue is fixed, but the policy is materially weaker than the unchanged starter. It is premature to attribute this to banking, builds, spells or camp choices from two matches. Next isolate **nearest-camp baseline routing vs reward-aware group scoring**, then banking threshold, deterministic item selection and spell logic one component at a time. Track submitted and collected gems separately, along with monster damage, gold earned/spent, deaths, and stdout errors. Use multiple maps and side swaps; do not invent a seed argument. Retain the unchanged starter for a safe Sprint 1 submission if no variant beats it.
