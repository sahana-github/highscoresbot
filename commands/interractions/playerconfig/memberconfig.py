from typing import Callable

import discord


class PlayerConfig(discord.ui.View):
    def __init__(self, add: Callable, remove: Callable, show: Callable, ctx):
        super().__init__()
        self.add = add
        self.remove = remove
        self.show = show
        self.ctx = ctx

    @discord.ui.button(label='add player', style=discord.ButtonStyle.blurple)
    async def addplayer(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="interaction starting.", view=None)
        await interaction.delete_original_message()
        await self.add(self.ctx)
        self.stop()

    @discord.ui.button(label='remove player', style=discord.ButtonStyle.green)
    async def removeplayer(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="interaction starting.", view=None)
        await interaction.delete_original_message()
        await self.remove(self.ctx)
        self.stop()

    @discord.ui.button(label='show playerconfigurations', style=discord.ButtonStyle.green)
    async def showplayers(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="interaction starting.", view=None)
        await interaction.delete_original_message()
        await self.show(self.ctx)
        self.stop()
