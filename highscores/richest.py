from highscores.highscore import Highscore


class Richest(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Money"]
        LINK = r"https://pokemon-planet.com/topRichest.php"
        NAME = "richest"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS richest(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "money TEXT)"
        super(Richest, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE richest SET username=?, clan=?, money=? WHERE rank=?"
