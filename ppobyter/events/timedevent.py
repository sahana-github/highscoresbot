import datetime
from typing import Union

import discord

from ppobyter.events.event import Event


class TimedEvent(Event):
    """
    This class is an event based on timing, it is in the first place initiated by the server but the actual event is
    has not started yet.
    """
    def __init__(self, cooldown: datetime.timedelta):
        """
        :param cooldown: how long the event should wait before beïng able to be repeated.
        :param amount: how many times the event should be repeated.
        """
        self.cooldown = cooldown
        super().__init__()
        self._pingroles = []
        self._recipients = []
        self._alive_time = []
        self._pmrecipients = []
        self.activationtime = None
        self.lastsent = None

    def setActivationTime(self, activationtime):
        self.activationtime = activationtime

    def determineRecipients(self):
        self._pingroles = []
        self._recipients = []
        self._alive_time = []
        self._pmrecipients = []
        self._determinechannelrecipients()

    def hasCooldown(self) -> bool:
        if self.lastsent is not None:
            return datetime.datetime.now() < self.lastsent + self.cooldown
        return False

    def messageProcesser(self, message: str):
        raise NotImplementedError

    async def __call__(self, client: discord.client.Client):
        """
        sends the event
        :param client:
        :return:
        """
        print("timed event called.")
        self.lastsent = datetime.datetime.now()
        self.determineRecipients()
        await super().__call__(client)

    def __bool__(self):
        """
        returns if the event can be sent.
        """
        raise NotImplementedError
