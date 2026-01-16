import os
import pickle

from helpers import yahoo_manager
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
    return yahoo_manager(team.managers[0].name)


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
