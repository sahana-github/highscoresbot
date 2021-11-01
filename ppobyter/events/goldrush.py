import sqlite3

from .event import Event


class Goldrush(Event):
    """
    This is an event that happens when a goldrush pops up.
    """
    def __init__(self, location: str):
        """
        calls the init of the superclass and sets the location.
        :param location:
        """
        self.location = location.lower()
        self.EVENTNAME = "goldrush"
        super(Goldrush, self).__init__()

    def makeMessage(self) -> str:
        """
        makes the message that gets sent to channels/users.
        :return: The message that gets sent to channels/users.
        """
        return f"A gold rush has started at {self.location}!"

    def determineRecipients(self, **kwargs):
        """
        Determines the channelrecipients and pmrecipients.
        :param kwargs:
        :return:
        """
        self.__determinepmrecipients()
        self._determinechannelrecipients()

    def __determinepmrecipients(self):
        """
        Determines the recipients for pm, if users have configured they want a pm if a goldrush shows up on the location
        the current gold rush is at they get a pm.
        """
        conn = sqlite3.connect(self.pathManager.getpath("eventconfigurations.db"))
        cur = conn.cursor()
        cur.execute("SELECT playerid FROM pmgoldrush WHERE location=?", (self.location,))
        self._pmrecipients = list(set([row[0] for row in cur.fetchall()]))
        conn.close()
