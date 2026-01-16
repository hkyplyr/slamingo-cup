import json
import os

import requests

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
