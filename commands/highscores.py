import re
import sqlite3

from discord.ext.commands import Command
from commands.utils import tablify, joinmessages
from discord.ext import commands
from commands.highscores_database import Database
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
                async def cmd(ctx, clanname):
                    if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
                        return
                    messages = tablify(score.LAYOUT, score.getDbValues(clan=clanname))
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

    @commands.command(name="getplayer")
    async def getplayer(self, ctx, username):
        """
        gets a collection of highscores a player is in.
        :param username:
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
    async def mapcontrol(self, ctx, clanname = None):
        """
        shows the standings of all mapcontrol areas.
        :param clanname
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
                clan=clanname))
            messages.append(area)
            messages += values
        messages = joinmessages(messages)
        for i in messages:
            await ctx.send(i)

    @commands.command(name="top")
    async def top(self, ctx, highscoretype, clanname=None):
        """
        shows top 9 + the provided clan.
        :param highscoretype: the type of highscore
        :param clanname: the clanname, default none, clannamehandler gets clan from db if none.
        :return:
        """
        if clanname is None:
            clanname = await self.getdefaultclanname(ctx, comment=False)
        highscoretype = highscoretype.lower()
        if highscoretype == "btwins" or highscoretype == "btwinstreak":
            values = []
            clanlist = getClanList(clanname.lower()) if clanname is not None else []
            highscore = Btwinstreak() if highscoretype == "btwinstreak" else Btwins()
            for row in highscore.getDbValues():
                if row[1] in clanlist or row[0] < 10:
                    values.append(row)
            resultmessages = tablify(highscore.LAYOUT, values)
            for msg in resultmessages:
                await ctx.send(msg)
            return
        for highscore in clanhighscores:
            highscore = highscore()
            if highscore.NAME == highscoretype:
                break
        else:
            await ctx.send("No valid highscore was given! Possible highscores:```" +
                           "\n".join(highscore().NAME for highscore in clanhighscores) + "```")
            return


        values = highscore.getDbValues(query="SELECT * FROM {0} WHERE clan=? OR rank<10".format(highscore.NAME),
                                       params=[(clanname.lower() if clanname is not None else None)])

        messages = tablify(highscore.LAYOUT, values)
        for i in messages:
            await ctx.send(i)

    @commands.command(name="getclan")
    async def getclan(self, ctx, clanname):
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

    async def getdefaultclanname(self, ctx, comment=True) -> str:
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


def setup(client):
    client.add_cog(Highscores(client))
