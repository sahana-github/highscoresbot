from highscores.highscore import Highscore



class Cwwins(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Wins", "Losses", "Wins-Losses", "Clan"]
        LINK = r"https://pokemon-planet.com/playerClanWarWins.php"
        NAME = "cwwins"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS cwwins(rank INTEGER PRIMARY KEY, username TEXT, wins TEXT, " \
                           "losses TEXT, wins_losses TEXT, clan TEXT)"
        super(Cwwins, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE cwwins SET username=?, wins=?, losses=?, wins_losses=?, clan=? WHERE rank=?"
