import datetime
import re
from ppobyter.events.timedevent import TimedEvent


class WorldBlessing(TimedEvent):
    """
    This event triggers 2 minutes before the expiring of the worldblessing.
    """
    def __init__(self):
        """
        calls the superclass init.
        """
        self.EVENTNAME = "worldblessing"
        super(WorldBlessing, self).__init__(datetime.timedelta(minutes=30))

    def messageProcesser(self, message: str):
        pattern = r"(?<=<\/var><var n='d' t='s'>)([0-9]+:[0-9]+)(?=<\/var><var n='a' t='n'>1.1</var><var n='_cmd' t='s'>" \
                  r"worldBlessing<\/var><\/dataObj>]]><\/body><\/msg>)"
        if re.search(pattern, message):
            print("activation time set.")
            self.setActivationTime(datetime.datetime.now() + datetime.timedelta(minutes=57))

    def determineRecipients(self):
        """
        Determines the recipients for channels.
        """
        self._determinechannelrecipients()

    def makeMessage(self) -> str:
        """
        Makes the message that gets sent to the recipients.
        :return: the message
        """
        return "world blessing expiring in 2 minutes!"

    def __bool__(self):
        now = datetime.datetime.now()
        return self.activationtime is not None and not self.hasCooldown() and self.activationtime <= now <= \
               (self.activationtime + datetime.timedelta(minutes=3))
