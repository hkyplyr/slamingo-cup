class WeeklyResult:
    def __init__(self, params):
        self.season = params["season"]
        self.week = params["week"]
        self.team = params["team"]
        self.opponent = params["opponent"]
        self.points_for = params["points_for"]
        self.points_against = params["points_against"]
        self.projected_points_for = params["projected_points_for"]
        self.projected_points_against = params["projected_points_against"]
        self.win = params["win"]
        self.tie = params["tie"]
        self.playoffs = params["playoffs"]
        self.consolation = params["consolation"]

    def __repr__(self):
        return str(self.__dict__)
