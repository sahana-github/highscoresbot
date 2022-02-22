import asyncio
import sqlite3
import datetime
from typing import List

from discord.ext import commands
from discord.ext.commands.context import Context
from discord_components import Button, ButtonStyle

from commands.utils.utils import tablify, datehandler, ResultmessageShower
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
    async def getencounters(self, ctx: Context, name: str):
        """
        gets the encounters
        :param ctx: message context
        :param name: either playername, pokemonname or a date
        """
        rollids = []
        buttons = [[Button(style=ButtonStyle.blue, label="Pokemon"),
                   Button(style=ButtonStyle.blue, label="Date (yyyy-mm-dd)"),
                   Button(style=ButtonStyle.blue, label="Player")],
                   [Button(style=ButtonStyle.blue, label="Top encounter dates"),
                    Button(style=ButtonStyle.blue, label="Top encounter players"),
                    Button(style=ButtonStyle.blue, label="Top encounter pokemon")]
                   ]
        for buttonrow in buttons:
            for button in buttonrow:
                rollids.append(button.id)
        msg = await ctx.send("is that a pokemon, date, or player? Press the button to get a response! ",
                             components=buttons)
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
            elif res.component.label == "Top encounter dates":
                resultmessages = self.__getencountersamount()
            elif res.component.label == "Top encounter players":
                resultmessages = self.__getencountersamountplayers()
            elif res.component.label == "Top encounter pokemon":
                resultmessages = self.__getencounteramountpokemon()
            else:
                raise Exception("????????????????????????")
        except asyncio.TimeoutError:
            for buttonrow in buttons:
                for button in buttonrow:
                    button.set_disabled(True)
            await msg.edit("responding has expired. Please try again.", components=buttons)
            return
        await msg.delete()
        resultmessageshower = ResultmessageShower(self.client, resultmessages, ctx)
        await resultmessageshower.loop()

    def __getplayerencounters(self, playername: str) -> List[str]:
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Name = ?", (playername,))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        return resultmessages[::-1]

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
        return resultmessages

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

    def __getencountersamount(self):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT date, count(date) FROM encounters GROUP BY date ORDER BY count(date) DESC")
        resultset = cur.fetchall()
        resultmessages = tablify(("Date", "Amount of encounters"), resultset, maxlength=1000)
        conn.close()
        return resultmessages

    def __getencountersamountplayers(self):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT name, count(name) FROM encounters GROUP BY name ORDER BY count(name) DESC")
        resultset = cur.fetchall()
        resultmessages = tablify(("Player", "Amount of encounters"), resultset, maxlength=1000)
        conn.close()
        return resultmessages

    def __getencounteramountpokemon(self):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT encounters.encounters, count(encounters.encounters) FROM encounters GROUP BY encounters ORDER BY count(encounters.encounters) DESC")
        resultset = cur.fetchall()
        resultmessages = tablify(("Pokemon", "Amount of encounters"), resultset, maxlength=1000)
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
        result = tablify(["Location", "Number Of Times Spawned"], cur.fetchall(), maxlength=1000)
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
        result = tablify(["Name", "Chests"], cur.fetchall(), maxlength=1000)
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
                    if name == "":
                        name = str(datetime.datetime.now()).split()[0]
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
            await msg.edit("responding has expired. Please try again.", components=buttons)
            return
        await msg.delete()
        resultmessageshower = ResultmessageShower(self.client, resultmessages[::-1], ctx, startpage=resultmessages[-1])
        await resultmessageshower.loop()


    def __getchestsbydate(self, date=None):
        if date is None:
            date = str(datetime.datetime.now()).split(" ")[0]
        date = datehandler(date)
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE date=?", (date,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        return resultmessages

    def __getchestsbyplayer(self, player):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE player=?", (player,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        return resultmessages

    def __getchestsbylocation(self, location):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE location=?", (location,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall(), maxlength=1000)
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
