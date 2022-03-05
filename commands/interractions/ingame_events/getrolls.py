import sqlite3
import datetime

import discord
from discord.ext.commands import Context

from commands.interractions.resultmessageshower import ResultmessageShower
from commands.utils.utils import tablify, datehandler


class GetRolls(discord.ui.View):
    def __init__(self, ctx: Context, parameter):
        super().__init__()
        self.parameter = parameter
        self.ctx = ctx

    @discord.ui.button(label='Pokemon', style=discord.ButtonStyle.green)
    async def pokemon(self, button: discord.ui.Button, interaction: discord.Interaction):
        query = "SELECT player, pokemon, date FROM rolls WHERE pokemon = ? ORDER BY date DESC"
        await self.showMessages(interaction, query)

    @discord.ui.button(label="Date (yyyy-mm-dd)", style=discord.ButtonStyle.green)
    async def date(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.parameter == "":
            date = str(datetime.datetime.now()).split(" ")[0]
        else:
            date = self.parameter
        date = datehandler(date)
        self.parameter = date
        query = "SELECT player, pokemon, date FROM rolls WHERE date = ? ORDER BY date DESC"
        await self.showMessages(interaction, query)

    @discord.ui.button(label="Player", style=discord.ButtonStyle.green)
    async def player(self, button: discord.ui.Button, interaction: discord.Interaction):
        query = "SELECT player, pokemon, date FROM rolls WHERE player = ? ORDER BY date DESC"
        await self.showMessages(interaction, query)

    async def showMessages(self, interaction: discord.Interaction, query):
        if not await self.isOwner(interaction): return
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute(query, (self.parameter,))
        resultmessages = tablify(["playername", "pokemon", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        msgshower = ResultmessageShower(messages=resultmessages, ctx=self.ctx)
        await interaction.response.edit_message(view=msgshower,
                                                content=f"page {msgshower.currentpage} of {msgshower.maxpage}\n" +
                                                        msgshower.messages[0])
        self.stop()

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        """
        check if the user initiating the interaction is the same user initiating the command.
        :param interaction:
        :return: boolean, true if is owner.
        """
        if interaction.guild != self.ctx.guild or interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True
