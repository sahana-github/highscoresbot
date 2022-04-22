from discord import app_commands, Interaction, InteractionResponse
from discord.ext import commands

from commands.command_functionality import highscores
from commands.sendable import Sendable


class Highscores(commands.Cog):
    def __init__(self, client):
        self.client: commands.bot.Bot = client

    highscoresgroup = app_commands.Group(name="highscores",
                                         description="all commands that have to do directly with all the highscores of pokemon planet.")

    @highscoresgroup.command(name="getplayer")
    async def getplayer(self, interaction: Interaction, username: str):
        await highscores.getplayer(Sendable(interaction), username)

    @highscoresgroup.command(name="getclan")
    async def getclan(self, interaction: Interaction, clanname: str):

       # InteractionResponse.is_done()
        #await interaction.response.pong()
        #await interaction.response.defer(thinking=False)
        await highscores.getclan(Sendable(interaction), clanname)

async def setup(client: commands.Bot):
    await client.add_cog(Highscores(client))