from sqlalchemy import literal

from slamingo_cup.models import Player, Team, db_session
from slamingo_cup.tools import Formatting

session = db_session()


def highest_scoring_starter(week, position):
    return (
        session.query(
            Player.name.label("player_name"),
            Player.image_url.label("player_image"),
            Player.points,
            Team.name.label("team_name"),
            Team.image_url.label("team_image"),
            literal(f"Best Starting {position}").label("label"),
        )
        .join(Team, Team.id == Player.team_id)
        .filter(Player.week == week)
        .filter(Player.positions.like(f"%{position}%"))
        .filter(Player.started)
        .order_by(Player.points.desc())
        .limit(1)
        .one()
    )


def lowest_scoring_starter(week, position):
    return (
        session.query(
            Player.name.label("player_name"),
            Player.image_url.label("player_image"),
            Player.points,
            Team.name.label("team_name"),
            Team.image_url.label("team_image"),
            literal(f"Worst Starting {position}").label("label"),
        )
        .join(Team, Team.id == Player.team_id)
        .filter(Player.week == week)
        .filter(Player.positions.like(f"%{position}%"))
        .filter(Player.started)
        .order_by(Player.points.asc())
        .limit(1)
        .one()
    )


def highest_scoring_bench(week, position):
    return (
        session.query(
            Player.name.label("player_name"),
            Player.image_url.label("player_image"),
            Player.points,
            Team.name.label("team_name"),
            Team.image_url.label("team_image"),
            literal(f"Best Benched {position}").label("label"),
        )
        .join(Team, Team.id == Player.team_id)
        .filter(Player.week == week)
        .filter(Player.positions.like(f"%{position}%"))
        .filter(not Player.started)
        .order_by(Player.points.desc())
        .limit(1)
        .one()
    )


def build_row(data):
    return {
        "player_name": data.player_name,
        "player_image": data.player_image,
        "team_name": data.team_name,
        "team_image": data.team_image,
        "points": Formatting.format_points(data.points),
        "award_name": data.label,
    }


def get_player_awards(week):
    awards = [
        highest_scoring_starter(week, "QB"),
        highest_scoring_starter(week, "RB"),
        highest_scoring_starter(week, "WR"),
        highest_scoring_starter(week, "TE"),
        lowest_scoring_starter(week, "QB"),
        lowest_scoring_starter(week, "RB"),
        lowest_scoring_starter(week, "WR"),
        lowest_scoring_starter(week, "TE"),
        highest_scoring_bench(week, "QB"),
        highest_scoring_bench(week, "RB"),
        highest_scoring_bench(week, "WR"),
        highest_scoring_bench(week, "TE"),
    ]

    return [build_row(r) for r in awards]
