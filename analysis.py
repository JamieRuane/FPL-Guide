"""
analysis.py - The "brain" of the site. Turns raw FPL data into recommendations.

This is the part that makes your project interesting, so it's the part
you should keep improving yourself (see the TODOs).
"""
from dataclasses import dataclass

POSITIONS = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
FIXTURES_TO_LOOK_AHEAD = 3


@dataclass
class Player:
    id: int
    name: str
    team: str
    position: str
    price: float          # in £m
    form: float           # avg points over the last 30 days
    points_per_game: float
    total_points: int
    selected_by: float    # % of managers who own him
    status: str           # "a" = available, "d" = doubtful, "i" = injured, ...
    avg_difficulty: float  # avg fixture difficulty over the next few games
    next_opponents: str
    score: float = 0.0
    value: float = 0.0


def current_gameweek(bootstrap: dict) -> int:
    for event in bootstrap["events"]:
        if event.get("is_next"):
            return event["id"]
    return bootstrap["events"][-1]["id"]


def team_fixture_info(bootstrap: dict, fixtures: list) -> dict:
    """For each team id: (average difficulty of next N games, 'ARS(H) CHE(A) ...')."""
    short = {t["id"]: t["short_name"] for t in bootstrap["teams"]}
    upcoming = sorted((f for f in fixtures if f.get("event")), key=lambda f: f["event"])

    per_team: dict[int, list[tuple[int, str]]] = {tid: [] for tid in short}
    for f in upcoming:
        home, away = f["team_h"], f["team_a"]
        if len(per_team[home]) < FIXTURES_TO_LOOK_AHEAD:
            per_team[home].append((f["team_h_difficulty"], f"{short[away]}(H)"))
        if len(per_team[away]) < FIXTURES_TO_LOOK_AHEAD:
            per_team[away].append((f["team_a_difficulty"], f"{short[home]}(A)"))

    info = {}
    for tid, games in per_team.items():
        if games:
            avg = sum(d for d, _ in games) / len(games)
            info[tid] = (round(avg, 2), " ".join(label for _, label in games))
        else:
            info[tid] = (3.0, "-")
    return info


def score_player(form: float, ppg: float, avg_difficulty: float) -> float:
    """
    Simple 'how good is this player for the next few weeks' score.

    Recent form matters most, season average stops us overreacting to one
    big haul, and easy fixtures (low difficulty) push the score up.

    TODO (your turn): tune these weights, or replace them with something
    better, e.g. use expected goals (xG) / expected assists (xA), minutes
    played, or the official 'ep_next' (expected points) field.
    """
    fixture_bonus = (5 - avg_difficulty)  # 0 (hard) .. 4 (easy)
    return round(0.5 * form + 0.3 * ppg + 0.8 * fixture_bonus, 2)


def build_players(bootstrap: dict, fixtures: list) -> list[Player]:
    teams = {t["id"]: t["name"] for t in bootstrap["teams"]}
    fixture_info = team_fixture_info(bootstrap, fixtures)

    players = []
    for e in bootstrap["elements"]:
        avg_diff, opponents = fixture_info.get(e["team"], (3.0, "-"))
        p = Player(
            id=e["id"],
            name=e["web_name"],
            team=teams[e["team"]],
            position=POSITIONS[e["element_type"]],
            price=e["now_cost"] / 10,          # API stores price in tenths: 105 -> £10.5m
            form=float(e["form"]),
            points_per_game=float(e["points_per_game"]),
            total_points=e["total_points"],
            selected_by=float(e["selected_by_percent"]),
            status=e["status"],
            avg_difficulty=avg_diff,
            next_opponents=opponents,
        )
        p.score = score_player(p.form, p.points_per_game, p.avg_difficulty)
        p.value = round(p.score / p.price, 3) if p.price else 0.0
        players.append(p)
    return players


def top_picks(players: list[Player], position: str | None = None,
              max_price: float | None = None, limit: int = 20,
              sort_by: str = "score") -> list[Player]:
    """Best available players, optionally filtered by position and budget."""
    pool = [p for p in players if p.status == "a"]
    if position:
        pool = [p for p in pool if p.position == position]
    if max_price is not None:
        pool = [p for p in pool if p.price <= max_price]
    return sorted(pool, key=lambda p: getattr(p, sort_by), reverse=True)[:limit]


def differentials(players: list[Player], max_ownership: float = 10.0, limit: int = 10) -> list[Player]:
    """Good players that few managers own - helps you climb ranks."""
    pool = [p for p in players if p.status == "a" and p.selected_by <= max_ownership]
    return sorted(pool, key=lambda p: p.score, reverse=True)[:limit]


def transfer_suggestions(players: list[Player], my_player_ids: list[int],
                         bank: float = 0.0, limit: int = 5) -> list[dict]:
    """
    For each player in your squad, find the best same-position replacement
    you can afford (his price + money in the bank) that isn't already in your squad.
    Returns the biggest upgrades first.

    TODO (your turn): account for the -4 points hit for extra transfers,
    and the 3-players-per-club rule.
    """
    by_id = {p.id: p for p in players}
    mine = [by_id[i] for i in my_player_ids if i in by_id]
    owned = set(my_player_ids)

    suggestions = []
    for out in mine:
        budget = out.price + bank
        options = [p for p in players
                   if p.position == out.position and p.status == "a"
                   and p.id not in owned and p.price <= budget]
        if not options:
            continue
        best = max(options, key=lambda p: p.score)
        gain = round(best.score - out.score, 2)
        if gain > 0:
            suggestions.append({"out": out, "in": best, "gain": gain})
    return sorted(suggestions, key=lambda s: s["gain"], reverse=True)[:limit]
