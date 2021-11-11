from highscores.highscore import Highscore


class Dex(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Unique Pokemon Caught/Evolved"]
        LINK = r"https://pokemon-planet.com/mostPokemonOwned.php"
        NAME = "dex"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS dex(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "caught TEXT)"
        super(Dex, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE dex SET username=?, clan=?, caught=? WHERE rank=?"
