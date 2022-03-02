import discord
from discord.ext.commands import Context


class BrowseSelection(discord.ui.View):
    """
    handles the buttons to browse through something.
    """
    def __init__(self, ctx: Context, pagesamount: int, ownerOnly=True):
        super().__init__()
        self.ownerOnly = ownerOnly
        self.ctx = ctx
        self.currentpage = 1
        self.maxpage = pagesamount

    @discord.ui.button(label='<<', style=discord.ButtonStyle.green)
    async def minpage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        self.currentpage = 1
        await self._sendPage(interaction)

    @discord.ui.button(label='<', style=discord.ButtonStyle.green)
    async def previouspage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        if self.currentpage - 1 >= 1:
            self.currentpage -= 1
        await self._sendPage(interaction)

    @discord.ui.button(label='>', style=discord.ButtonStyle.danger)
    async def nextpage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        if self.currentpage + 1 <= self.maxpage:
            self.currentpage += 1
        await self._sendPage(interaction)

    @discord.ui.button(label='>>', style=discord.ButtonStyle.danger)
    async def maxpage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        self.currentpage = self.maxpage
        await self._sendPage(interaction)

    async def _sendPage(self, interaction: discord.Interaction):
        raise NotImplementedError

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        if not self.ownerOnly:
            return True
        if interaction.guild.id != self.ctx.guild.id or interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True
