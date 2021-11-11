from highscores.highscore import Highscore


class TmBoxes(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Tm Boxes opened"]
        LINK = r"https://pokemon-planet.com/mostTMBoxes.php"
        NAME = "tmboxes"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS tmboxes(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "clan TEXT, amount TEXT)"
        super(TmBoxes, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE tmboxes SET username=?, clan=?, amount=? WHERE rank=?"
