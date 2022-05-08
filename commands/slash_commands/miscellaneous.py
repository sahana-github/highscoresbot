import discord
from discord import app_commands, Interaction
from discord.ext import commands

from commands.sendable import Sendable
from commands.command_functionality import miscellaneous


class Miscellaneous(commands.Cog):
    def __init__(self, client: discord.ext.commands.bot):
        self.client: discord.ext.commands.bot.Bot = client

    miscellaneousgroup = app_commands.Group(name="miscellaneous", description="random commands that don't have a category")

    @miscellaneousgroup.command(name="invite")
    async def invite(self, interaction: Interaction):
        sendable = Sendable(interaction)
        await miscellaneous.invite(sendable)

    @miscellaneousgroup.command(name="clanlist")
    async def clanlist(self, interaction: Interaction, clanname: str):
        sendable = Sendable(interaction)
        await miscellaneous.clanlist(sendable, clanname)

    @miscellaneousgroup.command(name="setdefault")
    async def setdefault(self, interaction: Interaction, clanname: str = None):
        sendable = Sendable(interaction)
        await miscellaneous.setdefault(sendable, clanname)

    @miscellaneousgroup.command(name="worldboss")
    async def worldboss(self, interaction: Interaction, playername: str):
        sendable = Sendable(interaction)
        await miscellaneous.worldboss(sendable, playername)

    @miscellaneousgroup.command(name="gmsearch")
    async def gmsearch(self, interaction: Interaction, searchstring: str):
        sendable = Sendable(interaction)
        await miscellaneous.gmsearch(sendable, searchstring)

    @miscellaneousgroup.command(name="help")
    async def help(self, interaction: Interaction):
        sendable = Sendable(interaction)
        await miscellaneous.help(sendable)


async def setup(client):
    client.remove_command('help')
    await client.add_cog(Miscellaneous(client))
