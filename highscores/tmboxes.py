from highscores.highscore import Highscore


class TmBoxes(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "Tm Boxes opened"]
        self.LINK = r"https://pokemon-planet.com/mostTMBoxes.php"
        self.NAME = "tmboxes"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS tmboxes(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "clan TEXT, amount TEXT)"
        super(TmBoxes, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE tmboxes SET username=?, clan=?, amount=? WHERE rank=?"
