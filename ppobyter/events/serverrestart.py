from .event import Event


class ServerRestart(Event):
    """
    This event gets triggered when a serverrestart happens in 10 minutes.
    """
    def __init__(self):
        """
        calls init of superclass.
        """
        self.EVENTNAME = "serverrestart"
        super(ServerRestart, self).__init__()

    def makeMessage(self) -> str:
        """
        Makes the message that gets sent to the recipients.
        :return: the message.
        """
        return f"Server restarting in 10 minutes."

    def determineRecipients(self):
        """
        determines the channels where the event must be sent to.
        """
        self._determinechannelrecipients()
