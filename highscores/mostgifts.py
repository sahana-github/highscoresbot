from highscores.highscore import Highscore


class MostGifts(Highscore):
    def __init__(self):
        LAYOUT = ["Rank", "Username", "Clan", "Gifts Sent"]
        LINK = r"https://pokemon-planet.com/mostGifts.php"
        NAME = "mostgifts"
        CREATEQUERY = "CREATE TABLE IF NOT EXISTS mostgifts(rank INTEGER PRIMARY KEY, username TEXT, clan TEXT, " \
                      "giftssent TEXT)"
        super(MostGifts, self).__init__(NAME, LINK, LAYOUT, CREATEQUERY)

    def updatequery(self) -> str:
        return "UPDATE mostgifts SET username=?, clan=?, giftssent=? WHERE rank=?"
