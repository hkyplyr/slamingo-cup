import json
import os

import requests

SLEEPER_URL = "https://api.sleeper.app/v1"


def get_players():
    if os.path.exists("players.json"):
        with open("players.json", "r") as f:
            return json.load(f)
    else:
        players = requests.get(f"{SLEEPER_URL}/players/nfl").json()
        with open("players.json", "w") as f:
            json.dump(players, f)
            return players
