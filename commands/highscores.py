import asyncio
import sqlite3
from typing import Union

import discord
from discord import app_commands, Interaction
from discord.ext.commands import Command, Context

from commands.interractions.highscore_command import HighscoreCommand
from commands.interractions.resultmessageshower import ResultmessageShower
from commands.interractions.selectsview import SelectsView
from commands.interractions.top_command import TopCommand
from commands.sendable import Sendable
from commands.utils.utils import tablify, joinmessages
from discord.ext import commands
from highscores import *
from highscores.highscore import Highscore


class Highscores(commands.Cog):
    def __init__(self, client):
        self.client: commands.bot.Bot = client
        self.databasepath = "highscores.db"
        self.makeClanCommands()
        self.makeTop10Commands()

    def makeClanCommands(self):
        for highscore in clanhighscores:
            highscore = highscore()

            def outer_cmd(score: Highscore) -> Command:
                @commands.command(name=score.NAME)
                async def cmd(ctx, clanname=None):
                    if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
                        return
                    messages = tablify(score.LAYOUT, score.getDbValues(clan=clanname.lower()))
                    for i in messages:
                        await ctx.send(i)
                return cmd

            self.client.add_command(outer_cmd(highscore))

    def makeTop10Commands(self):
        somelist = [RichestClans, BestClans]
        for highscore in somelist:
            highscore = highscore()

            def outer_cmd(score: Highscore) -> Command:
                @commands.command(name=score.NAME)
                async def cmd(ctx, clanname=None):
                    if clanname is None and ((clanname := await self.getdefaultclanname(ctx, comment=False)) is None):
                        clanname = ""
                    values = score.getDbValues(query="SELECT * FROM {0} WHERE rank < 10 or name = ?".format(score.NAME),
                                               clan=clanname.lower())
                    resultmessages = tablify(score.LAYOUT, values)
                    for i in resultmessages:
                        await ctx.send(i)

                return cmd

            self.client.add_command(outer_cmd(highscore))

    highscoresgroup = app_commands.Group(name="highscores",
                                         description="all commands that have to do directly with all the highscores of pokemon planet.")

    @highscoresgroup.command(name="getplayer")
    async def getplayer(self, sendable: Sendable, username: str):
        """
        gets a collection of highscores a player is in.
        :param ctx: discord context
        :param username: the name of the player you want info from.
        """
        username = username.lower()
        allmessages = []
        for highscore in allhighscores:
            highscore = highscore()
            try:
                values = highscore.getDbValues(query="SELECT * FROM {0} WHERE username=?".format(highscore.NAME),
                                               params=[username])
                if (newmessages := tablify(highscore.LAYOUT, values))[0] != "No results found.":
                    allmessages += newmessages
            except sqlite3.OperationalError:
                pass

        allmessages = joinmessages(allmessages)

        if len(allmessages) == 0:
            await sendable.send("or {0} is not in any highscore or he does not exist.".format(username))
        else:
            view = ResultmessageShower(allmessages, sendable)
            await sendable.send(allmessages[0], view=view)

    @commands.command(name="btwins")
    async def btwins(self, ctx, clanname=None):
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        values = []
        clanlist = getClanList(clanname.lower())
        btwins = Btwins()
        for row in btwins.getDbValues():
            if row[1] in clanlist:
                values.append(row)
        resultmessages = tablify(btwins.LAYOUT, values)
        for message in resultmessages:
            await ctx.send(message)

    @commands.command(name="btwinstreak")
    async def btwinstreak(self, interaction, clanname=None):
        if clanname is None and ((clanname := await self.getdefaultclanname(interaction)) is None):
            return
        values = []
        clanlist = getClanList(clanname.lower())
        btwinstreak = Btwinstreak()
        for row in btwinstreak.getDbValues():
            if row[1] in clanlist:
                values.append(row)
        resultmessages = tablify(btwinstreak.LAYOUT, values)
        view = ResultmessageShower(resultmessages, interaction)

    @highscoresgroup.command(name="mapcontrol")
    async def mapcontrol(self, interaction, clanname: str = None):
        """
        shows the standings of all mapcontrol areas.
        :param ctx: discord context
        :param clanname: the name of the clan, optional.
        """
        mapcontrolhighscores = [(AncMapcontrol, "Ancient cave"), (BzMapcontrol, "Battle zone"),
                                (SafariMapcontrol, "Safari zone")]
        if clanname is None and ((clanname := await self.getdefaultclanname(interaction)) is None):
            clanname = ""
        messages = []
        for highscore, area in mapcontrolhighscores:
            highscore = highscore()
            values = tablify(highscore.LAYOUT, highscore.getDbValues(
                query=f"SELECT * FROM {highscore.NAME} WHERE rank < 10 or clan=?",
                clan=clanname.lower()))
            messages.append(area)
            messages += values
        messages = joinmessages(messages)
        view = ResultmessageShower(messages, interaction)
        await interaction.response.send_message(messages[0], view=view)

    @highscoresgroup.command(name="top")
    async def top(self, interaction: Interaction, clanname: str=None):
        """
        shows top 9 + the provided clan if available.
        :param ctx: discord context
        :param clanname: the clanname, default none, clannamehandler gets clan from db if none.
        """
        if clanname is None:
            clanname = await self.getdefaultclanname(interaction, comment=False)
        highscoresdict = {}
        for highscore in allhighscores:
            highscore = highscore()
            highscoresdict[highscore.NAME] = highscore

        def highscoreselectionmaker(highscores):
            return TopCommand(interaction, highscores, clanname)

        view = SelectsView(interaction, highscoresdict, highscoreselectionmaker)
        await interaction.response.send_message(content=f"page {view.currentpage} of {view.maxpage}", view=view)

    @highscoresgroup.command(name="getclan")
    async def getclan(self, interaction: Interaction, clanname: str):
        clanname = clanname.lower()
        getclanhighscores = [(SafariMapcontrol, "Safari zone mapcontrol"),
                             (AncMapcontrol, "Ancient cave mapcontrol"),
                             (BzMapcontrol, "Battle zone mapcontrol"),
                             (BestClans, "Top clan experience"),
                             (RichestClans, "Top richest clans")]
        allmessages = []
        for highscore, name in getclanhighscores:
            highscore = highscore()
            values = highscore.getDbValues(f"SELECT * FROM {highscore.NAME}")
            for i in values:
                if i[1] == clanname:
                    allmessages.append(name)
                    allmessages += tablify(highscore.LAYOUT, [i])
                    break
        allmessages = joinmessages(allmessages)
        if not allmessages:
            await interaction.response.send_message(f"The clan {clanname} is not in the highscores or does not exist.")
            return

        view = ResultmessageShower(allmessages, interaction)
        await interaction.response.send_message(allmessages[0], view=view)

    async def getdefaultclanname(self, interaction, comment=True) -> Union[str, None]:
        if interaction.guild is None:
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT name FROM clannames WHERE id=?", (interaction.guild.id,))
        try:
            clanname = cur.fetchall()[0][0]
        except IndexError:
            clanname = None
        if clanname is None and comment:
            await interaction.response.send_message("Please register a default clanname or provide a clan in the command.")
        elif clanname is not None:
            clanname = clanname.lower()
        return clanname

    @highscoresgroup.command(name="highscore")
    async def highscore(self, interaction: Interaction, clanname: str=None):
        initializedhighscores = {}
        for highscore in allhighscores:
            highscore = highscore()
            initializedhighscores[highscore.NAME] = highscore

        def highscoreselectionmaker(highscores):
            return HighscoreCommand(interaction, highscores, clanname=clanname)

        view = SelectsView(interaction, initializedhighscores.keys(), highscoreselectionmaker)
        await interaction.response.send_message(content=f"page {view.currentpage} of {view.maxpage}", view=view)


async def setup(client: commands.Bot):
    await client.add_cog(Highscores(client))
