from highscores.highscore import Highscore


class Achievements(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "Achievements completed"]
        self.LINK = r"https://pokemon-planet.com/mostAchievements.php"
        self.NAME = "achievements"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS achievements(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "amount TEXT)"
        super(Achievements, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE achievements SET username=?, clan=?, amount=? WHERE rank=?"
