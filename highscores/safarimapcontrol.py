from highscores.highscore import Highscore


class SafariMapcontrol(Highscore):
    def __init__(self):
        self.LAYOUT = ["rank", "clanname", "pokemon defeated"]
        self.NAME = "safarimc"
        self.LINK = "https://pokemon-planet.com/safariZoneMapControl.php"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS safarimc(rank INTEGER PRIMARY KEY, clan TEXT, pokemon_defeated " \
                           "TEXT)"
        super(SafariMapcontrol, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE safarimc SET clan=?, pokemon_defeated=? WHERE rank=?"

    def create(self, databasepath: str):
        """
        This method is to create the database and initialize the rank column.
        Calls the method from the superclass to set the amount of values to have when filling the database to 100
        instead of the default 1000.
        :param databasepath:
        """
        super().create(databasepath, 100)
