"""Reward-aware farming bot for Autumn 2026 SDK 2.1.6.

No native-engine modifications. Keep reference bots/baseline untouched.
"""
import cambc
from cambc import game_map
from policy import should_bank, camp_score, choose_purchase_stat

Team, Item = cambc.Team, cambc.ItemType


def area(position, radius):
    bb = cambc.Bitboard()
    bb.draw_chebyshev(position, radius)
    return bb


def obstacles():
    """Only include *known* obstacles; fog-of-war is not omniscient."""
    bb = (game_map.walls() | game_map.holes() | game_map.altars()
          | game_map.spawn_region(Team.ENEMY) | cambc.vision.champion_tiles()
          | cambc.vision.camp_tiles() | cambc.vision.teleport_tiles())
    bb.set(cambc.me().position(), False)
    return bb


def approach(goals):
    """Reuse the starter's working distance-field movement for camp roots."""
    me = cambc.me()
    origin = me.position()
    if not me.can_move() or goals.is_set(origin):
        return False
    blocked = obstacles()
    # Camps may occupy goals: allow them as distance-field roots but not steps.
    goals &= ~blocked | cambc.vision.camp_tiles()
    if goals.is_empty():
        return False
    if goals.count() == 1 and not blocked.is_set(goals.positions()[0]):
        return me.move_towards(goals.positions()[0])
    field = cambc.DistanceField()
    field.compute_to(blocked & ~goals, goals, area(origin, 0), cambc.Bitboard())
    candidates = [origin, *blocked.reachable_tiles(
        origin, me.base_stats().base_move_speed).positions()]
    current = field.get(origin)
    candidates.sort(key=field.get)
    for step in candidates:
        if step == origin or field.get(step) >= current:
            continue
        try:
            if me.move_absolute(step):
                return True
        except cambc.Error:
            # Known occupied endpoint: try the next legal path candidate.
            continue
    return False


def try_attack(target):
    me = cambc.me()
    if not me.can_attack() or not target.is_visible() or target.health() <= 0:
        return False
    if not me.attack_tiles().is_set(target.position()):
        return False
    me.attack(target)
    return True


def try_damage_ability(target):
    """Only unit-targeted damaging abilities against legal visible camps."""
    me = cambc.me()
    if not me.can_cast() or not target.is_visible() or target.health() <= 0:
        return False
    for ability in me.abilities():
        if (ability.is_ready() and (ability.is_damage() or ability.is_aoe_damage())
                and ability.can_target_camps()
                and ability.valid_tiles().is_set(target.position())):
            if ability.use(target):
                return True
    return False


def try_self_heal():
    me = cambc.me()
    if not me.can_cast() or me.health() >= me.max_health() * 0.65:
        return False
    for ability in me.abilities():
        if ability.is_ready() and ability.is_heal() and ability.can_target_self():
            if ability.use(me):
                return True
    return False


def altar_targets():
    """Return unlocked altars in ascending direct distance (not path length)."""
    origin = cambc.me().position()
    return sorted(
        (altar for altar in game_map.altars().positions()
         if not cambc.vision.has_altar_lock(altar)),
        key=lambda altar: origin.chebyshev_distance(altar),
    )


def deposit_or_approach(altars):
    if not altars:
        return False
    me = cambc.me()
    closest = altars[0]
    if me.position().chebyshev_distance(closest) <= cambc.constants.SUBMIT_GEMS_RANGE:
        me.submit_gems(closest)
        return True
    roots = cambc.Bitboard()
    for altar in altars:
        roots |= area(altar, cambc.constants.SUBMIT_GEMS_RANGE)
    # Will not try to move onto the occupied altar itself.
    return approach(roots)


