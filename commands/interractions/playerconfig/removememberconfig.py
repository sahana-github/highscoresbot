import sqlite3
from typing import List

import discord

from commands.interractions.browseselection import BrowseSelection
from commands.interractions.selectsutility import SelectsUtility


class RemoveMemberConfig(SelectsUtility):
    """
    for removing a player of the playerconfig command.
    """
    def __init__(self, members: List[str], databasepath, ctx):
        # Set the options that will be presented inside the dropdown
        self.databasepath = databasepath

        super().__init__(ctx, members, len(members), placeholder="select the members you want to remove below:")

    async def callback(self, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        for member in self.values:
            cur.execute("DELETE FROM memberconfig WHERE guildid=? and playername=?", (interaction.guild.id, member))
        conn.commit()
        conn.close()
        if len(self.values) > 1:
            await interaction.response.edit_message(content=f'{len(self.values)} members removed from memberconfig!',
                                                    view=None)
        else:
            await interaction.response.edit_message(content=f"{self.values[0]} removed from memberconfig!", view=None)
