import json
import os

from queries import get_all_play_records, get_career_records

DATA_PATH = "docs/data"


def update_record_data():
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

        luck_percentage = (career_win_percentage - all_play_win_percentage) * 100

        record_data.append(
            {
                "manager_name": manager_name,
                "seasons": career_record.seasons,
                "active": all_play_record.manager.active,
                "gp": career_record.gp,
                "w": career_record.w,
                "l": career_record.l,
                "t": career_record.t,
                "w%": career_win_percentage,
                "pf": career_record.pf,
                "pa": career_record.pa,
                "pd": career_record.pd,
                "pf/g": career_record.pfg,
                "pa/g": career_record.pag,
                "pd/g": career_record.pdg,
                "ap gp": all_play_record.gp,
                "ap w": all_play_record.w,
                "ap l": all_play_record.l,
                "ap t": all_play_record.t,
                "ap w%": all_play_win_percentage,
                "luck": luck_percentage,
            }
        )

    persist_json("records", sorted(record_data, key=lambda x: (-x["active"], -x["w%"])))


def persist_json(filename, data):
    qualified_filename = f"{DATA_PATH}/{filename}.json"
    os.makedirs(os.path.dirname(qualified_filename), exist_ok=True)
    with open(qualified_filename, "w") as f:
        json.dump(data, f, indent=2)


def calculate_win_percentage(gp, w, t):
    return (w * 2 + t) / (gp * 2)


if __name__ == "__main__":
    update_record_data()
