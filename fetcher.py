import argparse
import json
from pathlib import Path

import requests

APP_API_URL = "https://api.sleeper.app/v1"
COM_API_URL = "https://api.sleeper.com"

REQUEST_TIMEOUT = 10

_session = requests.Session()


def get_weekly_results(league_id, season, week):
    league_info = _get_league_info(league_id)
    managers = _get_managers(league_id)

    matchups = {}
    for matchup in _get_matchups(league_id, week):
        if matchup["matchup_id"] in matchups:
            matchups[matchup["matchup_id"]].append(matchup)
        else:
            matchups[matchup["matchup_id"]] = [matchup]

    weekly_results = []
    for matchup_id, opponents in matchups.items():
        if matchup_id is None:
            continue

        for a, b in [[opponents[0], opponents[1]], [opponents[1], opponents[0]]]:
            weekly_results.append(
                {
                    "season": season,
                    "week": week,
                    "points_for": a["points"],
                    "playoffs": int(
                        week >= league_info["settings"]["playoff_week_start"]
                    ),
                    # TODO - add consolation logic
                    "consolation": int(False),
                    "result": _result(a, b),
                    "opponent": managers[b["roster_id"]],
                    "manager": managers[a["roster_id"]],
                }
            )

    _save(weekly_results, season, week, "weekly_results")


def _result(opponent_one, opponent_two):
    if opponent_one["points"] > opponent_two["points"]:
        return "W"
    elif opponent_one["points"] < opponent_two["points"]:
        return "L"
    else:
        return "T"


def get_player_stats(season, week):
    player_stats = _get_statistics(season, week)
    _save(player_stats, season, week, "player_stats")


def get_selected_positions(league_id, season, week):
    managers = _get_managers(league_id)
    league_info = _get_league_info(league_id)

    selected_positions = []
    for matchup in _get_matchups(league_id, week):
        manager_name = managers[matchup["roster_id"]]
        starter_positions = {
            starter_id: league_info["roster_positions"][idx]
            for idx, starter_id in enumerate(matchup["starters"])
        }

        for player_id in matchup["players"]:
            selected_positions.append(
                {
                    "season": season,
                    "week": week,
                    "position": starter_positions.get(player_id, "BN"),
                    "sleeper_id": player_id,
                    "manager": manager_name,
                }
            )

    _save(selected_positions, season, week, "selected_positions")


def _get_league_info(league_id):
    return _get(APP_API_URL, f"/league/{league_id}")


def _get_managers(league_id):
    roster_to_user = {
        e["owner_id"]: e["roster_id"]
        for e in _get(APP_API_URL, f"/league/{league_id}/rosters")
    }

    return {
        roster_to_user[e["user_id"]]: _translate(e["display_name"])
        for e in _get(APP_API_URL, f"/league/{league_id}/users")
    }


def _get_matchups(league_id, week):
    return _get(APP_API_URL, f"/league/{league_id}/matchups/{week}")


def _get_statistics(season, week):
    return [
        {
            "season": int(entry["season"]),
            "week": entry["week"],
            "pass_yards": int(entry["stats"].get("pass_yd", 0)),
            "pass_touchdowns": int(entry["stats"].get("pass_td", 0)),
            "pass_interceptions": int(entry["stats"].get("pass_int", 0)),
            "rush_yards": int(entry["stats"].get("rush_yd", 0)),
            "rush_touchdowns": int(entry["stats"].get("rush_td", 0)),
            "receptions": int(entry["stats"].get("rec", 0)),
            "rec_yards": int(entry["stats"].get("rec_yd", 0)),
            "rec_touchdowns": int(entry["stats"].get("rec_td", 0)),
            "fumbles_lost": int(entry["stats"].get("fum_lost", 0)),
            "two_point_conversions": int(
                entry["stats"].get("pass_2pt", 0)
                + entry["stats"].get("rush_2pt", 0)
                + entry["stats"].get("rec_2pt", 0)
            ),
            "sleeper_id": entry["player_id"],
        }
        for entry in _get(
            COM_API_URL, f"/stats/nfl/{season}/{week}?season_type=regular"
        )
    ]


MANAGER_NAMES = {
    "bettyg": "Betty",
    "HalfricanCaptain": "Chance",
    "cziemer13": "Clint",
    "NoctisZi": "Coulton",
    "erichogan8": "Eric",
    "EthanPlaysSports": "Ethan",
    "hoagie14": "Hogan",
    "jpagee": "Jason",
    "jsgwop": "Joe",
    "KeeganZiemer": "Keegan",
    "MMacLeod17": "Mason",
    "mgaron13": "Mel",
    "VonSchweetzz": "Mitch",
    "hkyplyr": "Travis",
}


def _translate(manager_name):
    return MANAGER_NAMES.get(manager_name, manager_name)


def _get(base_url, endpoint):
    response = _session.get(base_url + endpoint, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def _save(data, season, week, filename):
    path = Path(f"archive/{season}/{week}/{filename}.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--season", type=int)
    parser.add_argument("-w", "--week", type=int)
    parser.add_argument("-l", "--league_id")

    args = parser.parse_args()

    get_player_stats(args.season, args.week)
    get_selected_positions(args.league_id, args.season, args.week)
    get_weekly_results(args.league_id, args.season, args.week)
