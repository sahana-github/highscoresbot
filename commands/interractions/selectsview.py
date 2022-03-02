from typing import Callable, List

import discord

from commands.interractions.browseselection import BrowseSelection
from commands.interractions.selectsutility import SelectsUtility


class SelectsView(BrowseSelection):
    def __init__(self, ctx, options, selectoption: Callable[[List[str]], SelectsUtility], ownerOnly=True):
        self.selectoptionmaker = selectoption
        self.pages = []
        page = []
        for i in options:
            page.append(i)
            if len(page) == 25:
                self.pages.append(page)
                page = []
        if page:
            self.pages.append(page)
        super(SelectsView, self).__init__(ctx, pagesamount=len(self.pages), ownerOnly=ownerOnly)
        self.previous: SelectsUtility = self.selectoptionmaker(self.pages[0])
        self.add_item(self.previous)
        #await ctx.send(content=f"page {self.currentpage} of {self.maxpage}", view=self)

    async def _sendPage(self, interaction: discord.Interaction):
        if self.previous is not None:  # remove previous, else we get 2 select options.
            self.remove_item(self.previous)
        self.previous = self.selectoptionmaker(self.pages[self.currentpage-1])
        self.add_item(self.previous)
        await interaction.response.edit_message(content=f"page {self.currentpage} of {self.maxpage}", view=self)
