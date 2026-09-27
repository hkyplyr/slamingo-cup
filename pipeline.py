import os
import sys

import requests

from fetcher import get_player_stats, get_selected_positions, get_weekly_results
from generate import generate_all
from populate import build_database

LEAGUE_ID = "..."  # TODO: move to an env var / GH Actions secret


def resolve_season_and_week():
    response = requests.get("https://api.sleeper.app/v1/state/nfl")
    response.raise_for_status()
    return int(response.json()["season"]), response.json()["week"] - 1


def main():
    league_id = os.getenv("SLAMINGO_CUP_LEAGUE_ID")
    season, week = resolve_season_and_week()

    print(f"Fetching season {season}, week {week}...")
    get_player_stats(season, week)
    get_selected_positions(league_id, season, week)
    get_weekly_results(league_id, season, week)

    print()
    build_database()

    print()
    generate_all()


if __name__ == "__main__":
    sys.exit(main())
