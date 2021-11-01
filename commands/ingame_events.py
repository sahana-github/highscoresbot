import asyncio
import sqlite3
import datetime
from discord.ext import commands
from discord.ext.commands.context import Context
from discord_components import Button, ButtonStyle

from commands.utils import tablify, datehandler


class IngameEvents(commands.Cog):
    def __init__(self, client: commands.bot):
        self.client: commands.bot = client

    @commands.command(name="getencounters")
    async def getencounters(self, ctx: Context, playername: str):
        """
        gets the encounters of a player.
        :param ctx: message context
        :param playername: name of player to get the encounters from.
        """
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Name = ?", (playername.lower(),))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall())
        conn.close()
        await ctx.send(resultmessages[-1])
        for i in resultmessages[:-1]:
            await ctx.author.send(i)

    @commands.command(name="topchestlocations")
    async def topchestlocations(self, ctx: Context):
        """
        Shows you locations with the most spawned chests.
        :param ctx: discord context
        """
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT location, COUNT(*) FROM chests GROUP BY location ORDER BY COUNT(*) DESC")
        result = tablify(["Location", "Number Of Times Spawned"], cur.fetchall())
        conn.close()
        await ctx.send(result[0])

    @commands.command(name="topchestplayers")
    async def topchestplayers(self, ctx: Context):
        """
        shows you the players who opened the most chests.
        :param ctx:
        :return:
        """
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, COUNT(*) FROM chests GROUP BY player ORDER BY COUNT(*) DESC")
        result = tablify(["Name", "Chests"], cur.fetchall())
        conn.close()
        await ctx.send(result[0])

    @commands.command(name="getdate")
    async def getdate(self, ctx: Context, date: str):
        """
        get all encounters on a specific date.
        :param ctx: message context.
        :param date: the date a encounter happened.
        """
        date = datehandler(date)
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Date = ?", (date,))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall())
        conn.close()
        await ctx.send(resultmessages[0])

    @commands.command(name="getchestsbydate")
    async def getchestsbydate(self, ctx, date=None):
        if date is None:
            date = str(datetime.datetime.now()).split(" ")[0]
        date = datehandler(date)
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE date=?", (date,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall())
        for i in resultmessages:
            await ctx.send(i)

    @commands.command(name="getpokemon")
    async def getpokemon(self, ctx: Context, pokemonname: str):
        """
        shows a list of encounters where that pokemon was encountered.
        :param ctx: message context
        :param pokemonname: the name of the pokemon
        """
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Encounters = ? ORDER BY Date DESC",
                    (pokemonname,))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall())
        conn.close()
        await ctx.send(resultmessages[0])

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
        msg = await ctx.send("is that a pokemon, date, or player? Press the button to get a response! "
                             "This will be visible to you only.",
                       components=[buttons])

        def check(res):
            return res.component.id in rollids

        while True:
            try:
                res = await self.client.wait_for("button_click", check=check, timeout=600)
                query = "SELECT player, pokemon, date FROM rolls WHERE "
                if res.component.label == "Pokemon":
                    query += "pokemon = ?"
                elif res.component.label == "Date (yyyy-mm-dd)":
                    query += "date = ?"
                elif res.component.label == "Player":
                    query += "player = ?"
                else:
                    continue  # just in case
                conn = sqlite3.connect(r"ingame_data.db")
                cur = conn.cursor()
                cur.execute(query, (parameter,))
                for message in tablify(["player", "pokemon", "date"], cur.fetchall()):
                    await res.send(message)
                conn.close()
            except asyncio.TimeoutError:
                await msg.delete()
                break


def setup(client):
    client.add_cog(IngameEvents(client))
