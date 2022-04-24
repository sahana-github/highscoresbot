import asyncio
import os
import threading
from typing import List, Any

import discord
import nest_asyncio  # this makes the discord client useable together with pyshark.
from discord.ext import tasks

from commands.ingame_commands.highscores import get_clancommands
from commands.ingame_commands.discordbinding import bind, unbind, unbindall
from commands.ingame_commands.miscellaneous import helpcmd
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
from discord import Client, User

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
        self._messages = []

    def attachCommands(self):
        self.ingamecommandclient.register_command("bind", bind, binding_not_required=True)
        for cmdname, cmd in get_clancommands().items():
            self.ingamecommandclient.register_command(cmdname, cmd)
        self.ingamecommandclient.register_command("unbind", unbind, binding_not_required=True)
        self.ingamecommandclient.register_command("unbindall", unbindall)  # if user has no bindings, command will be useless anyway
        self.ingamecommandclient.register_command("help", helpcmd)

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.running:
            t = threading.Thread(target=self.messagegetter)
            t.start()
            await self.messageprocesser_.start()

            self.running = True

    def messagegetter(self):
        """
        constantly adds messages to the message list.
        """
        cap = self.__pysharkwrapper.cap()
        for message in cap:
            self._messages.append(message)

    @tasks.loop(seconds=4)
    async def messageprocesser_(self):
        """
        gets through all messages in the messagelist and processes them. Also clears the list.
        """
        while len(self._messages) != 0:
            message = self._messages[len(self._messages)-1]
            self._messages.pop(len(self._messages)-1)
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

    def handleTimedEvents(self, message):
        for task in self.__tasks:
            task.messageProcesser(message)
            if task:
                self.__scheduler.addEvent(task)

    def run(self):
        super(Main, self).run(token=self.__token)


if __name__ == "__main__":
    Main(token=os.environ.get("token")).run()
