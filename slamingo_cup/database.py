import logging

from peewee import SqliteDatabase

logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

BATCH_SIZE = 1000

db = SqliteDatabase(".cache/slamingo_cup.db")


def insert_all(cls, data):
    with db.atomic():
        for idx in range(0, len(data), BATCH_SIZE):
            logging.info(f"Upserting {cls} from {idx}-{idx + BATCH_SIZE}")
            cls.insert_many(data[idx : idx + BATCH_SIZE]).on_conflict_ignore().execute()
