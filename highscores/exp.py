from highscores.highscore import Highscore


class Exp(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Total Experience gained"]
        LINK = r"https://pokemon-planet.com/topStrongest.php"
        NAME = "exp"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS exp(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "total_experience TEXT)"
        super(Exp, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE exp SET username=?, clan=?, total_experience=? WHERE rank=?"
