"""Official Python entry-point shape; report exceptions rather than hiding them."""
import traceback
import cambc
import draft
from bot import Bot


def main():
    bot = Bot()
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
                bot.play_turn()
        except Exception:
            # An exception may not increment the engine's botFaults counter.
            # Preserve the engine loop, but emit a reliably detectable marker.
            print("HEURISTIC_V1_ERROR", flush=True)
            traceback.print_exc()
        cambc.end_turn()


if __name__ == "__main__":
    main()
