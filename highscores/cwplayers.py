from highscores.highscore import Highscore


class Cwplayers(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Wins-Losses", "Wins", "Losses", "Clan"]
        LINK = r"https://pokemon-planet.com/playerClanWarWinsLosses.php"
        NAME = "cwplayers"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS cwplayers(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "wins_losses TEXT, wins TEXT, losses TEXT, clan TEXT)"
        super(Cwplayers, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE cwplayers SET username=?, wins_losses=?, wins=?, losses=?, clan=? WHERE rank=?"
