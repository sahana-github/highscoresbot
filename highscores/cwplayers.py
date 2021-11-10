from highscores.highscore import Highscore


class Cwplayers(Highscore):
    def __init__(self):
        self.LAYOUT = ["Rank", "Username", "Wins-Losses", "Wins", "Losses", "Clan"]
        self.LINK = r"https://pokemon-planet.com/playerClanWarWinsLosses.php"
        self.NAME = "cwplayers"
        self.CREATEQUERY = "CREATE TABLE IF NOT EXISTS cwplayers(rank INTEGER PRIMARY KEY, username TEXT, " \
                           "wins_losses TEXT, wins TEXT, losses TEXT, clan TEXT)"
        super(Cwplayers, self).__init__()

    def updatequery(self) -> str:
        return "UPDATE cwplayers SET username=?, wins_losses=?, wins=?, losses=?, clan=? WHERE rank=?"
