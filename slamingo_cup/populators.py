import client
import peewee
from database import db, insert_all
from helpers import (
    all_managers,
    get_in,
    inclusive_range,
    is_active,
    sleeper_leagues,
    sleeper_manager,
    yahoo_leagues,
    yahoo_manager,
)
from models import (
    AllPlay,
    Manager,
    Player,
    PlayerStarted,
    PlayerStatistics,
    WeeklyResult,
)
from thefuzz import fuzz

SEASONS = inclusive_range(2020, 2025)
WEEKS = inclusive_range(1, 18)


def run():
    __populate_managers()
    __populate_players()
    __populate_statistics()
    __populate_started_sleeper_players()
    __populate_started_yahoo_players()
    __populate_sleeper_matchups()
    __populate_yahoo_matchups()
    __populate_all_play_records()


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


def __populate_started_yahoo_players():
    started_players_data = []
    for season, game_id, league_id in yahoo_leagues():
        league = client.get_yahoo_league_teams(league_id=league_id, game_id=game_id)
        for team_id in inclusive_range(1, league.num_teams):
            for week in inclusive_range(1, league.end_week):
                team = client.get_yahoo_team_roster(
                    league_id=league_id, game_id=game_id, team_id=team_id, week=week
                )
                for yahoo_player in team.players:
                    player = __get_player(yahoo_player)
                    if player is None:
                        continue

                    manager = Manager.get(
                        Manager.name == yahoo_manager(team.managers[0].name)
                    )

                    started = yahoo_player.selected_position not in ["BN", "IR", "IR+"]
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


def __get_player(yahoo_player):
    player = None
    try:
        if yahoo_player.position == "DEF":
            player = Player.get_by_id(yahoo_player.pro_team)
            player.yahoo_id = yahoo_player.id
            player.save()
        else:
            player = Player.get(Player.yahoo_id == yahoo_player.id)
    except peewee.DoesNotExist:
        try:
            player = Player.get(Player.name == yahoo_player.name)
            player.yahoo_id = yahoo_player.id
            player.save()
        except peewee.DoesNotExist:
            players = Player.select().where(
                Player.yahoo_id is None,
                Player.positions == yahoo_player.position,
                Player.pro_team == yahoo_player.pro_team,
            )
            players_with_score = [
                (p, fuzz.ratio(yahoo_player.name, p.name)) for p in players
            ]
            player, score = sorted(players_with_score, key=lambda x: -x[1])[0]

            if score < 65:
                print(score, yahoo_player.name, player)
            else:
                player.yahoo_id = yahoo_player.id
                player.save()

    return player


def __populate_yahoo_matchups():
    for season, game_id, league_id in yahoo_leagues():
        league = client.get_yahoo_league_teams(league_id=league_id, game_id=game_id)

        for matchup in client.get_yahoo_matchups(
            league_id=league_id,
            game_id=game_id,
            weeks=inclusive_range(1, league.end_week),
        ).matchups:
            week = matchup.week
            manager_one = Manager.get(
                Manager.name == yahoo_manager(matchup.teams[0].managers[0].name)
            )
            manager_two = Manager.get(
                Manager.name == yahoo_manager(matchup.teams[1].managers[0].name)
            )

            result_one = {
                "id": int(
                    f"{season}{str(week).zfill(4)}{str(manager_one.id).zfill(4)}"
                ),
                "season": season,
                "week": week,
                "manager": manager_one,
                "points_for": matchup.teams[0].points,
                "playoffs": matchup.is_playoffs,
                "consolation": False,  # TODO - fix consolation calculation,
                "result": None,
                "opponent": None,
            }

            result_two = {
                "id": int(
                    f"{season}{str(week).zfill(4)}{str(manager_two.id).zfill(4)}"
                ),
                "season": season,
                "week": week,
                "manager": manager_two,
                "points_for": matchup.teams[1].points,
                "playoffs": matchup.is_playoffs,
                "consolation": False,  # TODO - fix consolation calculation,
                "result": None,
                "opponent": None,
            }

            if result_one["points_for"] > result_two["points_for"]:
                result_one["result"] = "W"
                result_two["result"] = "L"
            elif result_one["points_for"] < result_two["points_for"]:
                result_one["result"] = "L"
                result_two["result"] = "W"
            else:
                result_one["result"] = "T"
                result_two["result"] = "T"

            try:
                created_one = WeeklyResult.create(**result_one)
            except peewee.IntegrityError:
                created_one = WeeklyResult.get_by_id(result_one["id"])

            try:
                result_two["opponent"] = created_one
                created_two = WeeklyResult.create(**result_two)
            except peewee.IntegrityError:
                created_two = WeeklyResult.get_by_id(result_two["id"])

            created_one.opponent = created_two
            created_one.save()


