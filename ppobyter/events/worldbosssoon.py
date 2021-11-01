import sys

from ppobyter.events.event import Event
from commands.utils import getworldbosstime
import datetime


class WorldbossSoon(Event):
    """
    Event triggers 30 minutes before the worldboss shows up.
    """
    def __init__(self):
        """
        calls superclass init, has a failsafe check for if the worldboss does not happen between 30 minutes and the
        worldboss time. It sets the recipients to an empty list if the current time falls outside that failsafe check.
        """
        self.EVENTNAME = "worldboss"
        super(WorldbossSoon, self).__init__()
        self.timedifference = getworldbosstime(path=self.pathManager.getpath("worldbosstime.txt")) - datetime.datetime.now()
        print(self.timedifference.total_seconds())
        if self.timedifference.total_seconds() > 1800 or self.timedifference.total_seconds() < 0:
            # bot died, or something went wrong. No-one should receive a message.
            print("no recipients")

            self._recipients = []
        else:
            self.announcementSent()

    def announcementSent(self):
        """
        Sets the boolean on the worldboss time file to True indicating that the announcement 30 minutes before the
        worldboss has been sent.
        :return:
        """
        readfile = open(self.pathManager.getpath("worldbosstime.txt"))
        splittedfile = readfile.read().split("\n")
        readfile.close()
        splittedfile[0] = "1"
        writefile = open(self.pathManager.getpath("worldbosstime.txt"), "w")
        writefile.write("\n".join(splittedfile))
        writefile.close()

    def determineRecipients(self, **kwargs):
        """
        Determines the channelrecipients.
        """
        self._determinechannelrecipients()

    def makeMessage(self) -> str:
        """
        Makes the message that gets sent to the recipients.
        """
        return f"world boss starting in {int(self.timedifference.total_seconds() / 60)} minutes!"
