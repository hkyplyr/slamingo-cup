import json
import os
import sys

from build_recap import build_recap
from jinja2 import Environment, PackageLoader, select_autoescape
from num2words import num2words

from slamingo_cup.queries import (
    PlayerAwards,
    PowerRankings,
    Standings,
    TeamAwards,
    WeeklyResults,
)


class Writer:
    def __build_template_values(self, week):
        return {
            "week": num2words(week).title(),
            "next_week": num2words(week + 1).title(),
            "previous_week_url": self.__build_url(week - 1),
            "next_week_url": self.__build_url(week + 1),
            "standings": Standings.get_standings(week),
            "power_rankings": PowerRankings.get_power_rankings(week),
            "weekly_results": WeeklyResults.get_weekly_results(week),
            "player_awards": PlayerAwards.get_player_awards(week),
            "team_awards": TeamAwards.get_awards(week),
            "recaps": self.__load_recaps(week),
        }

    def __build_url(self, week):
        if week == 0:
            return "index.html"
        url = f"week-{week}-recap.html"
        if os.path.isfile(f"docs/recaps/{url}"):
            return url

    def __load_recaps(self, week):
        file_path = f"slamingo_cup/recaps/week-{week}-recap.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            print(f"Building recap for Week {week}")
            return build_recap(week)

    def __load_template(self, template_name):
        env = Environment(
            loader=PackageLoader("slamingo_cup", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        return env.get_template(template_name)

    def write_report(self, week):
        template = self.__load_template("nfl_report.html")
        values = self.__build_template_values(int(week))

        with open(f"docs/recaps/week-{week}-recap.html", "w") as f:
            f.write(template.render(**values))

    def update_index(self, week):
        template = self.__load_template("index.html")
        weeks = [(w, num2words(w).title()) for w in range(1, week + 1)]

        with open("docs/recaps/index.html", "w") as f:
            f.write(template.render(weeks=weeks))


if __name__ == "__main__":
    writer = Writer()
    target_week = int(sys.argv[1])

    writer.update_index(target_week)
    for week in range(1, target_week + 1):
        writer.write_report(week)
