import sqlite3
from highscores import getPlayerClan
from.event import Event


class ClanEvent(Event):
    """
    This is an event whose recipients are based on the clan of the player.
    """
    def __init__(self, player: str):
        """
        Calls the superclass and sets the player attribute.
        :param player: the player on whose clan the recipients are based.
        """
        self.player = player.lower()
        super(ClanEvent, self).__init__()

    def _determinechannelrecipients(self):
        """
        determines the channel recipients based on the players clan
        """
        if (clan := getPlayerClan(self.player)) is None:
            clan = 'all'
        conn = sqlite3.connect(self.pathManager.getpath("eventconfigurations.db"))
        cur = conn.cursor()
        cur.execute("SELECT guildid FROM clanconfig WHERE clan=? OR clan='all'", (clan,))
        guilds = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT guildid FROM memberconfig WHERE playername=?", (self.player,))
        guilds += [row[0] for row in cur.fetchall()]
        guilds = list(set(guilds))

        total = []
        all_channels = []
        for guild in guilds:
            cur.execute("SELECT channel, pingrole, alivetime FROM eventconfig WHERE eventname=? AND guildid=? and "
                        "channel IS NOT NULL",
                        (self.EVENTNAME, guild))
            result = cur.fetchall()
            for row in result:
                if row[0] not in all_channels:
                    total.append(row)
        for row in total:
            self._recipients.append(row[0])
            self._pingroles.append(row[1])
            self._alive_time.append(row[2])
        conn.close()
