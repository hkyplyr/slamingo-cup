from slamingo_cup.models import Team, WeeklyResult, db_session

session = db_session()


def get_rolling_points(week):
    return (
        session.query(Team.name, WeeklyResult.pf)
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .filter(WeeklyResult.week == week)
        .group_by(Team.name)
        .all()
    )
