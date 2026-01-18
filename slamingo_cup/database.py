import logging

from peewee import SqliteDatabase

logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

BATCH_SIZE = 1000

db = SqliteDatabase(".cache/slamingo_cup.db", pragmas={"foreign_keys": 1})


def insert_all(cls, data, on_conflict_replace=False):
    with db.atomic():
        for idx in range(0, len(data), BATCH_SIZE):
            logging.info(f"Upserting {cls} from {idx}-{idx + BATCH_SIZE}")
            insert_query = cls.insert_many(data[idx : idx + BATCH_SIZE])

            if on_conflict_replace:
                insert_query.on_conflict_replace().execute()
            else:
                insert_query.on_conflict_ignore().execute()
