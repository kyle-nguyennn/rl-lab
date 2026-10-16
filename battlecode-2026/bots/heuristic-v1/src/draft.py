"""Fixed draft to reduce random-composition confounding in evaluations."""
import cambc

# Enum members instead of raw unit IDs: Cassi & Issac is ONE draft pick but TWO units.
ORDER = (
    cambc.ChampionDraft.CASSI_AND_ISSAC,
    cambc.ChampionDraft.VESPER_VALE,
    cambc.ChampionDraft.VENDETTA,
    cambc.ChampionDraft.TAVI,
    cambc.ChampionDraft.MARCELLA,
    cambc.ChampionDraft.RYTH,
    cambc.ChampionDraft.STELLAR,
    cambc.ChampionDraft.WILLOW,
    cambc.ChampionDraft.REN,
    cambc.ChampionDraft.VARG,
    cambc.ChampionDraft.PRISM,
)


def play():
    already = cambc.draft.current_draft(cambc.Team.ALLY)
    for choice in ORDER:
        if choice not in already:
            cambc.draft.pick(choice)
            return
    raise RuntimeError("no available champion to draft")
