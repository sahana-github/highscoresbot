import re
import time

from ppobyter.events.timedevent import TimedEvent
from commands.utils import getworldbosstime, worldbosssent
import datetime


class WorldbossSoon(TimedEvent):
    """
    Event triggers 30 minutes before the worldboss shows up.
    """
    def __init__(self):
        """
        calls superclass init, has a failsafe check for if the worldboss does not happen between 30 minutes and the
        worldboss time. It sets the recipients to an empty list if the current time falls outside that failsafe check.
        """
        self.EVENTNAME = "worldboss"
        super(WorldbossSoon, self).__init__(datetime.timedelta(hours=10))
        self.setActivationTime(getworldbosstime(path=self.pathManager.getpath("worldbosstime.txt")) - \
                              datetime.timedelta(minutes=30))
        print("worldboss soon announcement at:" + str(self.activationtime))

    def messageProcesser(self, message: str):
        pattern = r"``````Next World Boss in (?P<hours>[0-9]+) hours, (?P<minutes>[0-9]+) minutes.``````"
        if match := re.search(pattern, message):
            print("pressed powerticket")
            groupdict = match.groupdict()
            self.__writeworldbosstime(groupdict.get("hours"), groupdict.get("minutes"))
            self.setActivationTime(getworldbosstime(path=self.pathManager.getpath("worldbosstime.txt")) - \
                                   datetime.timedelta(minutes=30))
            print("new worldbosstime: " + str(self.activationtime))

    def __writeworldbosstime(self, hours, minutes):
        newtime = int(time.time()) + int(hours) * 60 * 60 + int(minutes) * 60
        file = open(self.pathManager.getpath("worldbosstime.txt"), "w")
        file.write("0\n" + str(newtime))
        file.close()

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
        timedifference = (self.activationtime + datetime.timedelta(minutes=30)) - datetime.datetime.now()
        return f"world boss starting in {int(timedifference.total_seconds() / 60)} minutes!"

    def hasCooldown(self) -> bool:
        return not (not super().hasCooldown() and not worldbosssent(self.pathManager.getpath("worldbosstime.txt")))

    def __bool__(self):
        now = datetime.datetime.now()
        return self.activationtime is not None and not self.hasCooldown() and \
                self.activationtime <= now <= (self.activationtime + datetime.timedelta(minutes=30))

    async def __call__(self, client):
        await super().__call__(client)
        self.announcementSent()
