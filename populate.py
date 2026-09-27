import json
import sys
from pathlib import Path

from sqlite_utils import Database

# Define constants
TARGET_DIR = Path("./archive")
DB_NAME = "slamingo_cup.db"


def build_database():
    # 1. Validate target directory
    if not TARGET_DIR.is_dir():
        print(f"❌ Error: Could not find directory '{TARGET_DIR}'")
        sys.exit(1)

    # 2. Clean up old database
    db_path = Path(DB_NAME)
    if db_path.is_file():
        db_path.unlink()
        print("🧹 Removed old database.")

    print("🚀 Building database...")
    db = Database(DB_NAME)

    # 3. Find and insert JSON files
    for json_file in TARGET_DIR.rglob("*.json"):
        if json_file.is_file():
            table_name = json_file.stem
            print(f"📂 {json_file} -> [{table_name}]")

            with open(json_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    # Ensure data is a list of records for insert_all
                    if isinstance(data, dict):
                        data = [data]

                    db[table_name].insert_all(data, alter=True)
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: Could not parse JSON from {json_file}")

    print("⚡ Creating database indexes...")

    # 4. Create single and composite indexes
    db["managers"].create_index(["name"])
    db["players"].create_index(["sleeper_id"])

    db["selected_positions"].create_index(["season", "week", "manager"])
    db["player_stats"].create_index(["season", "week", "sleeper_id"])
    db["weekly_results"].create_index(["season", "week", "manager"])

    print("✅ Database built and indexed successfully!")


if __name__ == "__main__":
    build_database()
