"""Autumn 2026 Python bot loop with bounded, observable diagnostics."""
import traceback
import cambc
import draft
from bot import Bot


def main():
    bot = Bot()
    errors = 0
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
                bot.play_turn()
        except Exception as error:
            # In-match stdout goes into team-*.stdout in the ZIP replay bundle.
            # Catching errors otherwise hides them from the engine's botFaults.
            if errors < 3:
                print("HEURISTIC_V1_ERROR:", type(error).__name__,
                      str(error), flush=True)
                print(traceback.format_exc(limit=5), flush=True)
            errors += 1
        cambc.end_turn()


if __name__ == "__main__":
    main()
