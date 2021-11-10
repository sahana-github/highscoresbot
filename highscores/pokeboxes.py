from highscores.highscore import Highscore


class PokeBoxes(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Clan", "Pokemon Boxes opened"]
        self.LINK = r"https://pokemon-planet.com/mostPokemonBoxes.php"
        self.NAME = "pokeboxes"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS pokeboxes(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "clan TEXT, amount TEXT)"
        super(PokeBoxes, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE pokeboxes SET username=?, clan=?, amount=? WHERE rank=?"
