import os
from typing import List, Any

import discord
import nest_asyncio  # this makes the discord client useable together with pyshark.

from commands.command_functionality.highscores import get_clancommands
from commands.ingame_commands.discordbinding import bind
from ppobyter.eventdeterminer import EventDeterminer
from ppobyter.eventmaker import EventMaker
from ppobyter.events.clanwars import Clanwars
from ppobyter.events.timedevent import TimedEvent
from ppobyter.events.worldblessing import WorldBlessing
from ppobyter.events.worldbosssoon import WorldbossSoon
from ppobyter.eventscheduler import EventScheduler
from ppobyter.ingame_commands.ingamecommandclient import IngamecommandClient
from ppobyter.ingame_commands.messageprocesser import MessageProcesser
from pysharkwrapper import PysharkWrapper
from discord import Client
nest_asyncio.apply()


class Main(discord.Client):
    def __init__(self, **options: Any):
        super().__init__(**options)
        self.__pysharkwrapper = PysharkWrapper()
        #self.__client = Client()
        self.__scheduler = EventScheduler(self)
        self.__tasks: List[TimedEvent] = []
        self.__tasks.append(WorldBlessing())
        self.__tasks.append(WorldbossSoon())
        self.__tasks.append(Clanwars())
        self.__token = options["token"]
        self.ingamecommandclient = IngamecommandClient(prefix=".", discordclient=self)
        self.attachCommands()
        self.messageprocesser = MessageProcesser()
        self.running = False

    def attachCommands(self):
        self.ingamecommandclient.register_command("bind", bind)
        # for cmdname, cmd in get_clancommands().items():
        #     self.ingamecommandclient.register_command(cmdname, cmd)

    async def on_ready(self):
        if not self.running:
            self.loop.create_task(self.mainloop())
            self.running = True

    async def mainloop(self):
        await self.wait_until_ready()
        cap = self.__pysharkwrapper.cap()
        for message in cap:
            #print(message)
            #print(EventDeterminer(message).determineEvent())
            if event := EventDeterminer(message).determineEvent():
                print(event)

                # if event[0] == "gmsearch":
                #     print("gm searched.")
                #     continue
                self.__scheduler.addEvent(EventMaker.makeEvent(event[0], **event[1]))
            elif self.ingamecommandclient is not None:
                processedmessage = self.messageprocesser.processMessage(message)
                if processedmessage is not None:
                    await self.ingamecommandclient.on_message(processedmessage)
            self.handleTimedEvents(message)
            await self.__scheduler.handleEvent()
        print("end")

    def handleTimedEvents(self, message):
        for task in self.__tasks:
            task.messageProcesser(message)
            if task:
                self.__scheduler.addEvent(task)

    def run(self):
        super(Main, self).run(token=self.__token)


if __name__ == "__main__":
    Main(token=os.environ.get("token")).run()
