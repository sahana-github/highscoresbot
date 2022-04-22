from typing import Callable, Coroutine, Awaitable

import discord
from discord import Interaction
from discord.ext.commands import Context


class PlayerConfig(discord.ui.View):
    """
    view for the playerconfig command.
    """
    def __init__(self, add: Callable[[Interaction, str], Awaitable[None]], remove: Callable[[Interaction], Awaitable[None]],
                 show: Callable[[Interaction], Awaitable[None]], interaction: Interaction, player=None):
        """

        :param add: callable for adding a player to playerconfig
        :param remove: callable for removing a player from playerconfig
        :param show: callable for showing playerconfig
        :param ctx:
        """
        super().__init__()
        self.add = add
        self.remove = remove
        self.show = show
        self.interaction = interaction
        self.player = player

    @discord.ui.button(label='add player', style=discord.ButtonStyle.green)
    async def addplayer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.isOwner(interaction):return
        if self.player is None:
            await interaction.response.send_message("provide a player in the command to add a player!")
            return
        await self.add(interaction, self.player)
        self.stop()

    @discord.ui.button(label='remove player', style=discord.ButtonStyle.danger)
    async def removeplayer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.isOwner(interaction): return
        await self.remove(interaction)
        self.stop()

    @discord.ui.button(label='show playerconfigurations', style=discord.ButtonStyle.blurple)
    async def showplayers(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.isOwner(interaction): return
        await self.show(interaction)
        self.stop()

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        if interaction.guild.id != self.interaction.guild.id or interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True
