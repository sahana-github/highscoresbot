import discord
from discord import Interaction


class BrowseSelection(discord.ui.View):
    """
    handles the buttons to browse through something.
    """
    def __init__(self, interaction: Interaction, pagesamount: int, ownerOnly=True):
        """
        constructor
        :param interaction: interaction context.
        :param pagesamount: amount of pages.
        :param ownerOnly: if only the owner/initiator may press the buttons.
        """
        super().__init__()
        self.ownerOnly = ownerOnly
        self.interaction = interaction
        self.currentpage = 1
        self.maxpage = pagesamount

    @discord.ui.button(label='<<', style=discord.ButtonStyle.green)
    async def minpage(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        set current page to 1.
        :param button:
        :param interaction:
        :return:
        """
        if not await self.isOwner(interaction): return
        self.currentpage = 1
        await self._sendPage(interaction)

    @discord.ui.button(label='<', style=discord.ButtonStyle.green)
    async def previouspage(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        go 1 page back (if possible)
        :param button:
        :param interaction:
        :return:
        """
        if not await self.isOwner(interaction): return
        if self.currentpage - 1 >= 1:
            self.currentpage -= 1
        await self._sendPage(interaction)

    @discord.ui.button(label='>', style=discord.ButtonStyle.danger)
    async def nextpage(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        go to the next page (if possible)
        :param button:
        :param interaction:
        :return:
        """
        if not await self.isOwner(interaction): return
        if self.currentpage + 1 <= self.maxpage:
            self.currentpage += 1
        await self._sendPage(interaction)

    @discord.ui.button(label='>>', style=discord.ButtonStyle.danger)
    async def maxpage(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        go to the max page.
        :param button:
        :param interaction:
        :return:
        """
        if not await self.isOwner(interaction): return
        self.currentpage = self.maxpage
        await self._sendPage(interaction)

    async def _sendPage(self, interaction: discord.Interaction):
        """
        to be implemented by subclasses.
        What gets sent on any button press.
        :param interaction:
        :return:
        """
        raise NotImplementedError

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        """
        :param interaction:
        :return: if the interaction is made by the owner.
        """
        if not self.ownerOnly:
            return True
        if interaction.guild != self.interaction.guild or interaction.user != self.interaction.user:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True
