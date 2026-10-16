# Battlecode 2026

Cambridge Battlecode 2026 competition workspace within RL-lab.

## Immediate objective

Build, test, and submit a valid Sprint 1 bot before the submission lock. Prioritize a reliable deterministic baseline over reinforcement learning.

## Implementation plan

1. Import the official competition starter kit and preserve its required entry point, language, and build layout.
2. Verify local build and run an example match.
3. Implement basic mining, resource logistics, expansion, and core defense.
4. Run multi-map regression matches and inspect replays.
5. Validate the official runtime constraints and submit to the ladder.
6. After a verified baseline, add reproducible evaluations and investigate high-level RL policies.

## Project boundaries

Keep competition-specific bot code and tests here. Reuse graph and pathfinding ideas from `algo-labs` and `MazeRunner` only when compatible with the official SDK. Do not introduce an RL training dependency into the submitted bot unless it demonstrably improves performance and fits runtime limits.

## Status

- [x] Workspace initialized
- [ ] Official starter imported
- [ ] Local match passes
- [ ] Ladder submission accepted
