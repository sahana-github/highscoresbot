import sqlite3

from highscores.highscore import Highscore


class Weeklyexp(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Experience gained"]
        LINK = r"https://pokemon-planet.com/weeklyTopStrongest.php"
        NAME = "weeklyexp"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS weeklyexp(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "experience TEXT)"
        super(Weeklyexp, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE weeklyexp SET username=?, clan=?, experience=? WHERE rank=?"
