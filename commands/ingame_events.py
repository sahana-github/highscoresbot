import asyncio
import sqlite3
import datetime
from typing import List

import discord
from discord.ext import commands
from discord.ext.commands.context import Context

from commands.interractions.ingame_events.getchests import GetChests
from commands.interractions.ingame_events.getencounters import GetEncounters
from commands.interractions.ingame_events.getrolls import GetRolls
from commands.interractions.resultmessageshower import ResultmessageShower
from commands.utils.utils import tablify, datehandler, getworldbosstime
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
    async def getrolls(self, ctx: Context, *parameter: str):
        """
        Gets the rolls of a player, the rolls of a pokemon, or the rolls on a specific date.
        Timeout is 10 minutes, then the message gets deleted.
        :param ctx: discord context
        :param parameter: The pokemon, date or player
        """
        parameter = " ".join(parameter)
        await ctx.send("is that a pokemon, date, or player? Press the button to get a response! ",
                       view=GetRolls(ctx, parameter))

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
        resultmessageshower = ResultmessageShower(resultmessages[::-1], ctx)
        await ctx.send(content=f"page {resultmessageshower.currentpage} of {resultmessageshower.maxpage}\n" +
                               resultmessages[-1],
                       view=resultmessageshower)

    @commands.command(name="getchestsbydate", aliases=["topchestlocations", "topchestplayers"])
    async def getchestsbydate(self, ctx: Context, *_):
        await ctx.send("please use .getchests instead!")

    @commands.command(name="worldbosstime")
    async def worldbosstime(self, ctx: Context):
        """
        gives the time untill the start of the worldboss.
        :param ctx: discord context
        """
        try:
            worldboss_datetime = getworldbosstime()
            timedifference = worldboss_datetime - datetime.datetime.now()
            embed = discord.Embed(title="worldboss",
                                  description=f"The worldboss will start at <t:{str(int(worldboss_datetime.timestamp()))}>")
            embed.add_field(name="relative",
                            value=f"that is in {(timedifference.days * 86400 + timedifference.seconds) // 3600} hours "
                                  f"and {(timedifference.seconds // 60) % 60} minutes\n")
            await ctx.send(embed=embed)
        except IndexError:
            await ctx.send("something went wrong!")
        except Exception as e:
            await ctx.send("uncaught exception.")
            print(e)

def setup(client):
    client.add_cog(IngameEvents(client))
