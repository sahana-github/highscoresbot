import asyncio
import sqlite3
import datetime
from typing import List

from discord.ext import commands
from discord.ext.commands.context import Context
from discord_components import Button, ButtonStyle

from commands.utils import tablify, datehandler, PageTurner


class IngameEvents(commands.Cog):
    def __init__(self, client: commands.bot):
        self.client: commands.bot = client

    @commands.command(name="getencounters")
    async def getencounters(self, ctx: Context, name: str):
        """
        gets the encounters
        :param ctx: message context
        :param name: either playername, pokemonname or a date
        """
        buttons = [Button(style=ButtonStyle.blue, label="Pokemon"),
                   Button(style=ButtonStyle.blue, label="Date (yyyy-mm-dd)"),
                   Button(style=ButtonStyle.blue, label="Player")]
        rollids = [button.id for button in buttons]
        msg = await ctx.send("is that a pokemon, date, or player? Press the button to get a response! "
                             "This will be visible to you only.",
                             components=[buttons])
        name = name.lower()

        def check(res):
            return res.component.id in rollids

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=600)
            if res.component.label == "Pokemon":
                resultmessages = self.__getpokemon(name)
            elif res.component.label == "Date (yyyy-mm-dd)":
                try:
                    resultmessages = self.__getdate(name)
                except ValueError:
                    await res.send(f"{name} does not match date format 'yyyy-mm-dd'!")
                    await msg.delete()
                    await self.getencounters(ctx, name)
                    return
            elif res.component.label == "Player":
                resultmessages = self.__getplayerencounters(name)
            else:
                raise Exception("????????????????????????")
        except asyncio.TimeoutError:
            for button in buttons:
                button.set_disabled(True)
            await msg.edit("responding has expired. Please try again.", components=[buttons])
            return
        page_changer = PageTurner(resultmessages[::-1])
        buttons = [Button(style=ButtonStyle.blue, label="<<"),
                   Button(style=ButtonStyle.blue, label="<"),
                   Button(style=ButtonStyle.red, label=">"),
                   Button(style=ButtonStyle.red, label=">>")]
        buttonids = [button.id for button in buttons]
        await res.edit_origin(f"```page {page_changer.page} of {page_changer.MAXPAGE}```\n" +
                              page_changer.changePage(0), components=[buttons])
        while True:
            try:
                res = await self.client.wait_for("button_click",
                                                 check=lambda response:
                                                 response.component.id in buttonids and
                                                 response.author.id == ctx.author.id,
                                                 timeout=600)
                if res.component.label == "<":
                    page = page_changer.changePage(-1)
                elif res.component.label == ">":
                    page = page_changer.changePage(1)
                elif res.component.label == "<<":
                    page = page_changer.changePage(page_changer.MINPAGE, True)
                elif res.component.label == ">>":
                    page = page_changer.changePage(page_changer.MAXPAGE, True)
                else:
                    page = page_changer.changePage(0)
                await res.edit_origin(f"```page {page_changer.page} of {page_changer.MAXPAGE}```\n"
                                      + page)
            except asyncio.TimeoutError:
                for button in buttons:
                    button.set_disabled(True)
                await msg.edit(f"```page {page_changer.page} of {page_changer.MAXPAGE}```\n" +
                               page_changer.changePage(0), components=[buttons])
                break

    def __getplayerencounters(self, playername: str) -> List[str]:
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Name = ?", (playername,))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        return resultmessages

    def __getpokemon(self, pokemonname: str) -> List[str]:
        """
        returns a list of encounters where that pokemon was encountered.
        :param pokemonname: the name of the pokemon
        """
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Encounters = ? ORDER BY Date DESC",
                    (pokemonname,))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        return resultmessages[::-1]

    def __getdate(self, date: str) -> List[str]:
        """
        get all encounters on a specific date.
        :param date: the date a encounter happened.
        """
        datetime.datetime.strptime(date, "%Y-%m-%d")

        date = datehandler(date)
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Date = ?", (date,))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        return resultmessages

    @commands.command(name="getpokemon")
    async def getpokemon(self, ctx: Context, *_):
        """
        @deprecated
        :param ctx:
        :param _:
        :return:
        """
        await ctx.send("please use .getencounters instead!")




    def __topchestlocations(self):
        """
        Shows you locations with the most spawned chests.
        :param ctx: discord context
        """
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT location, COUNT(*) FROM chests GROUP BY location ORDER BY COUNT(*) DESC")
        result = tablify(["Location", "Number Of Times Spawned"], cur.fetchall())
        conn.close()
        return result[::-1]

    def __topchestplayers(self):
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
        return result[::-1]

    @commands.command(name="getchests")
    async def getchests(self, ctx, *argument):
        rollids = []
        buttons = [[Button(style=ButtonStyle.blue, label="Location"),
                   Button(style=ButtonStyle.blue, label="Date (yyyy-mm-dd)"),
                   Button(style=ButtonStyle.blue, label="Player")],
                   [Button(style=ButtonStyle.blue, label="Top chest locations"),
                    Button(style=ButtonStyle.blue, label="Top chest players")]
                   ]
        for buttonrow in buttons:
            for button in buttonrow:
                rollids.append(button.id)
        msg = await ctx.send("is that a location, date, or player? Press the button to get a response! ",
                             components=buttons)
        name = " ".join(argument).lower().strip()

        def check(res):
            return res.component.id in rollids

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=600)
            if res.component.label == "Location":
                resultmessages = self.__getchestsbylocation(name)
            elif res.component.label == "Date (yyyy-mm-dd)":
                try:
                    resultmessages = self.__getchestsbydate(name)
                except ValueError:
                    await res.send(f"{name} does not match date format 'yyyy-mm-dd'!")
                    await msg.delete()
                    await self.getencounters(ctx, name)
                    return
            elif res.component.label == "Player":
                resultmessages = self.__getchestsbyplayer(name)
            elif res.component.label == "Top chest locations":
                resultmessages = self.__topchestlocations()
            elif res.component.label == "Top chest players":
                resultmessages = self.__topchestplayers()
            else:
                raise Exception("????????????????????????")
        except asyncio.TimeoutError:
            for buttonrow in buttons:
                for button in buttonrow:
                    button.set_disabled(True)
            await msg.edit("responding has expired. Please try again.", components=[buttons])
            return
        page_changer = PageTurner(resultmessages[::-1])
        buttons = [Button(style=ButtonStyle.blue, label="<<"),
                   Button(style=ButtonStyle.blue, label="<"),
                   Button(style=ButtonStyle.red, label=">"),
                   Button(style=ButtonStyle.red, label=">>")]
        buttonids = [button.id for button in buttons]
        await res.edit_origin(f"```page {page_changer.page} of {page_changer.MAXPAGE}```\n" +
                              page_changer.changePage(0), components=[buttons])
        while True:
            try:
                res = await self.client.wait_for("button_click",
                                                 check=lambda response:
                                                 response.component.id in buttonids and
                                                 response.author.id == ctx.author.id,
                                                 timeout=600)
                if res.component.label == "<":
                    page = page_changer.changePage(-1)
                elif res.component.label == ">":
                    page = page_changer.changePage(1)
                elif res.component.label == "<<":
                    page = page_changer.changePage(page_changer.MINPAGE, True)
                elif res.component.label == ">>":
                    page = page_changer.changePage(page_changer.MAXPAGE, True)
                else:
                    page = page_changer.changePage(0)
                await res.edit_origin(f"```page {page_changer.page} of {page_changer.MAXPAGE}```\n"
                                      + page)
            except asyncio.TimeoutError:
                for button in buttons:
                    button.set_disabled(True)
                await msg.edit(f"```page {page_changer.page} of {page_changer.MAXPAGE}```\n" +
                               page_changer.changePage(0), components=[buttons])
                break


    def __getchestsbydate(self, date=None):
        if date is None:
            date = str(datetime.datetime.now()).split(" ")[0]
        date = datehandler(date)
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE date=?", (date,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall())
        conn.close()
        return resultmessages

    def __getchestsbyplayer(self, player):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE player=?", (player,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall())
        conn.close()
        return resultmessages

    def __getchestsbylocation(self, location):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE location=?", (location,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall())
        conn.close()
        return resultmessages

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
                for button in buttons:
                    button.set_disabled(True)
                await msg.edit("responding has expired. Please try again.", components=[buttons])
                break

    @commands.command(name="getchestsbydate", aliases=["topchestlocations", "topchestplayers"])
    async def getchestsbydate(self, ctx, *_):
        await ctx.send("please use .getchests instead!")


def setup(client):
    client.add_cog(IngameEvents(client))
