import sqlite3
from typing import List
import highscores
from highscores.highscore import Highscore
from pathmanager import PathManager


class Btwins(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Wins", "Win Streak"]
        NAME = "btwins"
        LINK = "https://pokemon-planet.com/btWins.php"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS btwins(rank INTEGER PRIMARY KEY, username TEXT, wins TEXT, " \
                           "streak TEXT)"
        super(Btwins, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def getDbValues(self, query=None, clan=None, params: List = []):
        conn = sqlite3.connect(PathManager().getpath("highscores.db"))
        cur = conn.cursor()
        if query is not None:
            if clan is None:
                cur.execute(query, params)
            else:
                cur.execute(query, [clan] + params)
        else:
            cur.execute(f"SELECT * FROM {self.NAME}")
        result = list(cur.fetchall())

        if clan is not None:
            trimmedresult = []
            clanlist = highscores.getClanList(clan.lower())
            for row in result:
                for column in row:
                    if column in clanlist:
                        trimmedresult.append(row)
                        break
        else:
            trimmedresult = result
        return trimmedresult

    def updatequery(self) -> str:
        return "UPDATE btwins SET username=?, wins=?, streak=? WHERE rank=?"

    def create(self, databasepath: str):
        """
        This method is to create the database and initialize the rank column.
        Calls the method from the superclass to set the amount of values to have when filling the database to 100
        instead of the default 1000.
        :param databasepath:
        """
        super()._create(databasepath, 100)
