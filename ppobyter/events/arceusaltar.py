from .event import Event


class ArceusAltar(Event):
    """
    This class is the arceus altar event.
    """
    def __init__(self, player: str, amount: str):
        """
        here the superclass init is called, and it sets the player and the amount.
        :param player: The player who topped off the altar.
        :param amount: The amount used to top off the altar.
        """
        self.EVENTNAME = "arceusaltar"
        self.player = player
        self.amount = amount
        super(ArceusAltar, self).__init__()

    def makeMessage(self) -> str:
        """
        makes the message to send to the recipients.
        :return: The message to send to the recipients
        """
        return f"{self.player} topped off the Legendary Altar (Arceus) with a donation of {self.amount}!"

    def determineRecipients(self, **kwargs):
        """
        determines the recipients for the event.
        :param kwargs: none required
        """
        self._determinechannelrecipients()
