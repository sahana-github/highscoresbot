from highscores.highscore import Highscore


class EvoBoxes(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "Evo Boxes opened"]
        self.LINK = r"https://pokemon-planet.com/mostEvoBoxes.php"
        self.NAME = "evoboxes"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS evoboxes(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "clan TEXT, amount TEXT)"
        super(EvoBoxes, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE evoboxes SET username=?, clan=?, amount=? WHERE rank=?"
