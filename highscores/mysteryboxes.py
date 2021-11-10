from highscores.highscore import Highscore


class MysteryBoxes(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "Mystery boxes opened"]
        self.LINK = r"https://pokemon-planet.com/mostMysteryBoxes.php"
        self.NAME = "mysteryboxes"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS mysteryboxes(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "clan TEXT, amount TEXT)"
        super(MysteryBoxes, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE mysteryboxes SET username=?, clan=?, amount=? WHERE rank=?"
