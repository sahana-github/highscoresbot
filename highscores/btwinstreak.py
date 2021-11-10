

from highscores.highscore import Highscore


class Btwinstreak(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Win Streak", "Wins"]
        self.NAME = "btwinstreak"
        self.LINK = "https://pokemon-planet.com/btWinStreak.php"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS btwinstreak(rank INTEGER PRIMARY KEY, name TEXT, streak TEXT," \
                           "wins TEXT)"
        super(Btwinstreak, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE btwinstreak SET name=?, streak=?, wins=? WHERE rank=?"

    def create(self, databasepath: str):
        """
        This method is to create the database and initialize the rank column.
        Calls the method from the superclass to set the amount of values to have when filling the database to 100
        instead of the default 1000.
        :param databasepath:
        """
        super().create(databasepath, 100)
