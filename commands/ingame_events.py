import asyncio
import sqlite3
import datetime
from typing import List

from discord.ext import commands
from discord.ext.commands.context import Context

from commands.interractions.ingame_events.getchests import GetChests
from commands.interractions.ingame_events.getencounters import GetEncounters
from commands.utils.utils import tablify, datehandler
from highscores import getClanList


class IngameEvents(commands.Cog):
    def __init__(self, client: commands.bot):
        self.client: commands.bot = client

    @commands.command(name="lastonline")
    async def lastonline(self, ctx, playername=None):
        if playername is None:
            with sqlite3.connect("ingame_data.db") as conn:
                cur = conn.cursor()
                cur.execute("SELECT max(timestamp) FROM activity")
                online = datetime.datetime.fromtimestamp(cur.fetchall()[0][0], datetime.timezone.utc)
                await ctx.send(f"last online check was at {online}. Give a playername with the command to see what"
                               f"date the player was last online.")
            return
        playername = playername.lower()
        with sqlite3.connect("ingame_data.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT timestamp FROM activity WHERE playername=?", (playername,))
            try:
                timestamp = cur.fetchall()[0][0]
            except IndexError:
                await ctx.send(f"no information about last online of {playername}")
                return
            online = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
            if playername != "mishaal":
                await ctx.send(f"{playername} was last online at {str(online).split(' ')[0]}")
            else:
                await ctx.send(f"{playername} was last online at {str(online)}")

    @commands.command(name="getencounters")
    async def getencounters(self, ctx: Context, *name: str):
        """
        gets the encounters
        :param ctx: message context
        :param name: either playername, pokemonname or a date
        """
        name = " ".join(name)
        name = name.lower()
        await ctx.send("is that a pokemon, date, or player? Press the button to get a response!",
                             view=GetEncounters(ctx, name))

    @commands.command(name="getpokemon")
    async def getpokemon(self, ctx: Context, *_):
        """
        @deprecated
        :param ctx:
        :param _:
        :return:
        """
        await ctx.send("please use .getencounters instead!")

    @commands.command(name="getchests")
    async def getchests(self, ctx, *argument):
        name = " ".join(argument).lower().strip()
        name = name.lower()
        await ctx.send("is that a location, date, or player? Press the button to get a response! ",
                       view=GetChests(ctx, name))

    @commands.command(name="getrolls")
    async def getrolls(self, ctx: Context, parameter: str):
        """
        Gets the rolls of a player, the rolls of a pokemon, or the rolls on a specific date.
        Timeout is 10 minutes, then the message gets deleted.
        :param ctx: discord context
        :param parameter: The pokemon, date or player
        """

        buttons = [Button(style=ButtonStyle.blue, label="Pokemon"),
                   Button(style=ButtonStyle.blue, label="Date (yyyy-mm-dd)"),
                   Button(style=ButtonStyle.blue, label="Player")]
        rollids = [button.id for button in buttons]
        msg = await ctx.send("is that a pokemon, date, or player? Press the button to get a response! ",
                             components=[buttons])

        def check(res):
            return res.component.id in rollids
        try:
            res = await self.client.wait_for("button_click", check=check, timeout=600)
        except asyncio.TimeoutError:
            for button in buttons:
                button.set_disabled(True)
            await msg.edit("responding has expired. Please try again.", components=[buttons])
            return
        query = "SELECT player, pokemon, date FROM rolls WHERE "
        if res.component.label == "Pokemon":
            query += "pokemon = ?"
        elif res.component.label == "Date (yyyy-mm-dd)":
            query += "date = ?"
        elif res.component.label == "Player":
            query += "player = ?"
        else:
            raise ValueError("error with getrolls. This should not happen.")
        query += " ORDER BY date DESC"
        await msg.delete()
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute(query, (parameter,))
        resultmessages = tablify(["player", "pokemon", "date"], cur.fetchall())
        resultmessageshower = ResultmessageShower(self.client, resultmessages, ctx)
        await resultmessageshower.loop()


    @commands.command(name="getclanencounters")
    async def getclanencounters(self, ctx: Context, clanname: str):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()

        clanlist = getClanList(clanname.lower())
        totalencounters = []
        for player in clanlist:
            cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Name = ?", (player,))
            [totalencounters.append(row) for row in cur.fetchall()]
        totalencounters.sort(key=lambda x: x[2])
        resultmessages = tablify(["name", "pokemon", "date"], totalencounters, maxlength=1200)

        resultmessageshower = ResultmessageShower(self.client, resultmessages[::-1], ctx, startpage=resultmessages[-1])
        await resultmessageshower.loop()

    @commands.command(name="getchestsbydate", aliases=["topchestlocations", "topchestplayers"])
    async def getchestsbydate(self, ctx: Context, *_):
        await ctx.send("please use .getchests instead!")


def setup(client):
    client.add_cog(IngameEvents(client))
