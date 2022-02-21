import os
from typing import List

import nest_asyncio  # this makes the discord client useable together with pyshark.

from ppobyter.eventdeterminer import EventDeterminer
from ppobyter.eventmaker import EventMaker
from ppobyter.events.clanwars import Clanwars
from ppobyter.events.timedevent import TimedEvent
from ppobyter.events.worldblessing import WorldBlessing
from ppobyter.events.worldbosssoon import WorldbossSoon
from ppobyter.eventscheduler import EventScheduler
from pysharkwrapper import PysharkWrapper
from discord import Client
nest_asyncio.apply()


class Main:
    def __init__(self):
        self.__pysharkwrapper = PysharkWrapper()
        self.__client = Client()
        self.__scheduler = EventScheduler(self.__client)
        self.__tasks: List[TimedEvent] = []
        self.__tasks.append(WorldBlessing())
        self.__tasks.append(WorldbossSoon())
        self.__tasks.append(Clanwars())

    async def mainloop(self):
        await self.__client.wait_until_ready()
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
            self.handleTimedEvents(message)
            await self.__scheduler.handleEvent()
        print("end")

    def handleTimedEvents(self, message):
        for task in self.__tasks:
            task.messageProcesser(message)
            if task:
                self.__scheduler.addEvent(task)

    def run(self):
        self.__client.loop.create_task(self.mainloop())
        self.__client.run(os.environ.get("token"))


if __name__ == "__main__":
    Main().run()
