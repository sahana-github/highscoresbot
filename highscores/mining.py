from highscores.highscore import Highscore


class Mining(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Mining level", "Experience"]
        LINK = r"https://pokemon-planet.com/topMiners.php"
        NAME = "mining"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS mining(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "level TEXT, experience TEXT)"
        super(Mining, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE mining SET username=?, clan=?, level=?, experience=? WHERE rank=?"
