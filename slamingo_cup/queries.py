import peewee
from models import AllPlay, Manager, WeeklyResult


def get_all_play_records():
    return AllPlay.select(
        AllPlay.manager_id.alias("manager_id"),
        (
            peewee.fn.SUM(AllPlay.win)
            + peewee.fn.SUM(AllPlay.loss)
            + peewee.fn.SUM(AllPlay.tie)
        ).alias("gp"),
        peewee.fn.SUM(AllPlay.win).alias("w"),
        peewee.fn.SUM(AllPlay.loss).alias("l"),
        peewee.fn.SUM(AllPlay.tie).alias("t"),
    ).group_by(AllPlay.manager_id)


def get_career_records():
    opponent = WeeklyResult.alias()

    return (
        WeeklyResult.select(
            Manager.name,
            peewee.fn.COUNT(peewee.fn.Distinct(WeeklyResult.season)).alias("seasons"),
            peewee.fn.COUNT().alias("gp"),
            peewee.fn.SUM(
                peewee.Case(
                    None,
                    ((WeeklyResult.result == "W", 1),),
                    0,
                )
            ).alias("w"),
            peewee.fn.SUM(
                peewee.Case(
                    None,
                    ((WeeklyResult.result == "L", 1),),
                    0,
                )
            ).alias("l"),
            peewee.fn.SUM(
                peewee.Case(
                    None,
                    ((WeeklyResult.result == "T", 1),),
                    0,
                )
            ).alias("t"),
            peewee.fn.SUM(WeeklyResult.points_for).alias("pf"),
            peewee.fn.SUM(opponent.points_for).alias("pa"),
            peewee.fn.SUM(WeeklyResult.points_for - opponent.points_for).alias("pd"),
            peewee.fn.AVG(WeeklyResult.points_for).alias("pfg"),
            peewee.fn.AVG(opponent.points_for).alias("pag"),
            peewee.fn.AVG(WeeklyResult.points_for - opponent.points_for).alias("pdg"),
        )
        .join(Manager, on=(Manager.id == WeeklyResult.manager_id))
        .join(opponent, on=(opponent.id == WeeklyResult.opponent_id))
        .where(WeeklyResult.playoffs == False)
        .group_by(Manager)
    )
