import json
import sqlite3
from pathlib import Path

DB_PATH = Path("slamingo_cup.db")
QUERIES_DIR = Path("queries")
OUTPUT_DIR = Path("data")


def run_query(db, query_path, params=None):
    if params is None:
        params = {}

    sql = query_path.read_text(encoding="utf-8")

    cursor = db.execute(sql, params)

    columns = [column[0] for column in cursor.description]

    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def generate_record_book(db):
    query_dir = QUERIES_DIR / "record_book"

    entries = []

    for query in sorted(query_dir.glob("*.sql")):
        metadata = read_metadata(query)

        entries.append(
            {
                "name": metadata["name"],
                "ordinal": metadata["ordinal"],
                "entries": run_query(db, query),
            }
        )

    return sorted(entries, key=lambda x: x["ordinal"])


POSITIONS = ["QB", "RB", "WR", "TE"]


def generate_hall_of_fame(db):
    query_dir = QUERIES_DIR / "hall_of_fame"

    return {
        query.stem: {
            position: run_query(db, query, {"position": position})
            for position in POSITIONS
        }
        for query in sorted(query_dir.glob("*.sql"))
    }


def generate_head_to_head(db):
    query_dir = QUERIES_DIR / "head_to_head"

    return {
        query.stem: run_query(db, query) for query in sorted(query_dir.glob("*.sql"))
    }


def generate_career_stats(db):
    query_dir = QUERIES_DIR / "career_stats"
    return {
        query.stem: run_query(db, query) for query in sorted(query_dir.glob("*.sql"))
    }


def read_metadata(query_path):
    metadata = {}

    for line in query_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("-- name:"):
            metadata["name"] = line.removeprefix("-- name:").strip()

        elif line.startswith("-- ordinal:"):
            metadata["ordinal"] = int(line.removeprefix("-- ordinal:").strip())

    if "name" not in metadata:
        raise ValueError(f"Missing name in {query_path}")

    if "ordinal" not in metadata:
        raise ValueError(f"Missing ordinal in {query_path}")

    return metadata


def write_json(filename, data):
    output_path = OUTPUT_DIR / filename

    output_path.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Generated {output_path}")


def generate_all():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as db:
        write_json(
            "record_book.json",
            generate_record_book(db),
        )

        write_json(
            "hall_of_fame.json",
            generate_hall_of_fame(db),
        )

        write_json("head_to_head.json", generate_head_to_head(db))

        write_json("career_stats.json", generate_career_stats(db))


if __name__ == "__main__":
    generate_all()
