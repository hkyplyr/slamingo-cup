from sqlalchemy import and_
from sqlalchemy.orm import aliased

from slamingo_cup.models import Matchup, Team, WeeklyResult, db_session

session = db_session()


def get_matchups(week):
    winner_team = aliased(Team)
    loser_team = aliased(Team)
    winner_results = aliased(WeeklyResult)
    loser_results = aliased(WeeklyResult)

    results = (
        session.query(
            winner_team.name.label("winner_name"),
            winner_results.pf.label("winner_pf"),
            loser_team.name.label("loser_name"),
            loser_results.pf.label("loser_pf"),
        )
        .select_from(Matchup)
        .join(winner_team, Matchup.winner_team == winner_team.id)
        .join(loser_team, Matchup.loser_team == loser_team.id)
        .join(
            winner_results,
            and_(
                winner_team.id == winner_results.team_id,
                Matchup.week == winner_results.week,
            ),
        )
        .join(
            loser_results,
            and_(
                loser_team.id == loser_results.team_id,
                Matchup.week == loser_results.week,
            ),
        )
        .filter(Matchup.week == week)
        .order_by((winner_results.pf + loser_results.pf).desc())
    )

    return results
