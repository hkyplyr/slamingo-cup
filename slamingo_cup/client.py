import json
import os
import pickle

import requests
from yfantasy_api import YahooFantasyApi

SLEEPER_APP_API = "https://api.sleeper.app/v1"
SLEEPER_COM_API = "https://api.sleeper.com/stats/nfl"
CACHE_DIRECTORY = ".cache"


def cacheable(filename):
    def inner_cacheable(query_func):
        def maybe_cache_data(**kwargs):
            qualified_filename = f"{CACHE_DIRECTORY}/{filename.format(**kwargs)}"
            if os.path.exists(qualified_filename):
                with open(qualified_filename, "r") as f:
                    return json.load(f)
            else:
                os.makedirs(os.path.dirname(qualified_filename), exist_ok=True)
                data = query_func(**kwargs)
                with open(qualified_filename, "w") as f:
                    json.dump(data, f)
                return data

        return maybe_cache_data

    return inner_cacheable


def pickled(filename):
    def inner_pickled(query_func):
        def maybe_pickle_data(**kwargs):
            qualified_filename = f"{CACHE_DIRECTORY}/{filename.format(**kwargs)}"
            if os.path.exists(qualified_filename):
                with open(qualified_filename, "rb") as f:
                    return pickle.load(f)
            else:
                os.makedirs(os.path.dirname(qualified_filename), exist_ok=True)
                data = query_func(**kwargs)
                with open(qualified_filename, "wb") as f:
                    pickle.dump(data, f)
                return data

        return maybe_pickle_data

    return inner_pickled


@cacheable("players.json")
def get_players():
    return requests.get(f"{SLEEPER_APP_API}/players/nfl").json()


@cacheable("stats/{season}/{week}.json")
def get_statistics(season, week):
    params = {
        "position[]": ["QB", "RB", "WR", "TE", "DEF", "K"],
        "season_type": "regular",
        "order_by": "pts_half_ppr",
    }
    return requests.get(f"{SLEEPER_COM_API}/{season}/{week}", params=params).json()


@cacheable("matchups/sleeper/{league_id}/{week}.json")
def get_sleeper_matchups(league_id, week):
    return requests.get(f"{SLEEPER_APP_API}/league/{league_id}/matchups/{week}").json()


@cacheable("managers/sleeper/{league_id}/users.json")
def get_sleeper_users(league_id):
    return requests.get(f"{SLEEPER_APP_API}/league/{league_id}/users").json()


@cacheable("managers/sleeper/{league_id}/rosters.json")
def get_sleeper_rosters(league_id):
    return requests.get(f"{SLEEPER_APP_API}/league/{league_id}/rosters").json()


@cacheable("league_info/sleeper/{league_id}.json")
def get_sleeper_league(league_id):
    return requests.get(f"{SLEEPER_APP_API}/league/{league_id}").json()


@pickled("league_info/yahoo/{game_id}/{league_id}/teams.pkl")
def get_yahoo_league_teams(league_id, game_id):
    return YahooFantasyApi(league_id, game_id).league().teams().get()


@pickled("league_info/yahoo/{game_id}/{league_id}/{team_id}/{week}/roster.pkl")
def get_yahoo_team_roster(league_id, game_id, team_id, week):
    return YahooFantasyApi(league_id, game_id).team(team_id).roster(week=week).get()


@pickled("league_info/yahoo/{game_id}/{league_id}/matchups.pkl")
def get_yahoo_matchups(league_id, game_id, weeks):
    weeks = ",".join([str(w) for w in weeks])

    return YahooFantasyApi(league_id, game_id).league().scoreboard(week=weeks).get()
