



from highscores.highscore import Highscore


class RichestClans(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Clanname", "Founder", "Clan Bank"]
        NAME = "richestclans"
        LINK = "https://pokemon-planet.com/topRichestClans.php"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS richestclans(rank INTEGER PRIMARY KEY, name TEXT, founder TEXT," \
                           "clanbank TEXT)"
        super(RichestClans, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE richestclans SET name=?, founder=?, clanbank=? WHERE rank=?"

    def create(self, databasepath: str):
        """
        This method is to create the database and initialize the rank column.
        Calls the method from the superclass to set the amount of values to have when filling the database to 100
        instead of the default 1000.
        :param databasepath:
        """
        super()._create(databasepath, 100)
