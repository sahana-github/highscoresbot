from highscores.highscore import Highscore


class Philanthropist(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "Philanthropist points"]
        self.LINK = r"https://pokemon-planet.com/topPhilanthropists.php"
        self.NAME = "pp"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS pp(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "points TEXT)"
        super(Philanthropist, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE pp SET username=?, clan=?, points=? WHERE rank=?"
