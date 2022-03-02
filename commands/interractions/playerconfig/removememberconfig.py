import sqlite3
from typing import List

import discord


class RemoveMemberConfig(discord.ui.Select):
    def __init__(self, members: List[str], databasepath, ctx):
        self.ctx = ctx
        # Set the options that will be presented inside the dropdown
        self.databasepath = databasepath
        if len(members) > 25:
            raise ValueError("more than 25 members.")
        options = []  # discord.SelectOption(label='Green', description='Your favourite colour is green', emoji='🟩'),
        for member in members:
            options.append(discord.SelectOption(label=member))
        super().__init__(placeholder='Choose the members you want to remove from memberconfig', min_values=1,
                         max_values=len(members),
                         options=options)

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
        #await interaction.delete_original_message()

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        if interaction.guild.id != self.ctx.guild.id or interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True


class BrowseSelection(discord.ui.View):
    def __init__(self, members, databasepath, ctx):
        self.ctx = ctx
        self.databasepath = databasepath
        super().__init__()
        self.currentpage = 1
        self.pages = []
        page = []
        for member in members:
            page.append(member)
            if len(page) == 25:
                self.pages.append(page)
                page = []
        if page:
            self.pages.append(page)
        self.maxpage = len(self.pages)

        # keep track of selects, else we get multiple.
        self.previous = RemoveMemberConfig(self.pages[self.currentpage - 1], self.databasepath, self.ctx)
        self.add_item(self.previous)

    @discord.ui.button(label='<<', style=discord.ButtonStyle.green)
    async def minpage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        self.currentpage = 1
        await self.__sendPage(interaction)

    @discord.ui.button(label='<', style=discord.ButtonStyle.green)
    async def previouspage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        if self.currentpage - 1 >= 1:
            self.currentpage -= 1
        await self.__sendPage(interaction)

    @discord.ui.button(label='>', style=discord.ButtonStyle.green)
    async def nextpage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        if self.currentpage + 1 <= self.maxpage:
            self.currentpage += 1
        await self.__sendPage(interaction)

    @discord.ui.button(label='>>', style=discord.ButtonStyle.green)
    async def maxpage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        self.currentpage = self.maxpage
        await self.__sendPage(interaction)

    async def __sendPage(self, interaction: discord.Interaction):
        if self.previous is not None:  # remove previous, else we get 2 select options.
            self.remove_item(self.previous)
        self.previous = RemoveMemberConfig(self.pages[self.currentpage-1], self.databasepath, self.ctx)
        self.add_item(self.previous)
        await interaction.response.edit_message(content=f"page {self.currentpage} of {self.maxpage}", view=self)

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        if interaction.guild.id != self.ctx.guild.id or interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True
