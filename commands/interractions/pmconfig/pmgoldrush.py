from typing import List

from discord.ext.commands import Context

from commands.interractions.selectsutility import SelectsUtility
import discord
import sqlite3


class PmGoldrush(SelectsUtility):
    """
    a selectsutility for pmgoldrush
    """
    def __init__(self, ctx: Context, options: List[str], databasepath: str):
        """
        :param ctx:
        :param options: the list of options to choose from.
        :param databasepath: the path to the eventconfigurations database.
        """
        super().__init__(ctx, options, max_selectable=len(options),
                         placeholder="Select goldrushes you want pm for:")
        self.databasepath = databasepath

    async def callback(self, interaction: discord.Interaction):
        """
        on selection. adds locations to pmgoldrush config of a player.
        :param interaction:
        :return:
        """
        if not await self.isOwner(interaction): return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        for location in self.values:
            try:
                cur.execute("INSERT INTO pmgoldrush(playerid, location) VALUES(?,?)", (self.ctx.author.id, location))
                conn.commit()
                await self.ctx.send(f"You now get a pm when a gold rush shows up at {location}.")
            except sqlite3.IntegrityError:
                await self.ctx.send("can not insert the same location twice!")
        conn.close()