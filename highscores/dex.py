from highscores.highscore import Highscore


class Dex(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "Unique Pokemon Caught/Evolved"]
        self.LINK = r"https://pokemon-planet.com/mostPokemonOwned.php"
        self.NAME = "dex"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS dex(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "caught TEXT)"
        super(Dex, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE dex SET username=?, clan=?, caught=? WHERE rank=?"
