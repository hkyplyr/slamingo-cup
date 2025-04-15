from fetcher import get_or_load_weekly_results
import json

def calculate_head_to_head(weekly_results):
    head_to_head = {}
    for entry in weekly_results:
        if entry.playoffs:
            continue

        team_key = entry.team
        if team_key not in head_to_head:
            head_to_head[team_key] = {}

        opponent_key = entry.opponent
        if opponent_key not in head_to_head[team_key]:
            head_to_head[team_key][opponent_key] = {"w": 0, "l": 0, "t": 0}

        if entry.tie:
            wins = 0
            losses = 0
            ties = 1
        elif entry.win:
            wins = 1
            losses = 0
            ties = 0
        else:
            wins = 0
            losses = 1
            ties = 0

        head_to_head[team_key][opponent_key]["w"] += wins
        head_to_head[team_key][opponent_key]["l"] += losses
        head_to_head[team_key][opponent_key]["t"] += ties

    for k in head_to_head.items():
        print(k)


def calculate_all_play(weekly_results):
    results_by_week = {}
    for entry in weekly_results:
        if entry.playoffs:
            continue

        if (entry.season, entry.week) not in results_by_week:
            results_by_week[(entry.season, entry.week)] = []

        results_by_week[(entry.season, entry.week)].append(
            (entry.team, entry.points_for)
        )

    weekly_all_plays = []
    for teams in results_by_week.values():
        total_teams = len(teams) - 1
        wins = 0
        wins_for_ties = 0
        sorted_teams = sorted(teams, key=lambda x: x[1])

        points = set()
        tied_points = []
        for team in sorted_teams:
            if team[1] in points:
                tied_points.append(team[1])
            else:
                points.add(team[1])

        records = []
        for team in sorted_teams:

            tied = int(team[1] in tied_points)
            ties = len(list(filter(lambda x: x == team[1], tied_points)))
            if tied:
                losses = total_teams - wins_for_ties - ties
                records.append(
                    {"team": team[0], "w": wins_for_ties, "l": losses, "t": ties}
                )
            else:
                losses = total_teams - wins - ties
                records.append({"team": team[0], "w": wins, "l": losses, "t": ties})

            wins += 1
            if not tied:
                wins_for_ties = wins

        weekly_all_plays.extend(records)

    all_plays = {}
    for entry in weekly_all_plays:
        if entry["team"] not in all_plays:
            all_plays[entry["team"]] = {"w": 0, "l": 0, "t": 0}

        all_plays[entry["team"]]["w"] += entry["w"]
        all_plays[entry["team"]]["l"] += entry["l"]
        all_plays[entry["team"]]["t"] += entry["t"]

    for team, stats in all_plays.items():
        stats["gp"] = stats["w"] + stats["l"] + stats["t"]
        stats["w%"] = (stats["w"] + (stats["t"] / 2)) / stats["gp"]
        all_plays[team] = stats

    for k, v in sorted(all_plays.items(), key=lambda x: -x[1]["w%"]):
        print(k, v)


def calculate_career_stats(weekly_results):
    career_stats = {}

    for entry in weekly_results:
        if entry.playoffs:
            continue

        if entry.team not in career_stats:
            career_stats[entry.team] = {
                "seasons": set(),
                "team": entry.team,
                "gp": 0,
                "w": 0,
                "l": 0,
                "t": 0,
                "pf": 0,
                "pa": 0,
            }

        if entry.tie:
            wins = 0
            losses = 0
            ties = 1
        elif entry.win:
            wins = 1
            losses = 0
            ties = 0
        else:
            wins = 0
            losses = 1
            ties = 0

        career_stats[entry.team]["seasons"].add(entry.season)
        career_stats[entry.team]["gp"] += 1
        career_stats[entry.team]["w"] += wins
        career_stats[entry.team]["l"] += losses
        career_stats[entry.team]["t"] += ties
        career_stats[entry.team]["pf"] += entry.points_for
        career_stats[entry.team]["pa"] += entry.points_against

    for team, stats in career_stats.items():
        stats["seasons"] = len(stats["seasons"])
        stats["w%"] = round(stats["w"] / stats["gp"] * 100, 1)
        stats["pf"] = round(stats["pf"], 2)
        stats["pa"] = round(stats["pa"], 2)
        stats["pd"] = round(stats["pf"] - stats["pa"], 2)
        stats["pf/g"] = round(stats["pf"] / stats["gp"], 2)
        stats["pa/g"] = round(stats["pa"] / stats["gp"], 2)
        stats["pd/g"] = round(stats["pd"] / stats["gp"], 2)

        career_stats[team] = stats

    print(json.dumps(sorted(career_stats.values(), key=lambda x: (-x["w%"], -x["pf/g"]))))
    for stats in sorted(career_stats.values(), key=lambda x: (-x["w%"], -x["pf/g"])):
        print(stats)


def calculate_season_stats(weekly_results):
    season_stats = {}

    for entry in weekly_results:
        if entry.playoffs:
            continue

        if (entry.season, entry.team) not in season_stats:
            season_stats[(entry.season, entry.team)] = {
                "season": entry.season,
                "team": entry.team,
                "gp": 0,
                "w": 0,
                "l": 0,
                "t": 0,
                "pf": 0,
                "pa": 0,
            }

        if entry.tie:
            wins = 0
            losses = 0
            ties = 1
        elif entry.win:
            wins = 1
            losses = 0
            ties = 0
        else:
            wins = 0
            losses = 1
            ties = 0

        season_stats[(entry.season, entry.team)]["gp"] += 1
        season_stats[(entry.season, entry.team)]["w"] += wins
        season_stats[(entry.season, entry.team)]["l"] += losses
        season_stats[(entry.season, entry.team)]["t"] += ties
        season_stats[(entry.season, entry.team)]["pf"] += entry.points_for
        season_stats[(entry.season, entry.team)]["pa"] += entry.points_against

    for team_season, stats in season_stats.items():
        stats["pd"] = stats["pf"] - stats["pa"]
        stats["pf/g"] = stats["pf"] / stats["gp"]
        stats["pa/g"] = stats["pa"] / stats["gp"]
        stats["pd/g"] = stats["pd"] / stats["gp"]

        season_stats[team_season] = stats

    season_stats = sorted(season_stats.values(), key=lambda x: (x["season"], x["team"]))

    for stats in season_stats:
        print(stats)


if __name__ == "__main__":

    # calculate_all_play(get_or_load_weekly_results())
    # calculate_head_to_head(get_or_load_weekly_results())
    # calculate_season_stats(get_or_load_weekly_results())
    calculate_career_stats(get_or_load_weekly_results())
