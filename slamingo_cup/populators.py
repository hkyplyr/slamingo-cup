import logging

import client
from database import db
from helpers import inclusive_range
from models import Player, PlayerStatistics

BATCH_SIZE = 1000
SEASONS = inclusive_range(2020, 2025)
WEEKS = inclusive_range(1, 18)


def run():
    for player in Player.select():
        for stats in player.statistics:
            print(stats)
    # __populate_players()
    # __populate_statistics()


def __populate_players():
    player_data = [__player_params(p) for p in client.get_players()]

    with db.atomic():
        for idx in range(0, len(player_data), BATCH_SIZE):
            logging.info(f"Upserting players from {idx}-{idx + BATCH_SIZE}")
            Player.insert_many(
                player_data[idx : idx + BATCH_SIZE]
            ).on_conflict_replace().execute()


def __player_params(json):
    fantasy_positions = json["fantasy_positions"]

    return {
        "id": json["player_id"],
        "name": f"{json['first_name']} {json['last_name']}",
        "positions": None if not fantasy_positions else ",".join(fantasy_positions),
        "yahoo_id": None if not json.get("yahoo_id") else int(json.get("yahoo_id")),
    }


def __populate_statistics():
    statistics_data = [
        __statistic_params(s, season, week)
        for season in SEASONS
        for week in WEEKS
        for s in client.get_statistics(season, week)
    ]

    with db.atomic():
        for idx in range(0, len(statistics_data), BATCH_SIZE):
            logging.info(f"Upserting statistics from {idx}-{idx + BATCH_SIZE}")
            PlayerStatistics.insert_many(
                statistics_data[idx : idx + BATCH_SIZE]
            ).on_conflict_replace().execute()


def __statistic_params(json, season, week):
    stats = json["stats"]
    return {
        "player_id": json["player_id"],
        "season": season,
        "week": week,
        "pass_yards": int(stats.get("pass_yd", 0)),
        "pass_touchdowns": int(stats.get("pass_td", 0)),
        "pass_interceptions": int(stats.get("pass_int", 0)),
        "rush_yards": int(stats.get("rush_yd", 0)),
        "rush_touchdowns": int(stats.get("rush_td", 0)),
        "receptions": int(stats.get("rec", 0)),
        "rec_yards": int(stats.get("rec_yd", 0)),
        "rec_touchdowns": int(stats.get("rec_td", 0)),
        "fumbles": int(stats.get("fum_lost", 0)),
    }


if __name__ == "__main__":
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
    run()
