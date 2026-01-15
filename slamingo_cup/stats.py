import requests

SEASONS = [2020, 2021, 2022, 2023, 2024, 2025]
WEEKS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]


BASE_URL = "https://api.sleeper.com/stats/nfl"
PARAMS = {
    "position[]": ["QB", "RB", "WR", "TE", "DEF", "K"],
    "season_type": "regular",
    "order_by": "pts_half_ppr",
}


def get_stats(season, week):
    return requests.get(f"{BASE_URL}/{season}/{week}", params=PARAMS).json()


STAT_KEYS = [
    "pts_half_ppr",
    "pass_yd",
    "pass_td",
    "pass_int",
    "rush_yd",
    "rush_td",
    "rec",
    "rec_yd",
    "rec_td",
]

if __name__ == "__main__":
    for season in SEASONS:
        for week in WEEKS:
            for result in get_stats(season, week)[:1]:
                stats = {k: result["stats"].get(k, 0.0) for k in STAT_KEYS}
                print(
                    season,
                    week,
                    result["player"]["first_name"],
                    result["player"]["last_name"],
                    stats,
                )
