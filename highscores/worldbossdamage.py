from highscores.highscore import Highscore


class WorldbossDamage(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Total damage"]
        LINK = r"https://pokemon-planet.com/mostWorldBossDamage.php"
        NAME = "wbdmg"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS wbdmg(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                           "amount TEXT)"
        super(WorldbossDamage, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE wbdmg SET username=?, clan=?, amount=? WHERE rank=?"
