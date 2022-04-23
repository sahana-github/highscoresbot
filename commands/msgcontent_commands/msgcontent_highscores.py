import sqlite3
from typing import Union

import discord

from commands.interractions.discord_binder import DiscordBinder
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

    #user = get(bot.get_all_members(), id="1234")
    @commands.command(name="testcmd")
    async def testcmd(self, ctx):
        embed = discord.Embed(title="Accountbinding",
                              description="{user} has requested to bind his ppo account with your discord account!")
        embed.add_field(name="what does this mean?",
                        value="That means that the commands done in any local chat ingame (like `.lle nightraiders`) "
                              "would be sent to your discord account.", inline=False)
        embed.add_field(name="this wasn't me",
                        value="you could deny this specific ppo user from binding with your discord account,"
                              " and he won't be able to send future requests to bind to your user account (you can undo this with a command on discord).",
                        inline=False)
        embed.add_field(name="I don't want any message about this in the future",
                        value="you can press `prevent all accountbinding in the future` if you don't want any messages"
                              " like this one at all anymore. This can be undone with `{future_command}` in discord",
                        inline=False)

        await ctx.send(embed=embed, view=DiscordBinder("henkjan", 5))
        # for member in self.client.get_all_members():
        #     yield member
        #     print(member.name)
        #self.client.get_all_members()
        # cmd = list(get_clancommands().values())[0]
        # print(cmd)
        # sendable = Sendable(ctx.author)
        # await cmd(sendable, "nightraiders")

    def makeClanCommands(self):
        for name, cmd in get_clancommands().items():
            self.client.add_command(commands.command(name=name)(cmd))

    def makeTop10Commands(self):
        for name, cmd in get_top10cmds().items():
            self.client.add_command(commands.command(name=name)(cmd))


async def setup(client: commands.Bot):
    await client.add_cog(MsgContentHighscores(client))
