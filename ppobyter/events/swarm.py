from .event import Event
import json
import sqlite3


class Swarm(Event):
    """
    This event gets triggered when a swarm shows up.
    """
    def __init__(self, location: str, pokemon1: str, pokemon2: str):
        """
        This calls the superclass, sets the location, the first pokemon, and the second pokemon of the swarm.
        :param location: The location where the swarm showed up.
        :param pokemon1: The first pokemon that showed up in the swarm.
        :param pokemon2: The second pokemon that showed up in the swarm.
        """
        self.location = location.lower()
        self.pokemon1 = pokemon1.lower()
        self.pokemon2 = pokemon2.lower()
        self.EVENTNAME = "swarm"
        super(Swarm, self).__init__()

    def makeMessage(self) -> str:
        """
        Makes the message that gets sent to the recipients.
        :return: The message.
        """
        return f"A group of wild {self.pokemon1} and {self.pokemon2} have been spotted at {self.location}!"

    def determineRecipients(self, **kwargs):
        """
        Determines the recipients.
        """
        self.__determinepmrecipients()
        self._determinechannelrecipients()

    def __determinepmrecipients(self):
        """
        This determines the users that will receive a pm when this event shows up.
        They can either get a message for the location, or one of the pokemon, or a combination of both.
        """
        conn = sqlite3.connect(self.pathManager.getpath("eventconfigurations.db"))
        query = "SELECT playerid FROM pmswarm WHERE (location=? AND (pokemon=? OR pokemon=?) AND comparator='&') " \
                "OR ((location=? OR (pokemon=? OR pokemon=?)) AND comparator='|')"
        cur = conn.cursor()
        cur.execute(query, (self.location, self.pokemon1, self.pokemon2, self.location, self.pokemon1, self.pokemon2))
        playerids = [row[0] for row in cur.fetchall()]
        conn.close()
        # remove duplicates
        self._pmrecipients = list(set(playerids))
