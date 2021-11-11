

from highscores.highscore import Highscore


class Lle(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "LLE"]
        LINK = r"https://pokemon-planet.com/topLLE.php"
        NAME = "lle"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS lle(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "amount TEXT)"
        super(Lle, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE lle SET username=?, clan=?, amount=? WHERE rank=?"