def preferred_group():
    """Estimate reward density for each camp group; skip known respawns."""
    me = cambc.me()
    origin = me.position()
    vision = cambc.vision.visible_tiles()
    allies = [c.position() for c in cambc.vision.champions(Team.ALLY)
              if c != me and c.is_alive()]
    enemies = [c.position() for c in cambc.vision.champions(Team.ENEMY)]
    best = None
    best_score = -1.0
    for group in game_map.camp_groups():
        spawns = group.spawn_tiles().positions()
        if not spawns:
            continue
        if not (group.spawn_tiles() & vision).is_empty():
            if isinstance(group.state(), game_map.CampGroupRespawning):
                continue
        travel = min(origin.chebyshev_distance(p) for p in spawns)
        competing = sum(min(a.chebyshev_distance(p) for p in spawns) <= 4
                        for a in allies)
        danger = sum(min(e.chebyshev_distance(p) for p in spawns) <= 4
                     for e in enemies)
        score = camp_score(group.gem_value(), group.gold_value(),
                           travel, len(spawns), competing, danger)
        if score > best_score:
            best, best_score = group, score
    return best


def farm():
    me = cambc.me()
    # A visible low-health camp is normally the fastest reward to finish.
    visible_camps = [c for c in cambc.vision.camps() if c.is_visible() and c.health() > 0]
    visible_camps.sort(key=lambda c: (c.health(), c.position().chebyshev_distance(me.position())))
    for camp in visible_camps:
        if me.attack_tiles().is_set(camp.position()):
            used = try_damage_ability(camp)
            attacked = try_attack(camp)
            if used or attacked:
                return True
            # In range but attack/cast on cooldown; hold rather than walk away.
            return True

    group = preferred_group()
    if group is None:
        return False
    # The unchanged starter successfully navigates using occupied camp tiles
    # as distance-field roots (but not legal movement destinations).
    moved = approach(group.spawn_tiles().copy())
    if moved:
        # Moving can reveal a new camp and may leave the attack ready.
        for camp in cambc.vision.camps():
            if camp.is_visible() and camp.health() > 0:
                # Certain spells cannot be cast AFTER normal movement.
                if try_attack(camp):
                    break
    return moved


class Bot:
    def __init__(self):
        self.stat = None

    def buy_items(self):
        me = cambc.me()
        if self.stat is None:
            stats = me.base_stats()
            offensive = any((a.is_damage() or a.is_aoe_damage()) for a in me.abilities())
            self.stat = choose_purchase_stat(stats.base_strength, stats.base_focus, offensive)
        item = (Item.POWER_SHARD_OF_STRENGTH, Item.POWER_SHARD_OF_FOCUS)[self.stat]
        count = me.gold_count() // item.cost()
        if count > 0 and me.can_buy(item, count):
            me.buy(item, count)

    def play_turn(self):
        me = cambc.me()
        if (not me.is_alive() or me.is_recalling()
                or me.is_submitting_gems() or me.is_teleporting()):
            return

        at_spawn = game_map.spawn_region(Team.ALLY).is_set(me.position())
        if at_spawn:
            self.buy_items()

        # Heal before falling back to a recall; spell is legal only when ready.
        try_self_heal()
        health_ratio = me.health() / max(1.0, me.max_health())
        if health_ratio < 0.35 and not at_spawn:
            me.recall()
            return
        if not (me.can_move() or me.can_attack() or me.can_cast()):
            return

        gems = me.gem_count()
        altars = altar_targets() if gems else []
        dist = (me.position().chebyshev_distance(altars[0])
                if altars else game_map.width() + game_map.height())
        enemy_nearby = bool(cambc.vision.champions(Team.ENEMY))
        rounds_left = max(0, cambc.constants.MAX_ROUNDS - cambc.round_number())
        shortfall = (cambc.constants.WINNING_GEMS
                     - cambc.global_submitted_gems(Team.ALLY))
        if altars and should_bank(gems, health_ratio, dist, enemy_nearby,
                                  rounds_left, shortfall):
            if deposit_or_approach(altars):
                return

        # Opportunistic defensive basic attack; no chasing enemies carrying gems.
        if gems == 0 and health_ratio >= 0.65:
            for enemy in cambc.vision.champions(Team.ENEMY):
                if try_attack(enemy):
                    return
        farm()
