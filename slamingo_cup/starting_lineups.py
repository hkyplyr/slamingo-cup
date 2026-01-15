import json
import os
import pickle

import requests
from yfantasy_api import YahooFantasyApi

league_ids = {
    2020: ("399", "903720"),
    2021: ("406", "87025"),
    2022: ("414", "752449"),
    2023: ("423", "292234"),
}


yahoo_leagues = [
    ("399", "903720"),  # 2020
    ("406", "87025"),  # 2021
    ("414", "752449"),  # 2022
    ("423", "292234"),  # 2023
]

sleeper_leagues = [
    1135061048144519168,  # 2024
    1253952102217039872,  # 2025
]


def fetch_team_roster(season, week, team_id):
    game_id, league_id = league_ids.get(season)
    api = YahooFantasyApi(league_id, game_id)

    return api.team(team_id).roster(week=week).stats().get()


def get_or_load_weekly_team_rosters(season, week, team_id):
    filename = f"{season}/{week}/{team_id}.pkl"
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            team_roster = pickle.load(f)
    else:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        team_roster = fetch_team_roster(season, week, team_id)
        with open(filename, "wb") as f:
            pickle.dump(team_roster, f)

    return team_roster


def manager(team):
    raw_name = team.managers[0].name.split(" ")
    if len(raw_name) == 1:
        return yahoo_manager(raw_name[0].capitalize())
    else:
        first_name = raw_name[0].capitalize()
        last_initial = raw_name[1].capitalize()[0]
        return yahoo_manager(f"{first_name} {last_initial}.")


def yahoo_manager(name):
    if name == "Mitchell":
        return "Mitch"
    return name


def get_players():
    if os.path.exists("players.json"):
        with open("players.json", "r") as f:
            return json.load(f)
    else:
        players = requests.get(" https://api.sleeper.app/v1/players/nfl").json()
        with open("players.json", "w") as f:
            json.dump(players, f)
            return players


# for season in range(2021, 2023 + 1):
#    for week in range(1, 17 + 1):
#        for team_id in range(1, 12 + 1):
#            print(f"Getting roster for {season}/{week} for Team # {team_id}")
#            print(get_or_load_weekly_team_rosters(season, week, team_id))
#
# exit()


def sleeper_managers(display_name):
    if display_name == "hkyplyr":
        return "Travis"
    elif display_name == "hoagie14":
        return "Mike"
    elif display_name == "MMacLeod17":
        return "Mason"
    elif display_name == "KeeganZiemer":
        return "Keegan"
    elif display_name == "EthanPlaysSports":
        return "Ethan"
    elif display_name == "NoctisZi":
        return "Coulton"
    elif display_name == "VonSchweetzz":
        return "Mitch"
    elif display_name == "HalfricanCaptain":
        return "Chance"
    elif display_name == "jpagee":
        return "Jason"
    elif display_name == "jsgwop":
        return "Joe"
    elif display_name == "mgaron13":
        return "Mel"
    elif display_name == "mrgaron21":
        return "Betty"
    elif display_name == "cziemer13":
        return "Clint"
    elif display_name == "erichogan8":
        return "Eric"


players = get_players()

for game_id, league_id in yahoo_leagues:
    api = YahooFantasyApi(league_id, game_id)
    league = api.league().teams().get()

    for team_id in range(1, league.num_teams + 1):
        for week in range(1, league.end_week + 1):
            data = get_or_load_weekly_team_rosters(league.season, week, team_id)

            for player in data.players:
                started = player.selected_position not in ["BN", "IR"]
                print(
                    f"{manager(data)},{player.name},{started},{player.points},{league.season},{week}"
                )

for league_id in sleeper_leagues:
    league_data = requests.get(f"https://api.sleeper.app/v1/league/{league_id}").json()
    season = int(league_data["season"])
    rosters_data = requests.get(
        f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    ).json()
    roster_to_user = {d["owner_id"]: d["roster_id"] for d in rosters_data}
    users_data = requests.get(
        f"https://api.sleeper.app/v1/league/{league_id}/users"
    ).json()
    user_to_name = {
        roster_to_user[d["user_id"]]: sleeper_managers(d["display_name"])
        for d in users_data
    }
    start_week = league_data["settings"]["start_week"]
    end_week = league_data["settings"]["last_scored_leg"]
    for week in range(start_week, end_week + 1):
        matchups = requests.get(
            f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
        ).json()
        weekly_matchups = {}
        for entry in matchups:
            team = user_to_name[entry["roster_id"]]
            starters = entry["starters"]
            player_points = entry["players_points"]

            for player in entry["players"]:
                started = player in starters
                points = player_points.get(player, 0.0)
                player_name = (
                    f"{players[player]['first_name']} {players[player]['last_name']}"
                )
                print(f"{team},{player_name},{started},{points},{season},{week}")


exit()


for player in fetch_team_roster(2020, 1, 1).players:
    print(player.name, player.selected_position, player.points)

exit()
for game_id, league_id in yahoo_leagues:
    api = YahooFantasyApi(league_id, game_id)
    league = api.league().teams().get()

    for team in league.teams:
        roster = api.team(team.id).roster().stats().get().players
        for player in roster:
            print(player.name, player.selected_position, player.points)
    exit()

    team = api.team(1).roster().stats().get()
    print(league.__dict__)
    print(team.__dict__)
    exit()
