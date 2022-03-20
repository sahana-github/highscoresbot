from typing import Callable, List

import discord
from discord import Interaction
from discord.ext.commands import Context

from commands.interractions.browseselection import BrowseSelection
from commands.interractions.selectsutility import SelectsUtility


class SelectsView(BrowseSelection):
    def __init__(self, interaction: Interaction, options: List[str], selectoption: Callable[[List[str]], SelectsUtility],
                 ownerOnly: bool = True):
        """
        combines the browseselection with selects, to bypass the limitation of 25 selects.
        :param ctx: discord context
        :param options: total list of selectoptions.
        :param selectoption: function that makes a SelectsUtility. Parameter to this function is the list of options.
        :param ownerOnly: Can only the initiator of the command use this? boolean.
        """
        self.selectoptionmaker = selectoption
        self.pages: List[List[str]] = []
        page = []
        for i in options:
            page.append(i)
            if len(page) == 25:
                self.pages.append(page)
                page = []
        if page:
            self.pages.append(page)
        super(SelectsView, self).__init__(interaction, pagesamount=len(self.pages), ownerOnly=ownerOnly)
        self.previous: SelectsUtility = self.selectoptionmaker(self.pages[0])
        self.add_item(self.previous)
        #await ctx.send(content=f"page {self.currentpage} of {self.maxpage}", view=self)

    async def _sendPage(self, interaction: discord.Interaction):
        """
        browse through all selectoptions and send the current options page. Every options page is max 25 selections.
        :param interaction: discord interaction.
        """
        if not await self.isOwner(interaction): return
        if self.previous is not None:  # remove previous, else we get 2 select options.
            self.remove_item(self.previous)
        self.previous = self.selectoptionmaker(self.pages[self.currentpage-1])
        self.add_item(self.previous)
        await interaction.response.edit_message(content=f"page {self.currentpage} of {self.maxpage}", view=self)
