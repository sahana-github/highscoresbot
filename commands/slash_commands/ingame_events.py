from discord import app_commands, Interaction
from discord.ext import commands
from commands.command_functionality import ingame_events
from commands.sendable import Sendable


class IngameEvents(commands.Cog):
    def __init__(self, client: commands.bot):
        self.client: commands.bot = client

    ingameeventsgroup = app_commands.Group(name="ingame-events",
                                           description="deals with stuff that has been acquired from inside the game itself")

    @ingameeventsgroup.command(name="lastonline")
    async def lastonline(self, interaction: Interaction, playername: str=None):
        sendable = Sendable(interaction)
        await ingame_events.lastonline(sendable, playername)

    @ingameeventsgroup.command(name="getencounters")
    async def getencounters(self, interaction: Interaction, name: str):
        sendable = Sendable(interaction)
        await ingame_events.getencounters(sendable, name)

    @ingameeventsgroup.command(name="getchests")
    async def getchests(self, interaction: Interaction, argument: str):
        sendable = Sendable(interaction)
        await ingame_events.getchests(sendable, argument)

    @ingameeventsgroup.command(name="getrolls")
    async def getrolls(self, interaction: Interaction, parameter: str):
        sendable = Sendable(interaction)
        await ingame_events.getrolls(sendable, parameter)

    @ingameeventsgroup.command(name="getclanencounters")
    async def getclanencounters(self, interaction: Interaction, clanname: str):
        sendable = Sendable(interaction)
        await ingame_events.getclanencounters(sendable, clanname)

    @ingameeventsgroup.command(name="worldbosstime")
    async def worldbosstime(self, interaction: Interaction):
        sendable = Sendable(interaction)
        await ingame_events.worldbosstime(sendable)


async def setup(client):
    await client.add_cog(IngameEvents(client))
