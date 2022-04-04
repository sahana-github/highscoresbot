from typing import List
import discord
from discord import Interaction
from discord.ext.commands import Context

from commands.interractions.resultmessageshower import ResultmessageShower
from commands.interractions.selectsutility import SelectsUtility
from commands.utils.utils import tablify
from highscores import allhighscores


class HighscoreCommand(SelectsUtility):
    def __init__(self, interaction: Interaction, highscores: List[str], clanname: str=None):
        """
        creates a selectsutility for the highscore command.
        :param ctx:
        :param highscores: the options. max 25.
        """
        super().__init__(interaction=interaction, options=highscores, max_selectable=1, min_selectable=1,
                         placeholder="select the highscore you want to see")
        self.highscores = highscores
        self.clanname = clanname

    async def callback(self, interaction: discord.Interaction):
        """
        what happens on select.
        :param interaction:
        :return:
        """
        highscorename = self.values[0]
        for highscore in allhighscores:
            highscore = highscore()
            if highscore.NAME == highscorename:
                break
        else:
            raise ValueError(f"Highscore {highscorename} does not exist!!")
        messages = tablify(highscore.LAYOUT, highscore.getDbValues(clan=self.clanname), maxlength=1300)
        await interaction.response.send_message(content=messages[0],
                                                view=ResultmessageShower(messages, interaction=interaction))
