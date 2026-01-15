import json
import os

import requests

SLEEPER_APP_API = "https://api.sleeper.app/v1"
SLEEPER_COM_API = "https://api.sleeper.com/stats/nfl"
CACHE_DIRECTORY = ".cache"


def get_players():
    if __exists("players.json"):
        return __load("players.json")
    else:
        players = list(requests.get(f"{SLEEPER_APP_API}/players/nfl").json().values())
        return __save("players.json", players)


def get_statistics(season, week):
    filename = f"stats/{season}/{week}.json"
    if __exists(filename):
        return __load(filename)
    else:
        params = {
            "position[]": ["QB", "RB", "WR", "TE", "DEF", "K"],
            "season_type": "regular",
            "order_by": "pts_half_ppr",
        }
        stats = requests.get(f"{SLEEPER_COM_API}/{season}/{week}", params=params).json()
        return __save(filename, stats)


def __exists(filename):
    return os.path.exists(f"{CACHE_DIRECTORY}/{filename}")


def __load(filename):
    with open(f"{CACHE_DIRECTORY}/{filename}", "r") as f:
        return json.load(f)


def __save(filename, data):
    os.makedirs(os.path.dirname(f"{CACHE_DIRECTORY}/{filename}"), exist_ok=True)
    with open(f"{CACHE_DIRECTORY}/{filename}", "w") as f:
        json.dump(data, f)
        return data
