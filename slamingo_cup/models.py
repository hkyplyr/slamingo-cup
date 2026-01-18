from database import db
from peewee import (
    BooleanField,
    CharField,
    CompositeKey,
    ForeignKeyField,
    IntegerField,
    Model,
)


class BaseModel(Model):
    """
    Base model class that should be subclassed by all models in the app.
    Connects models to the database and implements shared functionality.
    """

    class Meta:
        database = db

    def __repr__(self):
        return self.__dict__["__data__"]

    def __str__(self):
        return str(self.__dict__["__data__"])


class Player(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    positions = CharField(null=True)
    pro_team = CharField(null=True)
    yahoo_id = IntegerField(null=True)


class PlayerStatistics(BaseModel):
    player = ForeignKeyField(Player, backref="statistics")
    season = IntegerField()
    week = IntegerField()
    pass_yards = IntegerField()
    pass_touchdowns = IntegerField()
    pass_interceptions = IntegerField()
    rush_yards = IntegerField()
    rush_touchdowns = IntegerField()
    receptions = IntegerField()
    rec_yards = IntegerField()
    rec_touchdowns = IntegerField()
    fumbles = IntegerField()

    class Meta:
        table_name = "player_statistics"
        primary_key = CompositeKey("player", "season", "week")


class Manager(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    active = BooleanField()


class PlayerStarted(BaseModel):
    manager = ForeignKeyField(Manager)
    player = ForeignKeyField(Player)
    season = IntegerField()
    week = IntegerField()
    started = BooleanField()

    class Meta:
        table_name = "player_started"
        primary_key = CompositeKey("player", "season", "week")


if __name__ == "__main__":
    db.connect()
    db.create_tables([Player, PlayerStatistics, Manager, PlayerStarted])
