import json

from yfantasy_api.api import YahooFantasyApi
from yfantasy_api.models.common import Team
from database import Database

db = Database()
api = YahooFantasyApi(752449, "nfl")


def get_positional_breakdowns():
    maximum = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "K": 0, "DEF": 0}
    data = {}
    positions = ["QB", "RB", "WR", "TE", "K", "DEF"]
    for position in positions:
        positional_points = db.get_positional_points(position)
        for team, points in positional_points:
            if team not in data:
                data[team] = [points]
            else:
                data[team].append(points)

            if points > maximum[position]:
                maximum[position] = points

    minimum = 1

    results = {}
    for team, values in data.items():
        shares = []

        for a, b in zip(values, maximum.values()):
            share = round(a / b, 2)
            shares.append(share)
            if share < minimum:
                minimum = share

        results[team] = shares

    return results


def get_player_starts_and_points():
    data = {}
    for team_name, team_id in db.get_teams():
        players = {"QB": [], "RB": [], "WR": [], "TE": [], "K": [], "DEF": []}
        for player in db.get_played_players(team_id):
            players[player[1]].append(player)
        data[team_name] = players
    return data


def get_rolling_points():
    weekly_results = {}
    for week in range(1, 15):
        results = db.get_weekly_results(week)
        if results == []:
            break
        print(results)

        for result in results:
            if result.name not in weekly_results:
                weekly_results[result.name] = []

            weekly_results[result.name].append(result.pf)
    averages = [
        average_points(value) for value in zip(*reversed(weekly_results.values()))
    ]

    results = {}
    for key, value in weekly_results.items():
        results[key] = value
    results["Average"] = averages
    return results


def average_points(points):
    total = sum([float(value) for value in points])
    return round(total / len(points), 2)


def format_win_percentage(win_percentage):
    if not win_percentage:
        return win_percentage

    return "{:.3f}".format(win_percentage)


def get_team_makeup():
    source_map = {}
    for draft_pick in api.league().draft_results().get().draft_results:
        source_map[draft_pick.player.id] = "draft"

    for transaction in api.league().transactions().get().transactions:
        if transaction.type in ["add", "add/drop"]:
            source_map[transaction.added_player.id] = transaction.source_type
        elif transaction.type in ["trade"]:
            for traded_player in transaction.traded_players:
                source_map[traded_player.id] = "trade"

    full_team_makeup = {}
    for team_name, team_id in db.get_teams():
        team_makeup = {}
        for player in api.team(team_id).roster().get().players:
            source = source_map[player.id]
            if source not in team_makeup:
                team_makeup[source] = 0
            team_makeup[source] += 1
        full_team_makeup[team_name] = team_makeup

    results = {}
    for team_name, breakdown in full_team_makeup.items():
        draft = breakdown.get("draft", 0)
        trade = breakdown.get("trade", 0)
        freeagent = breakdown.get("freeagents", 0)
        waiver = breakdown.get("waivers", 0)
        results[team_name] = [draft, trade, freeagent + waiver]
    return results


def get_results():
    all_play = {}

    for row in db.get_power_rankings(14):
        win, loss = row.record.replace("(", "").replace(")", "").split("-")

        win_percentage = round((int(win) / (int(win) + int(loss))), 3)
        win_percentage = "{:.3f}".format(win_percentage)

        all_play[row.name] = f"{win}-{loss} ({win_percentage})"

    results = {}
    for row in db.get_standings(14):
        win_percentage = round(
            (row.wins + (0.5 * row.ties)) / (row.wins + row.losses + row.ties), 3
        )
        win_percentage = "{:.3f}".format(win_percentage)

        results[row.name] = {
            "record": f"{row.record} ({win_percentage})",
            "all_play": all_play[row.name],
            "points_for": row.pf,
        }

    return results


if __name__ == "__main__":
    data = get_player_starts_and_points()

    with open("docs/data/positional.json", "w") as f:
        json.dump(data, f, indent=4)

    data = {
        "teams": get_positional_breakdowns(),
        "team_makeup": get_team_makeup(),
        "weekly_points": get_rolling_points(),
        "results": get_results(),
    }

    with open("docs/data/yearly.json", "w") as f:
        json.dump(data, f, indent=4)
