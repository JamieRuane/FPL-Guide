# ⚽ FPL Guide

A web app that helps Fantasy Premier League managers pick players and plan transfers.
It uses live data from the official FPL API.

**Built with:** Python, Flask, Jinja2 templates, HTML/CSS, pytest

## Features
- **Gameweek picks:** the top players in each position, ranked by form, season average and upcoming fixture difficulty
- **Player finder:** filter by position and budget, and sort by score, value (score per £m), form or points
- **Differentials:** strong players that fewer than 10% of managers own
- **Transfer helper:** enter your squad and bank balance to see the best affordable upgrades

## Run it
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py          # open http://127.0.0.1:5000
python -m pytest       # run the tests
```
If the FPL API can't be reached, the app uses the made-up data in `sample_data/`.

## How the scoring works
`score = 0.5 × form + 0.3 × points-per-game + 0.8 × (5 − avg fixture difficulty over the next 3 games)`
The code is in `analysis.py`. It's deliberately simple, and improving it is the main goal of the roadmap below.

## Project structure
```
app.py          Flask routes (the web pages)
fpl_api.py      Gets and caches data from the FPL API
analysis.py     Scoring, rankings and transfer logic
templates/      HTML pages
static/         CSS
tests/          Unit tests
```

---

## Roadmap (do these yourself, one at a time)

**Level 1: Get comfortable**
1. Run it and read every file. Change the score weights and see how the rankings move.
2. Add a "Captain pick" box on the home page showing the single highest-scoring player.
3. Make the player names clickable, linking to a `/player/<id>` page with more detail.

**Level 2: Better football logic**
4. Use more of the API data: `expected_goals`, `expected_assists`, `minutes` and `ep_next` (all in `bootstrap-static`).
5. Penalise players who don't play every week (low minutes).
6. Transfer helper: apply the 3-players-per-club rule and the −4 points hit for extra transfers.
7. Load a real team by FPL **team ID** from `/api/entry/{team_id}/event/{gw}/picks/` so users don't need to type player IDs.

**Level 3: Make it impressive**
8. Add charts (Chart.js) showing a player's points per gameweek from `/api/element-summary/{id}/`.
9. Save data in a database (SQLite plus SQLAlchemy) instead of JSON files.
10. Build a "best XI under £100m" optimiser using the `pulp` library (linear programming). It's a great talking point in interviews.
11. Deploy it for free on Render, Railway or PythonAnywhere so you can share a live link.
12. Set up GitHub Actions to run the tests automatically on every push.

---

## Putting it on your CV and LinkedIn
- Push it to **GitHub** with commits that have clear messages, little and often (not one giant upload).
- Add a **screenshot or GIF** to the top of this README. People look at those first.
- **Deploy it** (step 11) and put the live link on your CV.
- CV line example: *"Built a Flask web app that analyses live Fantasy Premier League data to recommend transfers, using a custom player-scoring model, API caching and unit tests."*
- LinkedIn: write a short post with a screenshot, saying what you built, one thing that was hard and what you learned. FPL is popular, so these posts get engagement.
