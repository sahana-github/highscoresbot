from highscores.highscore import Highscore


class Fishing(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "Fishing level", "Experience"]
        self.LINK = r"https://pokemon-planet.com/topFishers.php"
        self.NAME = "fishing"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS fishing(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "level TEXT, experience TEXT)"
        super(Fishing, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE fishing SET username=?, clan=?, level=?, experience=? WHERE rank=?"
