"""
TEMP
FOR TESTING ONLY
"""
import datetime

from commands.utils import getworldbosstime, worldbosssent
from eventdeterminer import EventDeterminer
import pyshark
from eventscheduler import EventScheduler
import os
from eventmaker import EventMaker
import discord
from discord import Client
import nest_asyncio
from events.worldbosssoon import WorldbossSoon
from pathmanager import PathManager
from ppobyter.events.worldblessing import WorldBlessing


# this makes the discord client useable together with pyshark.
nest_asyncio.apply()

def decodehex(hexa: str) -> str:
    """
    This takes a hex stream and makes a string from it.
    :param hexa: The hexadecimal string.
    :return: the string made from the hexa.
    """
    result = ""
    temp = ""
    for i in hexa:
        temp += i
        if len(temp) == 2:
            result += chr(int(temp, 16))
            temp = ""
    return result


class Main:
    def __init__(self):
        """
        This initializes the discord client, pyshark and the eventscheduler.
        """
        self.pathManager = PathManager()
        self.__cap = pyshark.LiveCapture(interface="Ethernet 2", include_raw=True, use_json=True, display_filter="ip.src == 167.114.159.20")
        #self.__cap = pyshark.LiveCapture(interface=r"\Device\NPF_{65E2C297-AC80-4851-95C2-795C9783D00F}", include_raw=True,
          #                        use_json=True, display_filter="ip.src == 167.114.159.20")

        self.__client = Client()
        self.__scheduler = EventScheduler(self.__client)

    async def mainloop(self):
        """
        Constantly checks packets and filters them out to check if they contain events.
        If they contain events those get sent to discord recipients.
        """
        await self.__client.wait_until_ready()
        worldbosstime = getworldbosstime(self.pathManager.getpath("worldbosstime.txt"))
        worldblessingtime = None
        for packet in self.__cap.sniff_continuously():
            now = datetime.datetime.now()
            if (now + datetime.timedelta(minutes=30)) > worldbosstime and not \
                    worldbosssent(self.pathManager.getpath("worldbosstime.txt")):
                self.__scheduler.addEvent(WorldbossSoon())
            if worldblessingtime is not None and now > worldblessingtime:
                e = WorldBlessing()
                self.__scheduler.addEvent(e)
                worldblessingtime = None
            try:
                hexa = packet.tcp.payload.replace(":", "")
                r = decodehex(hexa)
                for msg in r.split("\x00"):
                    if msg == "":
                        continue
                    if event := EventDeterminer(msg).determineEvent():
                        if event[0] == "worldblessing":
                            print("worldblessing just got added.")
                            worldblessingtime = now + datetime.timedelta(minutes=58)
                        else:
                            self.__scheduler.addEvent(EventMaker.makeEvent(event[0], **event[1]))

            except AttributeError:
                pass

            if self.__scheduler.eventAvailable():
                print(datetime.datetime.now())
                worldbosstime = getworldbosstime(self.pathManager.getpath("worldbosstime.txt"))
                await self.__scheduler.handleEvent()

    def run(self):
        """
        Creates the mainloop task and runs the bot.
        """
        self.__client.loop.create_task(self.mainloop())
        self.__client.run(os.environ.get("token"))


if __name__ == "__main__":
    #open("./eventconfigurations.db")
    Main().run()