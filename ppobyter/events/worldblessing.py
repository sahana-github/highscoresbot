from ppobyter.events.event import Event


class WorldBlessing(Event):
    """
    This event triggers 2 minutes before the expiring of the worldblessing.
    """
    def __init__(self):
        """
        calls the superclass init.
        """
        self.EVENTNAME = "worldblessing"
        super(WorldBlessing, self).__init__()

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
