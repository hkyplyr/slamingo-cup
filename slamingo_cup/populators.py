import client
from database import insert_all
from helpers import (all_managers, get_in, inclusive_range, is_active,
                     sleeper_leagues, sleeper_manager)
from models import Manager, Player, PlayerStarted, PlayerStatistics

SEASONS = inclusive_range(2020, 2025)
WEEKS = inclusive_range(1, 18)


def run():
    __populate_managers()
    __populate_players()
    __populate_statistics()
    __populate_started_sleeper_players()


def __populate_managers():
    manager_data = [__manager_params(idx, m) for idx, m in enumerate(all_managers())]
    insert_all(Manager, manager_data)


def __populate_players():
    player_data = [__player_params(p) for p in client.get_players().values()]

    insert_all(Player, player_data)


def __populate_statistics():
    statistics_data = [
        __statistic_params(s, season, week)
        for season in SEASONS
        for week in WEEKS
        for s in client.get_statistics(season=season, week=week)
    ]

    insert_all(PlayerStatistics, statistics_data)


def __populate_started_sleeper_players():
    started_players_data = []
    for season, league_id in sleeper_leagues():
        league_data = client.get_sleeper_league(league_id=league_id)
        roster_to_user = {
            d["owner_id"]: d["roster_id"]
            for d in client.get_sleeper_rosters(league_id=league_id)
        }
        user_to_name = {
            roster_to_user[d["user_id"]]: sleeper_manager(d["display_name"])
            for d in client.get_sleeper_users(league_id=league_id)
        }

        start_week = league_data["settings"]["start_week"]
        end_week = league_data["settings"]["last_scored_leg"]

        for week in inclusive_range(start_week, end_week):
            for matchup in client.get_sleeper_matchups(league_id=league_id, week=week):
                manager_name = user_to_name[matchup["roster_id"]]
                manager = Manager.get(Manager.name == manager_name)

                for player_id in matchup["players"]:
                    started = player_id in matchup["starters"]
                    player = Player.get_by_id(player_id)
                    started_players_data.append(
                        {
                            "manager": manager,
                            "player": player,
                            "season": season,
                            "week": week,
                            "started": started,
                        }
                    )
    insert_all(PlayerStarted, started_players_data)


def __player_params(json):
    fantasy_positions = json["fantasy_positions"]

    return {
        "id": json["player_id"],
        "name": f"{json['first_name']} {json['last_name']}",
        "positions": None if not fantasy_positions else ",".join(fantasy_positions),
        "yahoo_id": None if not json.get("yahoo_id") else int(json.get("yahoo_id")),
    }


def __statistic_params(json, season, week):
    return {
        "player_id": json["player_id"],
        "season": season,
        "week": week,
        "pass_yards": int(get_in(json, ["stats", "pass_yd"], 0)),
        "pass_touchdowns": int(get_in(json, ["stats", "pass_td"], 0)),
        "pass_interceptions": int(get_in(json, ["stats", "pass_int"], 0)),
        "rush_yards": int(get_in(json, ["stats", "rush_yd"], 0)),
        "rush_touchdowns": int(get_in(json, ["stats", "rush_td"], 0)),
        "receptions": int(get_in(json, ["stats", "rec"], 0)),
        "rec_yards": int(get_in(json, ["stats", "rec_yd"], 0)),
        "rec_touchdowns": int(get_in(json, ["stats", "rec_td"], 0)),
        "fumbles": int(get_in(json, ["stats", "fum_lost"], 0)),
    }


def __manager_params(manager_id, name):
    return {"id": manager_id, "name": name, "active": is_active(name)}


if __name__ == "__main__":
    run()
