import sqlite3

from ppobyter.events.event import Event


class OnlineList(Event):
    def __init__(self, timestamp, onlineplayers):
        self.onlineplayers = onlineplayers
        self.timestamp = timestamp
        super().__init__()

    def determineRecipients(self): pass

    async def __call__(self, _):
        conn = sqlite3.connect(r"../ingame_data.db")
        cur = conn.cursor()
        for playername in self.onlineplayers:
            result = cur.execute("UPDATE activity SET timestamp=? WHERE playername=?", (self.timestamp, playername))
            if not result.rowcount:
                cur.execute("INSERT INTO activity(playername, timestamp) VALUES(?,?)", (playername, self.timestamp))
        conn.commit()
        conn.close()
