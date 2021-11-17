import sqlite3
import datetime

from .clanevent import ClanEvent


class Chest(ClanEvent):
    """
    This is an event that happens when opening a treasure chest.
    """
    def __init__(self, player: str, location: str):
        self.location = location
        self.EVENTNAME = "chest"
        super(Chest, self).__init__(player)
        self.insertchest()

    def insertchest(self):
        """
        inserts a treasure chest in the database.
        """
        conn = sqlite3.connect(self.pathManager.getpath("ingame_data.db"))
        cur = conn.cursor()
        date = str(datetime.datetime.now()).split()[0]
        cur.execute("INSERT INTO chests(location, player, date) VALUES(?,?,?)", (self.location.lower(), self.player.lower(), date))
        conn.commit()
        conn.close()

    def determineRecipients(self):
        """
        Here the channelrecipients are determined.
        """
        self._determinechannelrecipients()

    def makeMessage(self) -> str:
        """
        Make the message that gets sent to the recipients.
        :return: The message that will get sent.
        """
        return f"{self.player} has opened a treasure chest at {self.location}!"
