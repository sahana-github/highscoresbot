import sqlite3
from typing import Union

from discord import User
from discord.ext import commands
from discord.ext.commands import Command

from commands.sendable import Sendable
from commands.utils.utils import tablify
from highscores import clanhighscores, RichestClans, BestClans
from highscores.highscore import Highscore
from commands.command_functionality.highscores import get_clancommands, get_top10cmds


class MsgContentHighscores(commands.Cog):
    def __init__(self, client):
        self.client: commands.bot.Bot = client
        self.databasepath = "highscores.db"
        self.makeClanCommands()
        self.makeTop10Commands()

    @commands.command(name="testcmd")
    async def testcmd(self, ctx):
        cmd = list(get_clancommands().values())[0]
        print(cmd)
        sendable = Sendable(ctx.author)
        await cmd(sendable, "nightraiders")

    def makeClanCommands(self):
        for name, cmd in get_clancommands().items():
            self.client.add_command(commands.command(name=name)(cmd))

    def makeTop10Commands(self):
        for name, cmd in get_top10cmds().items():
            self.client.add_command(commands.command(name=name)(cmd))


async def setup(client: commands.Bot):
    await client.add_cog(MsgContentHighscores(client))
