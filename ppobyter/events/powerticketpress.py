import time

from pathmanager import PathManager


class Powerticketpress:
    """
    This gets triggered when the power ticket gets pressed.
    It gets treated as an event to handle it.
    """
    def __init__(self, hours: int, minutes: int):
        """
        Sets the minutes and hours from now the worldboss gets active.
        :param hours:
        :param minutes:
        """
        self.hours = hours
        self.minutes = minutes
        self.pathManager = PathManager()

    async def __call__(self, client: any):
        """
        Writes the timestamp a worldboss occures to a file. Together with a boolean that indicates that the announcement
        that gets sent 30 minutes before the worldboss occurs is not sent yet.
        :param client: an argument that gets passed cause this class is treated as an event. But it won't matter what is
                passed. The parameter won't get used in this method.
        """
        newtime = int(time.time()) + int(self.hours) * 60 * 60 + int(self.minutes) * 60
        file = open(self.pathManager.getpath("worldbosstime.txt"), "w")
        file.write("0\n" + str(newtime))
        file.close()
