"""Pure policy functions; deliberately no cambc import so they can be unit-tested.

Heuristic constants are hypotheses, not tuned competition parameters.
"""


def should_bank(gems, health_ratio, altar_distance, enemy_nearby,
                rounds_left, winning_shortfall):
    """Choose between another farm trip and depositing carried gems."""
    if gems <= 0:
        return False
    if 0 < winning_shortfall <= gems:
        return True
    if rounds_left <= max(14, altar_distance * 3 + 6):
        return True
    if gems >= 18:
        return True
    if enemy_nearby or health_ratio <= 0.45:
        return gems >= 3
    if altar_distance <= 2 and gems >= 4:
        return True
    threshold = max(8, min(15, 8 + altar_distance // 3))
    return gems >= threshold


def camp_score(gem_reward, gold_reward, travel_tiles, camp_count,
               nearby_allies=0, danger=0):
    """Approximate expected gem-equivalent reward per effort; higher is better."""
    reward = max(0, gem_reward) + 0.02 * max(0, gold_reward)
    effort = 3.0 + max(0, travel_tiles) + 2.0 * max(0, camp_count - 1)
    effort += max(0, danger) * 4.0
    return reward / (effort * (1.0 + 0.35 * max(0, nearby_allies)))


def choose_purchase_stat(base_strength, base_focus, offensive_ability):
    """0=strength, 1=focus; use observed champion design, not random picks."""
    if base_focus >= base_strength * (0.95 if offensive_ability else 1.15):
        return 1
    return 0
