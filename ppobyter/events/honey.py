import sqlite3

from .event import Event


class Honey(Event):
    """
    This is an event that happens when a player spreads honey at a location.
    """
    def __init__(self, location: str, player: str):
        """
        Here the init of the superclass is called, the location is inserted, the player and location properties get set.
        :param location: the location honey is spread at.
        :param player: The player who spread the honey.
        """
        self.location = location.lower()
        self.player = player
        self.EVENTNAME = "honey"
        super(Honey, self).__init__()
        self.insertLocation()

    def insertLocation(self):
        """
        inserts the location into the database.
        :return:
        """
        conn = sqlite3.connect(self.pathManager.getpath("data.db"))
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO honeylocations(location) VALUES(?)", (self.location,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        except sqlite3.OperationalError:
            print("database locked!!!!")
        finally:
            conn.close()

    def makeMessage(self) -> str:
        """
        Makes the message that gets sent to the recipients.
        :return: the message that gets sent to the recipients.
        """
        return f"{self.player} has spread some Honey at {self.location}!"

    def determineRecipients(self, **kwargs):
        """
        Determines the recipients for both pm and channels.
        """
        self.__determinepmrecipients()
        self._determinechannelrecipients()

    def __determinepmrecipients(self):
        """
        Determines the recipients for pm. If a user has configured that he wants a pm if honey gets spread at that
        location he gets a pm.
        """
        conn = sqlite3.connect(self.pathManager.getpath("eventconfigurations.db"))
        cur = conn.cursor()
        cur.execute("SELECT playerid FROM pmhoney WHERE location=?", (self.location,))
        self._pmrecipients = list(set([row[0] for row in cur.fetchall()]))
        conn.close()
