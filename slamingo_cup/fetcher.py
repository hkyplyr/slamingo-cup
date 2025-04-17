import sys

from sqlalchemy import func
from yfantasy_api import YahooFantasyApi

from slamingo_cup.models import (
    AllPlay,
    Matchup,
    OptimalPoints,
    Player,
    Team,
    WeeklyResult,
    db_session,
)

session = db_session()


def all_play_wins():
    return (func.rank().over(order_by=WeeklyResult.pf.asc()) - 1).label("w")


def all_play_losses():
    return (func.rank().over(order_by=WeeklyResult.pf.desc()) - 1).label("l")


def update_all_play(week):
    result = (
        session.query(
            Team.id.label("team_id"),
            WeeklyResult.week,
            WeeklyResult.pf,
            all_play_wins(),
            all_play_losses(),
        )
        .join(WeeklyResult, Team.id == WeeklyResult.team_id)
        .filter(WeeklyResult.week == week)
    )

    for r in result:
        session.merge(
            AllPlay(team_id=r.team_id, week=r.week, all_win=r.w, all_loss=r.l)
        )
    session.commit()


def get_optimal_position(players, position, number_of_spots, used):
    players = filter(lambda player: player.id not in used, players)
    players = list(
        filter(lambda player: position in player.eligible_positions, players)
    )

    return [float(player.points) for player in players[:number_of_spots]], used + [
        player.id for player in players[:number_of_spots]
    ]


def get_rb_wr_te(players, used):
    rb, used = get_optimal_position(players, "RB", 2, used)
    wr, used = get_optimal_position(players, "WR", 2, used)
    te, used = get_optimal_position(players, "TE", 1, used)
    flx, used = get_optimal_position(players, "W/R/T", 1, used)
    return sum(rb) + sum(wr) + sum(te) + sum(flx)


def get_rb_te_wr(players, used):
    rb, used = get_optimal_position(players, "RB", 2, used)
    te, used = get_optimal_position(players, "TE", 1, used)
    wr, used = get_optimal_position(players, "WR", 2, used)
    flx, used = get_optimal_position(players, "W/R/T", 1, used)
    return sum(rb) + sum(wr) + sum(te) + sum(flx)


def get_wr_rb_te(players, used):
    wr, used = get_optimal_position(players, "WR", 2, used)
    rb, used = get_optimal_position(players, "RB", 2, used)
    te, used = get_optimal_position(players, "TE", 1, used)
    flx, used = get_optimal_position(players, "W/R/T", 1, used)
    return sum(rb) + sum(wr) + sum(te) + sum(flx)


def get_wr_te_rb(players, used):
    wr, used = get_optimal_position(players, "WR", 2, used)
    te, used = get_optimal_position(players, "TE", 1, used)
    rb, used = get_optimal_position(players, "RB", 2, used)
    flx, used = get_optimal_position(players, "W/R/T", 1, used)
    return sum(rb) + sum(wr) + sum(te) + sum(flx)


def get_sorted_players(api, team_id, week):
    players = api.team(team_id).roster(week=week).stats().get().players

    for player in players:
        session.merge(
            Player(
                id=player.id,
                team_id=team_id,
                week=week,
                name=player.name,
                image_url=player.image_url,
                positions=",".join(
                    [
                        pos
                        for pos in player.eligible_positions
                        if pos in ["QB", "RB", "WR", "TE", "DEF", "K"]
                    ]
                ),
                points=player.points,
                started=player.selected_position not in ["BN", "IR"],
            )
        )

    players = filter(lambda player: float(player.points) >= 0, players)
    players = sorted(players, key=lambda player: float(player.points), reverse=True)
    return list(players)


def get_last_updated_week():
    week = session.query(func.max(Player.week)).one()[0]
    return 1 if not week else week


def inclusive_range(start, end):
    return range(start, end + 1)


week = int(sys.argv[1])
api = YahooFantasyApi(292234, "nfl")

for i in inclusive_range(get_last_updated_week(), week):
    matchups = api.league().scoreboard(week=i).get().matchups

    for matchup in matchups:
        if matchup.is_tied:
            for team in matchup.teams:
                session.merge(
                    Team(id=team.id, name=team.name, image_url=team.team_logos)
                )

                session.merge(
                    WeeklyResult(
                        team_id=team.id,
                        week=i,
                        is_winner=False,
                        is_tied=True,
                        pf=team.points,
                        ppf=team.projected_points,
                        ppf_percentage=(team.points / team.projected_points),
                    )
                )

            session.merge(
                Matchup(
                    winner_team=matchup.teams[0].id,
                    loser_team=matchup.teams[1].id,
                    week=i,
                    victory_margin=0.0,
                )
            )
        else:
            session.merge(
                Team(
                    id=matchup.winning_team.id,
                    name=matchup.winning_team.name,
                    image_url=matchup.winning_team.team_logos,
                )
            )

            session.merge(
                Team(
                    id=matchup.losing_team.id,
                    name=matchup.losing_team.name,
                    image_url=matchup.losing_team.team_logos,
                )
            )

            session.merge(
                WeeklyResult(
                    team_id=matchup.winning_team.id,
                    week=i,
                    is_winner=True,
                    is_tied=False,
                    pf=matchup.winning_team.points,
                    ppf=matchup.winning_team.projected_points,
                    ppf_percentage=(
                        matchup.winning_team.points
                        / matchup.winning_team.projected_points
                    ),
                )
            )

            session.merge(
                WeeklyResult(
                    team_id=matchup.losing_team.id,
                    week=i,
                    is_winner=False,
                    is_tied=False,
                    pf=matchup.losing_team.points,
                    ppf=matchup.losing_team.projected_points,
                    ppf_percentage=(
                        matchup.losing_team.points
                        / matchup.losing_team.projected_points
                    ),
                )
            )

            session.merge(
                Matchup(
                    winner_team=matchup.winning_team.id,
                    loser_team=matchup.losing_team.id,
                    week=i,
                    victory_margin=float(matchup.winning_team.points)
                    - float(matchup.losing_team.points),
                )
            )

    session.commit()

    teams = api.league().teams().get().teams
    for team in teams:
        print(f"Getting players for {team.name} for week {i}")
        players = get_sorted_players(api, team.id, i)
        qb, used = get_optimal_position(players, "QB", 1, [])
        dst, used = get_optimal_position(players, "DEF", 1, used)
        k, used = get_optimal_position(players, "K", 1, used)
        rest = max(
            get_rb_wr_te(players, used),
            get_rb_te_wr(players, used),
            get_wr_rb_te(players, used),
            get_wr_te_rb(players, used),
        )

        session.merge(
            OptimalPoints(team_id=team.id, week=i, points=sum(qb + dst + k + [rest]))
        )

    for i in range(1, week + 1):
        update_all_play(i)
