"""Control draft: exactly mirror starter's spawn-seeded deterministic choices.

Using an independently fixed line-up would confound comparison with the
original starter. When comparing same-map/same-side runs, both implementations
now choose the same champions for that side.
"""
import cambc
from randomness import below


def play():
    chosen = cambc.draft.current_draft(cambc.Team.ALLY)
    available = [pick for pick in range(11) if pick not in chosen]
    cambc.draft_memory.submit(b"hello world")
    cambc.draft.pick(available[below(len(available))])
