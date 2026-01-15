from client import get_players
from peewee import BooleanField, CharField, IntegerField, Model, SqliteDatabase

BATCH_SIZE = 1000

db = SqliteDatabase("slamingo_cup.db")


class Player(Model):
    id = CharField(unique=True)
    name = CharField()
    positions = CharField(null=True)
    yahoo_id = IntegerField(null=True)

    class Meta:
        database = db

    @classmethod
    def to_params(cls, json):
        id = json["player_id"]
        name = f"{json['first_name']} {json['last_name']}"
        fantasy_positions = json["fantasy_positions"]
        positions = None if not fantasy_positions else ",".join(fantasy_positions)
        yahoo_id = None if not json.get("yahoo_id") else int(json.get("yahoo_id"))

        return {"id": id, "name": name, "positions": positions, "yahoo_id": yahoo_id}


class RosterPosition(Model):
    started = BooleanField()
    season = IntegerField()
    week = IntegerField()
    player_id = CharField()
    team_id = CharField()


def populate_players():
    player_data = [Player.to_params(p) for p in get_players().values()]

    with db.atomic():
        for idx in range(0, len(player_data), BATCH_SIZE):
            Player.insert_many(
                player_data[idx : idx + BATCH_SIZE]
            ).on_conflict_replace().execute()


if __name__ == "__main__":
    db.connect()
    db.create_tables([Player])
    populate_players()

    print(Player.select().count())
