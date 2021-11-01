import sqlite3
import re
from typing import List

from .event import Event


class Tournament(Event):
    """
    This event triggers when a tournament shows up.
    """
    def __init__(self, tournament: str, prizes: List[str]):
        """
        Calls superclass init, sets the tournament type, and the prizes. Also inserts the prizes into a database.
        :param tournament: The tournament type
        :param prizes: The prizes to be won in the tournament.
        """
        self.prizes = [prize.lower() for prize in prizes]
        self.tournament = tournament.lower()
        self.EVENTNAME = "tournament"
        super(Tournament, self).__init__()
        self.insertprizes()

    def makeMessage(self) -> str:
        """
        makes the message that gets sent to the recipients.
        :return: The message that gets sent.
        """
        return f"The {self.tournament} Tournament will start in 30 minutes at the Vermilion City PvP Arena. " \
               f"Tournament prize: " + ", ".join(self.prizes)

    def insertprizes(self):
        """
        Inserts the prizes into the database.
        """
        conn = sqlite3.connect(self.pathManager.getpath("data.db"))
        cur = conn.cursor()
        for prize in self.prizes:
            pattern = r"(.* ?)(?= \(([0-9]+)\))"
            if match := re.search(pattern, prize):
                prize = match.group()
            try:
                cur.execute("INSERT INTO tournamentprizes(prize) VALUES(?)", (prize,))
                conn.commit()
            except sqlite3.IntegrityError:
                pass
            except sqlite3.OperationalError:
                print("database locked!!!!")
        conn.close()

    def determineRecipients(self):
        """
        This determines both the recipients for pm and for channels.
        :return:
        """
        self._determinechannelrecipients()
        self.__determinepmrecipients()

    def __determinepmrecipients(self):
        """
        This determines the pmrecipients based on prize, tournament type or a combination of both.
        """
        playerids = []
        query = "SELECT playerid FROM pmtournament WHERE (tournament=? OR prize=?) AND comparator='|' " \
                "OR (tournament = ? AND prize=? AND comparator='&')"
        conn = sqlite3.connect(self.pathManager.getpath("eventconfigurations.db"))
        cur = conn.cursor()
        for prize in self.prizes:
            pattern = r"(.* ?)(?= \(([0-9]+)\))"
            if match := re.search(pattern, prize):
                prize = match.group()
            cur.execute(query, (self.tournament, prize, self.tournament, prize))
            playerids += [row[0] for row in cur.fetchall()]
        self._pmrecipients = list(set(playerids))
