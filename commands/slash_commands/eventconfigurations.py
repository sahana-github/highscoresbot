import discord
from discord import app_commands, Interaction
from discord.ext import commands
import sqlite3
from commands.command_functionality import eventconfigurations
from commands.sendable import Sendable


class Eventconfigurations(commands.Cog):
    """
    responsible for making sure the functionality gets the right parameters.
    """
    def __init__(self, client: commands.bot.Bot):
        self.client = client

    eventconfiggroup = app_commands.Group(name="eventconfig",
                                          description="configurate ingame events to be sent in certain channels")

    @eventconfiggroup.command(name="setperms")
    async def setperms(self, interaction: Interaction, role: discord.Role):
        """
        This command gives permission to the specified role to adjust eventconfigurations for this server.
        Only useable by administrators of the server.
        :param ctx: discord context
        :param role: the role id or the role mention. Union[int, str]
        """
        sendable = Sendable(interaction)
        await eventconfigurations.setperms(sendable, role)

    @eventconfiggroup.command(name="removeperms")
    async def removeperms(self, interaction: Interaction, role: discord.Role):
        sendable = Sendable(interaction)
        await eventconfigurations.removeperms(sendable, role)

    @eventconfiggroup.command(name="getperms")
    async def getperms(self, interaction: Interaction):
        sendable = Sendable(interaction)
        await eventconfigurations.getperms(sendable)

    @eventconfiggroup.command(name="register")
    async def register(self, interaction: Interaction, channel: discord.TextChannel = None):
        sendable = Sendable(interaction)
        await eventconfigurations.register(sendable, channel)

    @eventconfiggroup.command(name="settime")
    async def settime(self, interaction: Interaction, eventname: str, time: int = None):
        sendable = Sendable(interaction)
        await eventconfigurations.settime(sendable, eventname, time)

    @eventconfiggroup.command(name="getclanregistrations")
    async def getclanregistrations(self, interaction: Interaction):
        sendable = Sendable(interaction)
        await eventconfigurations.getclanregistrations(sendable)

    @eventconfiggroup.command(name="showregistrations")
    async def showregistrations(self, interaction: Interaction):
        sendable = Sendable(interaction)
        await eventconfigurations.showregistrations(sendable, self.client)

    @eventconfiggroup.command(name="unregisterclan")
    async def unregisterclan(self, interaction: Interaction, clanname: str):
        sendable = Sendable(interaction)
        await eventconfigurations.unregisterclan(sendable, clanname)

    @eventconfiggroup.command(name="registerclan")
    async def registerclan(self, interaction: Interaction, clanname: str):
        sendable = Sendable(interaction)
        await eventconfigurations.registerclan(sendable, clanname)

    @eventconfiggroup.command(name="unregister")
    async def unregister(self, interaction: Interaction, eventname: str):
        sendable = Sendable(interaction)
        await eventconfigurations.unregister(sendable, eventname)

    @eventconfiggroup.command(name="setpingrole")
    async def setpingrole(self, interaction: Interaction, eventname: str, pingrole: discord.Role):
        sendable = Sendable(interaction)
        await eventconfigurations.setpingrole(sendable, eventname, pingrole)

    @eventconfiggroup.command(name="removeping")
    async def removeping(self, interaction: Interaction, eventname: str):
        sendable = Sendable(interaction)
        await eventconfigurations.removeping(sendable, eventname)

    @eventconfiggroup.command(name="playerconfig")
    async def playerconfig(self, interaction: Interaction, player: str = None):
        sendable = Sendable(interaction)
        await eventconfigurations.playerconfig(sendable, player)


async def setup(client):
    await client.add_cog(Eventconfigurations(client))
