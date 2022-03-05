from abc import ABC
from typing import List, Union
import discord
from discord import Embed, InteractionResponse
from discord.ext.commands import Context

from commands.interractions.browseselection import BrowseSelection


class ResultmessageShower(BrowseSelection, ABC):
    """
    shows the resultmessages with buttons.
    """
    def __init__(self, messages: List[Union[str, Embed]], ctx: Context, ownerOnly=True):
        super(ResultmessageShower, self).__init__(ctx, pagesamount=len(messages), ownerOnly=ownerOnly)
        self.messages = messages

    async def _sendPage(self, interaction: discord.Interaction):
        """
        send the currentpage -1
        :param interaction:
        :return:
        """
        msg = self.messages[self.currentpage-1]
        if type(msg) == Embed:
            await interaction.response.edit_message(content=f"page {self.currentpage} of {self.maxpage}",
                                                    embed=msg,
                                                    view=self)
        else:
            await interaction.response.edit_message(content=f"page {self.currentpage} of {self.maxpage}\n" + str(msg),
                                                    view=self)
