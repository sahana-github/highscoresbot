import sqlite3
from typing import List

import highscores
from highscores.highscore import Highscore
from pathmanager import PathManager


class Btwinstreak(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Win Streak", "Wins"]
        NAME = "btwinstreak"
        LINK = "https://pokemon-planet.com/btWinStreak.php"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS btwinstreak(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "streak TEXT, wins TEXT)"
        super(Btwinstreak, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

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
        return "UPDATE btwinstreak SET username=?, streak=?, wins=? WHERE rank=?"

    def create(self, databasepath: str):
        """
        This method is to create the database and initialize the rank column.
        Calls the method from the superclass to set the amount of values to have when filling the database to 100
        instead of the default 1000.
        :param databasepath:
        """
        super()._create(databasepath, 100)
