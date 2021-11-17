

from highscores.highscore import Highscore


class Btwinstreak(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Win Streak", "Wins"]
        NAME = "btwinstreak"
        LINK = "https://pokemon-planet.com/btWinStreak.php"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS btwinstreak(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "streak TEXT, wins TEXT)"
        super(Btwinstreak, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

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
