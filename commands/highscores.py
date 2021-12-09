import asyncio
import sqlite3
from typing import Union

from discord.ext.commands import Command, Context
from discord_components import Select, SelectOption, Interaction, ButtonStyle, Button

from commands.utils import tablify, joinmessages
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
        highscorenames = []
        for highscore in allhighscores:
            highscore = highscore()
            highscorenames.append(highscore.NAME)

        selects = [
            Select(placeholder="Select the highscore you want to see.",
                   options=[SelectOption(label=highscore,
                                         value=highscore)
                            for highscore in highscorenames], )
        ]
        selectids = [selection.id for selection in selects]
        originalmsg = await ctx.send("Select the highscore you want to see.", components=selects)
        try:
            event: Interaction = await self.client.wait_for("select_option",
                                                            check=lambda selection:
                                                            ctx.channel == selection.channel
                                                            and ctx.author == selection.author
                                                            and selection.component.id in selectids,
                                                            timeout=30)
            await event.send(f"showing highscore {event.values[0]}")
        except asyncio.TimeoutError:
            await originalmsg.delete()
            return
        highscoretype = event.values[0]
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
        for highscore in allhighscores:
            highscore = highscore()
            if highscore.NAME == highscoretype:
                break

        try:
            values = highscore.getDbValues(query="SELECT * FROM {0} WHERE clan=? OR rank<10".format(highscore.NAME),
                                           params=[(clanname.lower() if clanname is not None else None)])
        except Exception as e:
            print(e)
            values = highscore.getDbValues(query="SELECT * FROM {0} WHERE rank<10".format(highscore.NAME))
        messages = tablify(highscore.LAYOUT, values)
        for i in messages:
            await ctx.send(i)

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

        selects = [
            Select(placeholder="Select the highscore you want to see.",
                   options=[SelectOption(label=highscore,
                                         value=highscore)
                            for highscore in initializedhighscores.keys()], )
        ]
        selectids = [selection.id for selection in selects]
        originalmsg = await ctx.send("Select the highscore you want to see.", components=selects)
        try:
            event: Interaction = await self.client.wait_for("select_option",
                                                            check=lambda selection:
                                                            ctx.channel == selection.channel
                                                            and ctx.author == selection.author
                                                            and selection.component.id in selectids,
                                                            timeout=30)
            await event.send(f"showing highscore {event.values[0]}")
        except asyncio.TimeoutError:
            await originalmsg.delete()
            return

        buttons = [Button(style=ButtonStyle.blue, label="<<"),
                   Button(style=ButtonStyle.blue, label="<"),
                   Button(style=ButtonStyle.red, label=">"),
                   Button(style=ButtonStyle.red, label=">>")]
        loopedHighscore = LoopedHighscore(initializedhighscores[event.values[0]])

        def check(res):
            return res.channel == ctx.channel and res.author == ctx.author and \
                   res.component.id in [button.id for button in buttons]

        msg = await ctx.send(loopedHighscore.change_page(0), components=[buttons], )
        await originalmsg.delete()
        while True:
            try:
                res = await self.client.wait_for("button_click", check=check, timeout=60)
                if res.component.label == "<":
                    await res.edit_origin(loopedHighscore.change_page(0 - loopedHighscore.size))
                elif res.component.label == ">":
                    await res.edit_origin(loopedHighscore.change_page(loopedHighscore.size))
                elif res.component.label == "<<":
                    await res.edit_origin(loopedHighscore.change_page(loopedHighscore.MINRANK, True))
                elif res.component.label == ">>":
                    await res.edit_origin(loopedHighscore.change_page(loopedHighscore.MAXRANK - loopedHighscore.size,
                                                                      True))
            except asyncio.TimeoutError:
                for button in buttons:
                    button.set_disabled(True)
                await msg.edit(loopedHighscore.change_page(0), components=[buttons])
                break


class LoopedHighscore:
    def __init__(self, highscore: Highscore):
        self.min = 1
        self.size = 20
        self.highscore = highscore
        self.MAXRANK = highscore.getDbValues(f"SELECT rank FROM {highscore.NAME} ORDER BY rank DESC LIMIT 1")[0][0]
        self.MINRANK = 1

    def change_page(self, movement, absolute=False):

        if absolute:
            self.min = movement
        else:
            newmin = self.min + movement
            if newmin + movement > self.MAXRANK:
                self.min = self.MAXRANK - self.size
            elif newmin < self.MINRANK:
                self.min = self.MINRANK
            else:
                self.min += movement
        msg = self.getmsg()
        return msg

    def getmsg(self):
        values = self.highscore.getDbValues(query=f"SELECT * FROM {self.highscore.NAME} WHERE rank >= ? AND rank <= ?",
                                            params=[self.min, self.min + self.size])
        return tablify(self.highscore.LAYOUT, values)[0]


def setup(client):
    client.add_cog(Highscores(client))
