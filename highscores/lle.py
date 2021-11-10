

from highscores.highscore import Highscore


class Lle(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "LLE"]
        self.LINK = r"https://pokemon-planet.com/topLLE.php"
        self.NAME = "lle"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS lle(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "amount TEXT)"
        super(Lle, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE lle SET username=?, clan=?, amount=? WHERE rank=?"
