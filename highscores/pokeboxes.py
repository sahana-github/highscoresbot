from highscores.highscore import Highscore


class PokeBoxes(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Pokemon Boxes opened"]
        LINK = r"https://pokemon-planet.com/mostPokemonBoxes.php"
        NAME = "pokeboxes"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS pokeboxes(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "clan TEXT, amount TEXT)"
        super(PokeBoxes, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE pokeboxes SET username=?, clan=?, amount=? WHERE rank=?"
