import argparse
import json
from pathlib import Path

import requests

APP_API_URL = "https://api.sleeper.app/v1"
COM_API_URL = "https://api.sleeper.com"


def get_weekly_results(league_id, season, week):
    league_info = __get_league_info(league_id)
    managers = __get_managers(league_id)

    matchups = {}
    for matchup in __get_matchups(league_id, week):
        if matchup["matchup_id"] in matchups:
            matchups[matchup["matchup_id"]].append(matchup)
        else:
            matchups[matchup["matchup_id"]] = [matchup]

    weekly_results = []
    for matchup_id, opponents in matchups.items():
        if matchup_id is None:
            continue

        result_one = {
            "season": season,
            "week": week,
            "points_for": opponents[0]["points"],
            "playoffs": int(week >= league_info["settings"]["playoff_week_start"]),
            "consolation": int(False),
            "result": __result(opponents[0], opponents[1]),
            "opponent": managers[opponents[1]["roster_id"]],
            "manager": managers[opponents[0]["roster_id"]],
        }

        result_two = {
            "season": season,
            "week": week,
            "points_for": opponents[1]["points"],
            "playoffs": int(week >= league_info["settings"]["playoff_week_start"]),
            "consolation": int(False),
            "result": __result(opponents[1], opponents[0]),
            "opponent": managers[opponents[0]["roster_id"]],
            "manager": managers[opponents[1]["roster_id"]],
        }

        weekly_results.extend([result_one, result_two])

    file_path = Path(f"archive/{season}/{week}/weekly_results.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(weekly_results, f, indent=2)


def __result(opponent_one, opponent_two):
    if opponent_one["points"] > opponent_two["points"]:
        return "W"
    elif opponent_one["points"] < opponent_two["points"]:
        return "L"
    else:
        return "T"


def get_player_stats(season, week):
    file_path = Path(f"archive/{season}/{week}/player_stats.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    results = __get_statistics(season, week)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def get_selected_positions(league_id, season, week):
    file_path = Path(f"archive/{season}/{week}/selected_positions.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    managers = __get_managers(league_id)
    league_info = __get_league_info(league_id)

    selected_positions = []
    for matchup in __get_matchups(league_id, week):
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

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(selected_positions, f, indent=2)


def __get_league_info(league_id):
    return __get(APP_API_URL, f"/league/{league_id}")


def __get_managers(league_id):
    roster_to_user = {
        e["owner_id"]: e["roster_id"]
        for e in __get(APP_API_URL, f"/league/{league_id}/rosters")
    }

    return {
        roster_to_user[e["user_id"]]: __translate(e["display_name"])
        for e in __get(APP_API_URL, f"/league/{league_id}/users")
    }


def __get_matchups(league_id, week):
    return __get(APP_API_URL, f"/league/{league_id}/matchups/{week}")


def __get_selected_positions(season, week):
    pass


def __get_statistics(season, week):
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
        for entry in __get(
            COM_API_URL, f"/stats/nfl/{season}/{week}?season_type=regular"
        )
    ]


def __translate(manager_name):
    if manager_name == "bettyg":
        return "Betty"
    if manager_name == "HalfricanCaptain":
        return "Chance"
    if manager_name == "cziemer13":
        return "Clint"
    if manager_name == "NoctisZi":
        return "Coulton"
    if manager_name == "erichogan8":
        return "Eric"
    if manager_name == "EthanPlaysSports":
        return "Ethan"
    if manager_name == "hoagie14":
        return "Hogan"
    if manager_name == "jpagee":
        return "Jason"
    if manager_name == "jsgwop":
        return "Joe"
    if manager_name == "KeeganZiemer":
        return "Keegan"
    if manager_name == "MMacLeod17":
        return "Mason"
    if manager_name == "mgaron13":
        return "Mel"
    if manager_name == "VonSchweetzz":
        return "Mitch"
    if manager_name == "hkyplyr":
        return "Travis"
    return manager_name


def __get(base_url, endpoint):
    return requests.get(base_url + endpoint).json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--season", type=int)
    parser.add_argument("-w", "--week", type=int)
    parser.add_argument("-l", "--league_id", type=int)

    args = parser.parse_args()

    get_player_stats(args.season, args.week)
    get_selected_positions(args.league_id, args.season, args.week)
    get_weekly_results(args.league_id, args.season, args.week)
