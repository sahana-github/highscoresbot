import asyncio
import sqlite3
import datetime
from typing import List
from discord import app_commands, Interaction, InteractionResponse
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

    ingameeventsgroup = app_commands.Group(name="ingame-events",
                                           description="deals with stuff that has been acquired from inside the game itself")
    @ingameeventsgroup.command(name="lastonline")
    async def lastonline(self, interaction: Interaction, playername=None):
        if playername is None:
            with sqlite3.connect("ingame_data.db") as conn:
                cur = conn.cursor()
                cur.execute("SELECT max(timestamp) FROM activity")
                online = datetime.datetime.fromtimestamp(cur.fetchall()[0][0], datetime.timezone.utc)
                await interaction.response.send_message(f"last online check was at {online}. Give a playername with the command to see what"
                               f"date the player was last online.")
            return
        playername = playername.lower()
        with sqlite3.connect("ingame_data.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT timestamp FROM activity WHERE playername=?", (playername,))
            try:
                timestamp = cur.fetchall()[0][0]
            except IndexError:
                await interaction.response.send_message(f"no information about last online of {playername}")
                return
            online = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
            if playername != "mishaal":
                await interaction.response.send_message(f"{playername} was last online at {str(online).split(' ')[0]}")
            else:
                await interaction.response.send_message(f"{playername} was last online at {str(online)}")


    @ingameeventsgroup.command(name="getencounters")
    async def getencounters(self, interaction: Interaction, name: str):
        """
        gets the encounters
        :param ctx: message context
        :param name: either playername, pokemonname or a date
        """
        interaction.u
        # name = " ".join(name)  @todo check if this is needed
        name = name.lower()
        await interaction.response.send_message(content="is that a pokemon, date, or player? Press the button to get a response!",
                             view=GetEncounters(interaction, name))

    @ingameeventsgroup.command(name="getpokemon")
    async def getpokemon(self, interaction: Interaction, *_):
        """
        @deprecated
        :param ctx:
        :param _:
        :return:
        """
        await interaction.response.send_message("please use .getencounters instead!")

    @ingameeventsgroup.command(name="getchests")
    async def getchests(self, interaction: Interaction, argument):
        #name = " ".join(argument).lower().strip()  @todo check if needed
        name = argument.lower()
        await interaction.response.send_message("is that a location, date, or player? Press the button to get a response! ",
                       view=GetChests(interaction, name))

    @ingameeventsgroup.command(name="getrolls")
    async def getrolls(self, interaction: Interaction, parameter: str):
        """
        Gets the rolls of a player, the rolls of a pokemon, or the rolls on a specific date.
        Timeout is 10 minutes, then the message gets deleted.
        :param ctx: discord context
        :param parameter: The pokemon, date or player
        """
        #parameter = " ".join(parameter)
        a: InteractionResponse = interaction.response
        await interaction.response.send_message(content="is that a pokemon, date, or player? Press the button to get a response! ",
                       view=GetRolls(interaction, parameter))

    @ingameeventsgroup.command(name="getclanencounters")
    async def getclanencounters(self, interaction: Interaction, clanname: str):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()

        clanlist = getClanList(clanname.lower())
        totalencounters = []
        for player in clanlist:
            cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Name = ?", (player,))
            [totalencounters.append(row) for row in cur.fetchall()]
        totalencounters.sort(key=lambda x: x[2])
        resultmessages = tablify(["name", "pokemon", "date"], totalencounters, maxlength=1200)
        resultmessageshower = ResultmessageShower(resultmessages[::-1], interaction)
        await interaction.response.send_message(content=f"page {resultmessageshower.currentpage} of {resultmessageshower.maxpage}\n" +
                               resultmessages[-1],
                       view=resultmessageshower)

    @commands.command(name="worldbosstime")
    async def worldbosstime(self, interaction: Interaction):
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
            await Interaction.response.send_message(embed=embed)
        except IndexError:
            await Interaction.response.send_message("something went wrong!")
        except Exception as e:
            await Interaction.response.send_message.send("uncaught exception.")
            raise e

async def setup(client):
    await client.add_cog(IngameEvents(client))
