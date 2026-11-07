"""Run with:  python -m pytest   (from the project folder)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import analysis  # noqa: E402


def make_player(pid, pos="MID", price=6.0, form=5.0, status="a", owned=5.0, score=None):
    p = analysis.Player(id=pid, name=f"P{pid}", team="Team", position=pos, price=price,
                        form=form, points_per_game=4.0, total_points=40, selected_by=owned,
                        status=status, avg_difficulty=3.0, next_opponents="-")
    p.score = score if score is not None else analysis.score_player(form, 4.0, 3.0)
    return p


def test_easier_fixtures_give_higher_score():
    assert analysis.score_player(5, 4, 2.0) > analysis.score_player(5, 4, 4.5)


def test_top_picks_skips_injured_and_respects_budget():
    players = [make_player(1, form=9, status="i"), make_player(2, price=12.0, form=8),
               make_player(3, form=6)]
    picks = analysis.top_picks(players, max_price=8.0)
    assert [p.id for p in picks] == [3]


def test_transfer_suggests_affordable_upgrade_in_same_position():
    players = [make_player(1, price=6.0, score=3), make_player(2, price=6.5, score=8),
               make_player(3, price=10.0, score=12), make_player(4, pos="FWD", price=5.0, score=20)]
    result = analysis.transfer_suggestions(players, my_player_ids=[1], bank=0.5)
    assert result[0]["in"].id == 2
    assert result[0]["gain"] == 5
