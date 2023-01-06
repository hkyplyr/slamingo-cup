from sqlalchemy import and_, func, literal
from sqlalchemy.orm import aliased

from slamingo_cup.models import Matchup, OptimalPoints, Team, WeeklyResult, db_session
from slamingo_cup.tools import Formatting

session = db_session()


def highest_scorer(week):
    return (
        session.query(
            Team.name.label("team_one_name"),
            literal(None).label("team_two_name"),
            Team.image_url.label("team_one_image"),
            WeeklyResult.pf.label("points"),
            literal(None).label("percentage"),
            literal("Highest Scorer").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .filter(WeeklyResult.week == week)
        .order_by(WeeklyResult.pf.desc())
        .limit(1)
        .one()
    )


def lowest_scorer(week):
    return (
        session.query(
            Team.name.label("team_one_name"),
            literal(None).label("team_two_name"),
            Team.image_url.label("team_one_image"),
            WeeklyResult.pf.label("points"),
            literal(None).label("percentage"),
            literal("Lowest Scorer").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .filter(WeeklyResult.week == week)
        .order_by(WeeklyResult.pf.asc())
        .limit(1)
        .one()
    )


def biggest_blowout(week):
    winner = aliased(Team)
    loser = aliased(Team)

    return (
        session.query(
            winner.name.label("team_one_name"),
            loser.name.label("team_two_name"),
            winner.image_url.label("team_one_image"),
            Matchup.victory_margin.label("points"),
            literal(None).label("percentage"),
            literal("Biggest Blowout").label("label"),
        )
        .join(winner, Matchup.winner_team == winner.id)
        .join(loser, Matchup.loser_team == loser.id)
        .filter(Matchup.week == week)
        .order_by(Matchup.victory_margin.desc())
        .limit(1)
        .one()
    )


def closest_victory(week):
    winner = aliased(Team)
    loser = aliased(Team)

    return (
        session.query(
            winner.name.label("team_one_name"),
            loser.name.label("team_two_name"),
            winner.image_url.label("team_one_image"),
            Matchup.victory_margin.label("points"),
            literal(None).label("percentage"),
            literal("Closest Victory").label("label"),
        )
        .join(winner, Matchup.winner_team == winner.id)
        .join(loser, Matchup.loser_team == loser.id)
        .filter(Matchup.week == week)
        .order_by(Matchup.victory_margin.asc())
        .limit(1)
        .one()
    )


def overacheiving_team(week):
    return (
        session.query(
            Team.name.label("team_one_name"),
            literal(None).label("team_two_name"),
            Team.image_url.label("team_one_image"),
            literal(None).label("points"),
            (WeeklyResult.pf / WeeklyResult.ppf * 100).label("percentage"),
            literal("Overacheiving Team").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .filter(WeeklyResult.week == week)
        .order_by((WeeklyResult.pf / WeeklyResult.ppf * 100).desc())
        .limit(1)
        .one()
    )


def underacheiving_team(week):
    return (
        session.query(
            Team.name.label("team_one_name"),
            literal(None).label("team_two_name"),
            Team.image_url.label("team_one_image"),
            literal(None).label("points"),
            (WeeklyResult.pf / WeeklyResult.ppf * 100).label("percentage"),
            literal("Underacheiving Team").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .filter(WeeklyResult.week == week)
        .order_by((WeeklyResult.pf / WeeklyResult.ppf * 100).asc())
        .limit(1)
        .one()
    )


def best_coach(week):
    subquery = (
        session.query(
            OptimalPoints.team_id,
            OptimalPoints.week,
            func.sum(OptimalPoints.points).label("points"),
        )
        .group_by(OptimalPoints.team_id, OptimalPoints.week)
        .subquery()
    )

    return (
        session.query(
            Team.name.label("team_one_name"),
            literal(None).label("team_two_name"),
            Team.image_url.label("team_one_image"),
            literal(None).label("points"),
            (WeeklyResult.pf / subquery.c.points * 100).label("percentage"),
            literal("Best Coach").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .join(
            subquery,
            and_(subquery.c.team_id == Team.id, subquery.c.week == WeeklyResult.week),
        )
        .filter(WeeklyResult.week == week)
        .order_by((WeeklyResult.pf / subquery.c.points * 100).desc())
        .limit(1)
        .one()
    )


def worst_coach(week):
    subquery = (
        session.query(
            OptimalPoints.team_id,
            OptimalPoints.week,
            func.sum(OptimalPoints.points).label("points"),
        )
        .group_by(OptimalPoints.team_id, OptimalPoints.week)
        .subquery()
    )

    return (
        session.query(
            Team.name.label("team_one_name"),
            literal(None).label("team_two_name"),
            Team.image_url.label("team_one_image"),
            literal(None).label("points"),
            (WeeklyResult.pf / subquery.c.points * 100).label("percentage"),
            literal("Worst Coach").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .join(
            subquery,
            and_(subquery.c.team_id == Team.id, subquery.c.week == WeeklyResult.week),
        )
        .filter(WeeklyResult.week == week)
        .order_by((WeeklyResult.pf / subquery.c.points * 100).asc())
        .limit(1)
        .one()
    )


def build_row(data):
    if data.points != None:
        points = Formatting.format_points(data.points)
    else:
        points = None

    if data.percentage:
        percentage = Formatting.format_percentage(data.percentage)
    else:
        percentage = None

    return {
        "team_one_name": data.team_one_name,
        "team_one_image": data.team_one_image,
        "team_two_name": data.team_two_name,
        "points": points,
        "percentage": percentage,
        "award_name": data.label,
    }


def get_awards(week):
    awards = [
        biggest_blowout(week),
        closest_victory(week),
        highest_scorer(week),
        lowest_scorer(week),
        overacheiving_team(week),
        underacheiving_team(week),
        best_coach(week),
        worst_coach(week),
    ]

    return [build_row(r) for r in awards]
