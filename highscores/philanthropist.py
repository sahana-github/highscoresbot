from highscores.highscore import Highscore


class Philanthropist(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Philanthropist points"]
        LINK = r"https://pokemon-planet.com/topPhilanthropists.php"
        NAME = "pp"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS pp(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "points TEXT)"
        super(Philanthropist, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE pp SET username=?, clan=?, points=? WHERE rank=?"
