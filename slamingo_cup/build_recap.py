import json
import os
import sys

from yfantasy_api.api import YahooFantasyApi
from database import Database

db = Database()
api = YahooFantasyApi(87025, "nfl")


def get_last_matchups(week):
    return [
        f"<strong>{m.winner_name} ({m.winner_pf})</strong> beat "
        + f"<strong>{m.loser_name} ({m.loser_pf})</strong>"
        for m in db.get_matchups(week)
    ]


def get_next_matchups(week):
    records = {
        t.name: {"w": t.wins, "record": t.record} for t in db.get_standings(week)
    }

    previews = []
    matchups = api.league().scoreboard(week=week + 1).get().matchups

    for m in matchups:
        matchup_info = []
        combined_wins = 0
        for team in m.teams:
            combined_wins += records[team.name]["w"]
            matchup_info.append(team.name)
            matchup_info.append(records[team.name]["record"])
        matchup_info.append(combined_wins)
        previews.append(matchup_info)
    previews = sorted(previews, key=lambda x: x[4], reverse=True)

    return [
        f"<strong>{row[0]} {row[1]}</strong> vs. <strong>{row[2]} {row[3]}</strong>"
        for row in previews
    ]


def build_recap(week):
    file_path = f"slamingo_cup/recaps/week-{week}-recap.json"
    if os.path.exists(file_path):
        return

    recap = {"recaps": get_last_matchups(week), "previews": get_next_matchups(week)}

    with open(file_path, "w") as f:
        json.dump(recap, f, indent=4)

    return recap


if __name__ == "__main__":
    build_recap(int(sys.argv[1]))
