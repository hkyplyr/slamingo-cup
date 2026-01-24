import json
import os

from helpers import format_percentage, format_points, format_record
from queries import get_all_play_records, get_career_records

DATA_PATH = "docs/data"


def fetch_record_data():
    career_records = {c.manager.name: c for c in get_career_records()}
    all_play_records = {ap.manager.name: ap for ap in get_all_play_records()}

    record_data = []
    for manager_name, career_record in career_records.items():
        all_play_record = all_play_records.get(manager_name)

        career_win_percentage = calculate_win_percentage(
            career_record.gp, career_record.w, career_record.t
        )

        all_play_win_percentage = calculate_win_percentage(
            all_play_record.gp, all_play_record.w, all_play_record.t
        )

        luck_percentage = format_percentage(
            (career_win_percentage - all_play_win_percentage) * 100, 1
        )

        record_data.append(
            {
                "manager": manager_name,
                "seasons": career_record.seasons,
                "active": all_play_record.manager.active,
                "career_record": format_record(
                    career_record.w, career_record.l, career_record.t
                ),
                "sort": career_win_percentage,
                "career_win_percentage": format_percentage(career_win_percentage, 3),
                "points_for": format_points(career_record.pf),
                "points_for_per_game": format_points(career_record.pfg),
                "points_against": format_points(career_record.pa),
                "points_against_per_game": format_points(career_record.pag),
                "all_play_record": format_record(
                    all_play_record.w, all_play_record.l, all_play_record.t
                ),
                "all_play_win_percentage": format_percentage(
                    all_play_win_percentage, 3
                ),
                "luck_percentage": luck_percentage,
            }
        )
    return sorted(record_data, key=lambda x: -x["sort"])


def persist_json(filename, data):
    qualified_filename = f"{DATA_PATH}/{filename}.json"
    os.makedirs(os.path.dirname(qualified_filename), exist_ok=True)
    with open(qualified_filename, "w") as f:
        json.dump(data, f, indent=2)


def calculate_win_percentage(gp, w, t):
    return (w * 2 + t) / (gp * 2)