def __populate_sleeper_matchups():
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
        playoffs_start_week = league_data["settings"]["playoff_week_start"]

        for week in inclusive_range(start_week, end_week):
            weekly_matchups = {}
            for matchup in client.get_sleeper_matchups(league_id=league_id, week=week):
                manager_name = user_to_name[matchup["roster_id"]]
                manager = Manager.get(Manager.name == manager_name)

                matchup_id = matchup["matchup_id"]
                points = matchup["points"]

                if matchup_id is None:
                    continue

                if matchup_id not in weekly_matchups:
                    weekly_matchups[matchup_id] = []

                weekly_matchups[matchup_id].append(
                    {
                        "id": int(
                            f"{season}{str(week).zfill(4)}{str(manager.id).zfill(4)}"
                        ),
                        "season": season,
                        "week": week,
                        "manager": manager,
                        "points_for": points,
                        "playoffs": week >= playoffs_start_week,
                        "consolation": False,  # TODO - fix consolation calculation,
                        "result": None,
                        "opponent": None,
                    }
                )

            for result_one, result_two in weekly_matchups.values():
                if result_one["points_for"] > result_two["points_for"]:
                    result_one["result"] = "W"
                    result_two["result"] = "L"
                elif result_one["points_for"] < result_two["points_for"]:
                    result_one["result"] = "L"
                    result_two["result"] = "W"
                else:
                    result_one["result"] = "T"
                    result_two["result"] = "T"

                try:
                    created_one = WeeklyResult.create(**result_one)
                except peewee.IntegrityError:
                    created_one = WeeklyResult.get_by_id(result_one["id"])

                try:
                    result_two["opponent"] = created_one
                    created_two = WeeklyResult.create(**result_two)
                except peewee.IntegrityError:
                    created_two = WeeklyResult.get_by_id(result_two["id"])

                created_one.opponent = created_two
                created_one.save()


def __player_params(json):
    fantasy_positions = json["fantasy_positions"]

    return {
        "id": json["player_id"],
        "name": f"{json['first_name']} {json['last_name']}",
        "positions": None if not fantasy_positions else ",".join(fantasy_positions),
        "pro_team": json["team"],
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


def __populate_all_play_records():
    matchups = WeeklyResult.select(
        WeeklyResult.season,
        WeeklyResult.week,
        WeeklyResult.manager_id,
        peewee.fn.RANK()
        .over(
            order_by=[WeeklyResult.points_for],
            partition_by=[WeeklyResult.season, WeeklyResult.week],
        )
        .alias("rank"),
    ).where(WeeklyResult.playoffs == False)

    all_play_records = []
    matchup_groupings = {}
    for matchup in matchups:
        id = (matchup.season, matchup.week)
        if id not in matchup_groupings:
            matchup_groupings[id] = []

        matchup_groupings[id].append((matchup.manager, matchup.rank))

    for (season, week), entries in matchup_groupings.items():
        total_games = len(entries) - 1
        missing_ranks = set(inclusive_range(1, len(entries))) - set(
            [r for _, r in entries]
        )
        tied_rank = None if not missing_ranks else (missing_ranks.pop() - 1)

        for manager, rank in entries:
            wins = rank - 1
            ties = 1 if tied_rank == rank else 0
            losses = total_games - wins - ties

            all_play_records.append(
                {
                    "season": season,
                    "week": week,
                    "manager": manager,
                    "win": wins,
                    "tie": ties,
                    "loss": losses,
                }
            )
    insert_all(AllPlay, all_play_records)


def __manager_params(manager_id, name):
    return {"id": manager_id, "name": name, "active": is_active(name)}


if __name__ == "__main__":
    run()
