import sqlite3
import datetime

import discord
from discord.ext.commands import Context

from commands.interractions.resultmessageshower import ResultmessageShower
from commands.utils.utils import tablify, datehandler


class GetChests(discord.ui.View):
    """
    the view of the getchests command.
    """
    def __init__(self, ctx: Context, parameter: str):
        super().__init__()
        self.parameter = parameter
        self.ctx = ctx

    @discord.ui.button(label='Location', style=discord.ButtonStyle.green)
    async def location(self, button: discord.ui.Button, interaction: discord.Interaction):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE location=?", (self.parameter,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages, interaction)

    @discord.ui.button(label="Date (yyyy-mm-dd)", style=discord.ButtonStyle.green)
    async def date(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.parameter == "":
            date = str(datetime.datetime.now()).split(" ")[0]
        else:
            date = self.parameter
        date = datehandler(date)
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE date=?", (date,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages, interaction)

    @discord.ui.button(label="player", style=discord.ButtonStyle.green)
    async def player(self, button: discord.ui.Button, interaction: discord.Interaction):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, location, date FROM chests WHERE player=?", (self.parameter,))
        resultmessages = tablify(["playername", "location", "date"], cur.fetchall(), maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages[::-1], interaction)

    @discord.ui.button(label="Top chest locations", style=discord.ButtonStyle.green, row=2)
    async def topchestlocations(self, button: discord.ui.Button, interaction: discord.Interaction):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT location, COUNT(*) FROM chests GROUP BY location ORDER BY COUNT(*) DESC")
        resultmessages = tablify(["Location", "Number Of Times Spawned"], cur.fetchall(), maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages, interaction)

    @discord.ui.button(label="Top chest players", style=discord.ButtonStyle.green, row=2)
    async def topchestplayers(self, button: discord.ui.Button, interaction: discord.Interaction):
        conn = sqlite3.connect(r"ingame_data.db")
        cur = conn.cursor()
        cur.execute("SELECT player, COUNT(*) FROM chests GROUP BY player ORDER BY COUNT(*) DESC")
        resultmessages = tablify(["Name", "Chests"], cur.fetchall(), maxlength=1000)
        conn.close()
        await self.showMessages(resultmessages, interaction)

    async def showMessages(self, resultmessages, interaction: discord.Interaction):
        """
        show the provided resultmessages inside a ResultmessageShower. also stop receiving input for buttons.
        :param resultmessages:
        :param interaction:
        :return:
        """
        if not await self.isOwner(interaction): return
        msgshower = ResultmessageShower(messages=resultmessages, ctx=self.ctx)
        await interaction.response.edit_message(view=msgshower,
                                                content=f"page {msgshower.currentpage} of {msgshower.maxpage}\n" +
                                                        msgshower.messages[0])
        self.stop()

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        if interaction.guild != self.ctx.guild or interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True
