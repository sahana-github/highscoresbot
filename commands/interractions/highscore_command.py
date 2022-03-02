from typing import List
import discord
from discord.ext.commands import Context

from commands.interractions.resultmessageshower import ResultmessageShower
from commands.interractions.selectsutility import SelectsUtility
from commands.utils.utils import tablify
from highscores import allhighscores


class HighscoreCommand(SelectsUtility):
    def __init__(self, ctx: Context, highscores: List[str]):
        super().__init__(ctx=ctx, options=highscores, max_selectable=1, min_selectable=1,
                         placeholder="select the highscore you want to see")
        self.highscores = highscores

    async def callback(self, interaction: discord.Interaction):
        highscorename = self.values[0]
        for highscore in allhighscores:
            highscore = highscore()
            if highscore.NAME == highscorename:
                break
        else:
            raise ValueError(f"Highscore {highscorename} does not exist!!")
        messages = tablify(highscore.LAYOUT, highscore.getDbValues(), maxlength=1300)
        await self.ctx.send(content=messages[0], view=ResultmessageShower(messages, ctx=self.ctx))
