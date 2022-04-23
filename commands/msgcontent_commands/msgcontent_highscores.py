import sqlite3
from typing import Union

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

    def makeClanCommands(self):
        for cmd in get_clancommands():
            self.client.add_command(cmd)

    def makeTop10Commands(self):
        for cmd in get_top10cmds():
            self.client.add_command(cmd)


async def setup(client: commands.Bot):
    await client.add_cog(MsgContentHighscores(client))
