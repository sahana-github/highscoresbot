from .clanevent import ClanEvent


class Elite4(ClanEvent):
    """
    This is an event that happens when any player defeats an elite 4.
    """
    def __init__(self, player: str, region: str):
        """
        calls the init of the superclass and sets the region that the player beat.
        :param player: the player that defeated an elite 4.
        :param region: the elite 4 of what region was beat.
        """
        self.region = region
        self.EVENTNAME = "elite4"
        super(Elite4, self).__init__(player)

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
        return f"{self.player} has beat the {self.region} Elite 4!"
