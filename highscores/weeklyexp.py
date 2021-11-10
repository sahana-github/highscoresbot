import sqlite3

from highscores.highscore import Highscore


class Weeklyexp(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "Experience gained"]
        self.LINK = r"https://pokemon-planet.com/weeklyTopStrongest.php"
        self.NAME = "weeklyexp"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS weeklyexp(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "experience TEXT)"
        super(Weeklyexp, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE weeklyexp SET username=?, clan=?, experience=? WHERE rank=?"
