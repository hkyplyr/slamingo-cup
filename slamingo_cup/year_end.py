import json

from yfantasy_api.api import YahooFantasyApi
from yfantasy_api.models.common import Team
from database import Database

db = Database()
api = YahooFantasyApi(87025, "nfl")


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

    for team, values in data.items():
        shares = []

        for a, b in zip(values, maximum.values()):
            share = round(a / b, 2)
            shares.append(share)
            if share < minimum:
                minimum = share

        print(team, shares)
    print(minimum)


def get_player_starts_and_points():
    data = {}
    for team_name, team_id in db.get_teams():
        players = {"QB": [], "RB": [], "WR": [], "TE": [], "K": [], "DEF": []}
        for player in db.get_played_players(team_id):
            players[player[1]].append(player)
        data[team_name] = players
    print(data)
    with open("test.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
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

    for team_name, breakdown in full_team_makeup.items():
        draft = breakdown.get("draft", 0)
        trade = breakdown.get("trade", 0)
        freeagent = breakdown.get("freeagents", 0)
        waiver = breakdown.get("waivers", 0)

        print(f'"{team_name}": [{draft}, {trade}, {freeagent}, {waiver}],')
