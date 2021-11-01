import sqlite3
from pathmanager import PathManager
import discord
from typing import Union


class Event:
    """
    This is the baseclass of an event. It can determine channelrecipients based on the eventname provided.
    When you call this class the event will be sent.
    """
    def __init__(self):
        """
        Here pingroles, recipients, alivetime and pmrecipients are initialized.
        It also calls the determineRecipients method.
        """
        self.pathManager = PathManager()
        self.EVENTNAME: str
        # pingroles should be same size as recipients.
        self._pingroles = []
        self._recipients = []
        self._alive_time = []
        self._pmrecipients = []
        self.determineRecipients()

    def determineRecipients(self, **kwargs):
        """
        Here pingroles, recipients, alivetime and pmrecipients are determined. This method should be overridden.
        :param kwargs:
        :raise NotImplementedError if it's not implemented.
        """
        raise NotImplementedError

    def _determinechannelrecipients(self):
        """
        Base method for determining channel recipients based on eventname.
        :return:
        """
        conn = sqlite3.connect(self.pathManager.getpath("eventconfigurations.db"))
        cur = conn.cursor()
        cur.execute("SELECT channel, pingrole, alivetime FROM eventconfig WHERE eventname=? AND channel is not null", (self.EVENTNAME,))
        result = cur.fetchall()
        self._recipients = [row[0] for row in result]
        self._pingroles = [row[1] for row in result]
        self._alive_time = [row[2] for row in result]
        conn.close()

    def makeMessage(self) -> Union[str, discord.Embed]:
        """
        Here the message that must be sent gets made.
        :return: either a discord embed or a string that must be sent.
        :raises NotImplementedError if this method is not implemented in the subclass.
        """
        raise NotImplementedError

    async def __call__(self, client: discord.client.Client):
        """
        send the event to all recipients.
        :param client, the discord client
        """
        for channelindex in range(len(self._recipients)):
            try:
                chan = await client.fetch_channel(self._recipients[channelindex])
                msg = self.makeMessage()
                if self._pingroles and self._pingroles[channelindex] is not None and type(msg) != discord.Embed:
                    msg += f"<@&{self._pingroles[channelindex]}>"
                if type(msg) == discord.embeds.Embed:
                    if self._alive_time[channelindex] is not None:
                        await chan.send(embed=msg, delete_after=self._alive_time[channelindex]*60)
                    else:
                        await chan.send(embed=msg)
                else:
                    if self._alive_time[channelindex] is not None:
                        await chan.send(msg, delete_after=self._alive_time[channelindex]*60)
                    else:
                        await chan.send(msg)
            except Exception as e:
                # probably 403 forbidden exceptions etc, those exceptions will be catched and ignored in the future.
                print(e)
        for user in self._pmrecipients:
            try:
                user = await client.fetch_user(user)
                await user.send(self.makeMessage())
            except Exception as e:
                # probably 403 forbidden exceptions etc, those exceptions will be catched and ignored in the future.
                print(e)
