"""
app.py - The website. Run with:  python app.py   then open http://127.0.0.1:5000
"""
from flask import Flask, render_template, request

import analysis
import fpl_api

app = Flask(__name__)


def load_players():
    bootstrap = fpl_api.get_bootstrap()
    fixtures = fpl_api.get_fixtures()
    return bootstrap, analysis.build_players(bootstrap, fixtures)


@app.route("/")
def home():
    bootstrap, players = load_players()
    gw = analysis.current_gameweek(bootstrap)
    best_by_position = {pos: analysis.top_picks(players, position=pos, limit=3)
                        for pos in ["GK", "DEF", "MID", "FWD"]}
    return render_template("index.html", gw=gw,
                           best_by_position=best_by_position,
                           differentials=analysis.differentials(players, limit=5))


@app.route("/players")
def players_page():
    _, players = load_players()
    position = request.args.get("position") or None
    max_price = request.args.get("max_price", type=float)
    sort_by = request.args.get("sort", "score")
    if sort_by not in {"score", "value", "form", "total_points"}:
        sort_by = "score"
    picks = analysis.top_picks(players, position, max_price, limit=50, sort_by=sort_by)
    return render_template("players.html", players=picks, position=position,
                           max_price=max_price, sort_by=sort_by)


@app.route("/transfers", methods=["GET", "POST"])
def transfers_page():
    _, players = load_players()
    suggestions, error = None, None
    if request.method == "POST":
        try:
            ids = [int(x) for x in request.form["ids"].replace(" ", "").split(",") if x]
            bank = float(request.form.get("bank") or 0)
            suggestions = analysis.transfer_suggestions(players, ids, bank)
        except ValueError:
            error = "Enter player IDs as numbers separated by commas, e.g. 1, 5, 12"
    all_players = sorted(players, key=lambda p: (p.position, p.name))
    return render_template("transfers.html", suggestions=suggestions,
                           error=error, all_players=all_players)


if __name__ == "__main__":
    app.run(debug=True)
