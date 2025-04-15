import os
import pickle

import requests
from models import WeeklyResult
from yfantasy_api import YahooFantasyApi

yahoo_leagues = [
    ("399", "903720"),  # 2020
    ("406", "87025"),  # 2021
    ("414", "752449"),  # 2022
    ("423", "292234"),  # 2023
]

sleeper_leagues = [1135061048144519168]  # 2024


def build_weeks_param(api):
    total_weeks = api.league().get().end_week
    weeks = [str(w) for w in range(1, total_weeks + 1)]
    return ",".join(weeks)


def manager(team):
    raw_name = team.managers[0].name.split(" ")
    if len(raw_name) == 1:
        return yahoo_manager(raw_name[0].capitalize())
    else:
        first_name = raw_name[0].capitalize()
        last_initial = raw_name[1].capitalize()[0]
        return yahoo_manager(f"{first_name} {last_initial}.")


def yahoo_weekly_result(team_idx, matchup, league):
    team = matchup.teams[team_idx]
    opponent = matchup.teams[abs(team_idx - 1)]

    return WeeklyResult(
        {
            "season": league.season,
            "week": matchup.week,
            "team": manager(team),
            "opponent": manager(opponent),
            "points_for": team.points,
            "points_against": opponent.points,
            "projected_points_for": team.projected_points,
            "projected_points_against": opponent.projected_points,
            "win": hasattr(matchup, "winning_team")
            and matchup.winning_team.key == team.key,
            "tie": matchup.is_tied,
            "playoffs": matchup.is_playoffs,
            "consolation": matchup.is_consolation,
        }
    )


def fetch_all_matchups():
    weekly_results = []
    for game_id, league_id in yahoo_leagues:
        print(f"Loading matchups for {game_id}.l.{league_id}")
        api = YahooFantasyApi(league_id, game_id)
        weeks_param = build_weeks_param(api)

        league = api.league().scoreboard(week=weeks_param).get()
        for matchup in league.matchups:
            weekly_results.append(yahoo_weekly_result(0, matchup, league))
            weekly_results.append(yahoo_weekly_result(1, matchup, league))

    for league_id in sleeper_leagues:
        print(f"Loading matchups for {league_id}")
        league_data = requests.get(
            f"https://api.sleeper.app/v1/league/{league_id}"
        ).json()
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
        playoffs_start = league_data["settings"]["playoff_week_start"]
        for week in range(start_week, end_week + 1):
            matchups = requests.get(
                f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
            ).json()
            weekly_matchups = {}
            for entry in matchups:
                team = user_to_name[entry["roster_id"]]
                matchup_id = entry["matchup_id"]
                points = entry["points"]

                if matchup_id not in weekly_matchups:
                    weekly_matchups[matchup_id] = []

                weekly_matchups[matchup_id].append(
                    {
                        "season": season,
                        "week": week,
                        "team": team,
                        "points": points,
                        "playoffs": week >= playoffs_start,
                    }
                )

            for matchup in weekly_matchups.values():
                weekly_results.append(sleeper_weekly_result(0, matchup))
                weekly_results.append(sleeper_weekly_result(1, matchup))

    return weekly_results


def get_or_load_weekly_results(output=False):
    if os.path.exists("weekly_results.pkl"):
        with open("weekly_results.pkl", "rb") as f:
            weekly_results = pickle.load(f)
    else:
        weekly_results = fetch_all_matchups()
        with open("weekly_results.pkl", "wb") as f:
            pickle.dump(weekly_results, f)

    if output:
        for entry in weekly_results:
            if not entry.win:
                continue

            fields = [
                str(entry.season),
                str(entry.week),
                "",
                "",
                str(entry.playoffs),
                "",
                "",
                "",
                str(entry.team),
                str(entry.points_for),
                str(entry.projected_points_for),
                "",
                "",
                str(entry.opponent),
                str(entry.points_against),
                str(entry.projected_points_against),
                str(entry.points_for - entry.points_against),
            ]

            print(",".join(fields))

    return weekly_results


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


def active_manager(name):
    return name in [
        "Travis",
        "Mike",
        "Mason",
        "Keegan",
        "Ethan",
        "Coulton",
        "Mitch",
        "Chance",
        "Jason",
        "Joe",
        "Mel",
        "Betty",
    ]


def yahoo_manager(name):
    if name == "Mitchell":
        return "Mitch"
    return name


def sleeper_weekly_result(team_idx, matchup):
    team_data = matchup[team_idx]
    opponent_data = matchup[abs(team_idx - 1)]

    points_for = team_data["points"]
    points_against = opponent_data["points"]

    return WeeklyResult(
        {
            "season": team_data["season"],
            "week": team_data["week"],
            "team": team_data["team"],
            "opponent": opponent_data["team"],
            "points_for": points_for,
            "points_against": points_against,
            "projected_points_for": None,
            "projected_points_against": None,
            "win": points_for > points_against,
            "tie": points_for == points_against,
            "playoffs": team_data["playoffs"],
            "consolation": False,
        }
    )


if __name__ == "__main__":
    get_or_load_weekly_results()
