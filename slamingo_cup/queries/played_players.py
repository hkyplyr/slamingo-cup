from sqlalchemy import and_, func, literal
from sqlalchemy.orm import aliased

from slamingo_cup.models import Player, Team, db_session
from slamingo_cup.tools import Formatting

session = db_session()

MAX_WEEK = 14


def get_players(team_id, position):
    return (
        session.query(
            Player.name,
            literal(position).label("position"),
            func.round(func.sum(Player.points), 2).label("points"),
            func.count(Player.id).label("starts"),
            func.round(func.sum(Player.points) / func.count(Player.id), 2).label("avg"),
        )
        .filter(Player.started)
        .filter(Player.team_id == team_id)
        .filter(Player.positions.like(f"%{position}%"))
        .filter(Player.week <= MAX_WEEK)
        .group_by(Player.name)
        .order_by(func.sum(Player.points).desc())
        .all()
    )


def build_row(data):
    return (data.name, data.position, data.points, data.starts, data.avg)


def get_played_players(team_id):
    players = (
        get_players(team_id, "QB")
        + get_players(team_id, "RB")
        + get_players(team_id, "WR")
        + get_players(team_id, "TE")
        + get_players(team_id, "K")
        + get_players(team_id, "DEF")
    )

    return [build_row(p) for p in players]
