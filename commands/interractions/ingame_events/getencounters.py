import sqlite3
import datetime

import discord
from discord import Interaction
from discord.ext.commands import Context

from commands.interractions.resultmessageshower import ResultmessageShower
from commands.utils.utils import tablify, datehandler


class GetEncounters(discord.ui.View):
    """
    the view of the getencounters command.
    """
    def __init__(self, interaction: Interaction, parameter):
        super().__init__()
        self.parameter = parameter
        self.interaction = interaction

    @discord.ui.button(label='pokemon', style=discord.ButtonStyle.green)
    async def pokemon(self, button: discord.ui.Button, interaction: discord.Interaction):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Encounters = ? ORDER BY Date DESC",
                    (self.parameter,))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages, interaction)

    @discord.ui.button(label="Date (yyyy-mm-dd)", style=discord.ButtonStyle.green)
    async def date(self, button: discord.ui.Button, interaction: discord.Interaction):
        datetime.datetime.strptime(self.parameter, "%Y-%m-%d")

        date = datehandler(self.parameter)
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Date = ?", (date,))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages, interaction)

    @discord.ui.button(label="player", style=discord.ButtonStyle.green)
    async def player(self, button: discord.ui.Button, interaction: discord.Interaction):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Name = ?", (self.parameter,))
        resultmessages = tablify(["Name", "encounter", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages[::-1], interaction)

    @discord.ui.button(label="Top encounter dates", style=discord.ButtonStyle.green, row=2)
    async def topencounterdates(self, button: discord.ui.Button, interaction: discord.Interaction):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT date, count(date) FROM encounters GROUP BY date ORDER BY count(date) DESC")
        resultset = cur.fetchall()
        resultmessages = tablify(("Date", "Amount of encounters"), resultset, maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages, interaction)

    @discord.ui.button(label="Top encounter players", style=discord.ButtonStyle.green, row=2)
    async def topencounterplayers(self, button: discord.ui.Button, interaction: discord.Interaction):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT name, count(name) FROM encounters GROUP BY name ORDER BY count(name) DESC")
        resultset = cur.fetchall()
        resultmessages = tablify(("Player", "Amount of encounters"), resultset, maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages, interaction)

    @discord.ui.button(label="Top encounter pokemon", style=discord.ButtonStyle.green, row=2)
    async def topencounterpokemon(self, button: discord.ui.Button, interaction: discord.Interaction):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT encounters.encounters, count(encounters.encounters) FROM encounters GROUP BY encounters ORDER BY count(encounters.encounters) DESC")
        resultset = cur.fetchall()
        resultmessages = tablify(("Pokemon", "Amount of encounters"), resultset, maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages, interaction)

    async def showMessages(self, resultmessages, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        msgshower = ResultmessageShower(messages=resultmessages, interaction=self.interaction)
        await interaction.response.edit_message(view=msgshower,
                                                content=f"page {msgshower.currentpage} of {msgshower.maxpage}\n" +
                                                        msgshower.messages[0])
        self.stop()

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        """
        check if the user initiating the interaction is the same user initiating the command.
        :param interaction:
        :return:boolean
        """
        if interaction.guild != self.interaction.guild or interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True
