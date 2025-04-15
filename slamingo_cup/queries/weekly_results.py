from sqlalchemy import and_, func

from slamingo_cup.models import AllPlay, OptimalPoints, Team, WeeklyResult, db_session
from slamingo_cup.tools import Formatting

session = db_session()


def rank():
    return (
        func.row_number()
        .over(order_by=(wins().desc(), ties().desc(), points_for().desc()))
        .label("rank")
    )


def team_name():
    return Team.name.label("team_name")


def wins():
    return WeeklyResult.is_winner.label("is_winner")


def ties():
    return WeeklyResult.is_tied.label("is_tied")


def points_for():
    return WeeklyResult.pf.label("pf")


def coach_percentage(subquery):
    return (points_for() / subquery.c.points * 100).label("coach")


def optimal_points_for(subquery):
    return func.sum(subquery.c.points).label("opf")


def optimal_points_subquery():
    return (
        session.query(
            OptimalPoints.week,
            OptimalPoints.team_id,
            func.sum(OptimalPoints.points).label("points"),
        )
        .group_by(OptimalPoints.week, OptimalPoints.team_id)
        .subquery()
    )


def get_weekly_results(week):
    optimal_points = optimal_points_subquery()

    result = (
        session.query(
            rank(),
            team_name(),
            wins(),
            ties(),
            points_for(),
            optimal_points_for(optimal_points),
            coach_percentage(optimal_points),
        )
        .join(WeeklyResult, Team.id == WeeklyResult.team_id)
        .join(
            optimal_points,
            and_(
                optimal_points.c.team_id == Team.id,
                optimal_points.c.week == WeeklyResult.week,
            ),
        )
        .join(
            AllPlay, and_(AllPlay.team_id == Team.id, AllPlay.week == WeeklyResult.week)
        )
        .filter(WeeklyResult.week == week)
        .group_by(Team.name)
        .order_by(wins().desc(), ties().desc(), points_for().desc())
    )

    return [__build_standings_row(r) for r in result]


def __build_standings_row(r):
    if r.is_winner:
        result = "W"
    elif r.is_tied:
        result = "T"
    else:
        result = "L"

    return {
        "rank": r.rank,
        "name": r.team_name,
        "result": result,
        "pf": Formatting.format_points(r.pf),
        "opf": Formatting.format_points(r.opf),
        "coach": Formatting.format_percentage(r.coach),
    }
