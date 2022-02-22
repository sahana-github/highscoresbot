import datetime
from typing import Union

import discord

from ppobyter.events.settimeevent import SettimeEvent


class Clanwars(SettimeEvent):
    """
    Clan Wars is an event held two times every Saturday and Sunday. Clan Wars start at 7:00PM and 7:50PM UTC
    (Tier 1 and Tier 2 respectively).
    """
    def __init__(self):
        self.EVENTNAME = "clanwars"
        self.currenttier = 1
        super().__init__([6, 7], [datetime.time(hour=19, minute=0), datetime.time(hour=19, minute=40)],
                         datetime.timedelta(minutes=15))

    def generateActivationTimes(self):
        super().generateActivationTimes()
        self.currenttier = 1

    def changeTier(self):
        if self.currenttier == 1:
            self.currenttier = 2
        elif self.currenttier == 2:
            self.currenttier = 1

    def makeMessage(self) -> Union[str, discord.Embed]:
        now = datetime.datetime.now()
        timedifference = self.activationtime - now
        return f"tier {self.currenttier} of clan wars is starting in {int(timedifference.total_seconds() / 60)} minutes."

    async def __call__(self, client):
        await super().__call__(client)
        self.changeTier()

    def __bool__(self):
        now = datetime.datetime.now()
        return super().__bool__() and (self.activationtime - datetime.timedelta(minutes=10) <= now <=
                                       self.activationtime)
