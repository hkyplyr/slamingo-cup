from sqlalchemy import func

from slamingo_cup.models import Player, Team, db_session

session = db_session()


def get_positional_points(position):
    return (
        session.query(Team.name, func.sum(Player.points))
        .join(Player, Player.team_id == Team.id)
        .filter(Player.started)
        .filter(Player.positions.like(f"%{position}%"))
        .group_by(Team.name)
        .order_by(Team.name)
        .all()
    )
