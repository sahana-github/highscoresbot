import asyncio
import sqlite3
from typing import Union

from discord.ext.commands import Command, Context

from commands.interractions.highscore_command import HighscoreCommand
from commands.interractions.selectsview import SelectsView
from commands.interractions.top_command import TopCommand
from commands.utils.utils import tablify, joinmessages
from discord.ext import commands
from highscores import *
from highscores.highscore import Highscore


class Highscores(commands.Cog):
    def __init__(self, client):
        self.client: commands.bot.Bot = client
        self.databasepath = "highscores.db"
        self.makeClanCommands()

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

    @commands.command(name="getplayer")
    async def getplayer(self, ctx: Context, username: str):
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
            await ctx.send("or {0} is not in any highscore or he does not exist.".format(username))
        else:
            for i in allmessages:
                await ctx.send(i)

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
    async def btwinstreak(self, ctx, clanname=None):
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        values = []
        clanlist = getClanList(clanname.lower())
        btwinstreak = Btwinstreak()
        for row in btwinstreak.getDbValues():
            if row[1] in clanlist:
                values.append(row)
        resultmessages = tablify(btwinstreak.LAYOUT, values)
        for message in resultmessages:
            await ctx.send(message)

    @commands.command(name="mapcontrol")
    async def mapcontrol(self, ctx, clanname: str = None):
        """
        shows the standings of all mapcontrol areas.
        :param ctx: discord context
        :param clanname: the name of the clan, optional.
        """
        mapcontrolhighscores = [(AncMapcontrol, "Ancient cave"), (BzMapcontrol, "Battle zone"),
                                (SafariMapcontrol, "Safari zone")]
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
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
        for i in messages:
            await ctx.send(i)

    @commands.command(name="top")
    async def top(self, ctx: Context, clanname=None):
        """
        shows top 9 + the provided clan if available.
        :param ctx: discord context
        :param clanname: the clanname, default none, clannamehandler gets clan from db if none.
        """
        if clanname is None:
            clanname = await self.getdefaultclanname(ctx, comment=False)
        highscoresdict = {}
        for highscore in allhighscores:
            highscore = highscore()
            highscoresdict[highscore.NAME] = highscore

        def highscoreselectionmaker(highscores):
            return TopCommand(ctx, highscores, clanname)

        view = SelectsView(ctx, highscoresdict, highscoreselectionmaker)
        await ctx.send(content=f"page {view.currentpage} of {view.maxpage}", view=view)

    @commands.command(name="getclan")
    async def getclan(self, ctx, clanname: str):
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
            await ctx.send(f"The clan {clanname} is not in the highscores or does not exist.")
            return
        for message in allmessages:
            await ctx.send(message)

    async def getdefaultclanname(self, ctx, comment=True) -> Union[str, None]:
        if ctx.guild is None:
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT name FROM clannames WHERE id=?", (ctx.guild.id,))
        try:
            clanname = cur.fetchall()[0][0]
        except IndexError:
            clanname = None
        if clanname is None and comment:
            await ctx.send("Please register a default clanname or provide a clan in the command.")
        elif clanname is not None:
            clanname = clanname.lower()
        return clanname

    @commands.command(name="highscore")
    async def highscore(self, ctx):
        initializedhighscores = {}
        for highscore in allhighscores:
            highscore = highscore()
            initializedhighscores[highscore.NAME] = highscore

        def highscoreselectionmaker(highscores):
            return HighscoreCommand(ctx, highscores)

        view = SelectsView(ctx, initializedhighscores.keys(), highscoreselectionmaker)
        await ctx.send(content=f"page {view.currentpage} of {view.maxpage}", view=view)


def setup(client):
    client.add_cog(Highscores(client))
