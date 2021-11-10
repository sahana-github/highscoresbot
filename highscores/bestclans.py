

from highscores.highscore import Highscore


class BestClans(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Clanname", "Founder", "Clan Experience"]
        self.NAME = "bestclans"
        self.LINK = "https://pokemon-planet.com/topStrongestClans.php"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS bestclans(rank INTEGER PRIMARY KEY, name TEXT, founder TEXT," \
                           "experience TEXT)"
        super(BestClans, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE bestclans SET name=?, founder=?, experience=? WHERE rank=?"

    def create(self, databasepath: str):
        """
        This method is to create the database and initialize the rank column.
        Calls the method from the superclass to set the amount of values to have when filling the database to 100
        instead of the default 1000.
        :param databasepath:
        """
        super().create(databasepath, 100)
