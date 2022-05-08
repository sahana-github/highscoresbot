import sqlite3
from typing import Union

from discord import app_commands, Interaction, InteractionResponse
from discord.ext import commands

from commands.command_functionality import highscores
from commands.sendable import Sendable


class Highscores(commands.Cog):
    def __init__(self, client):
        self.client: commands.bot.Bot = client
        self.databasepath = "highscores.db"

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

    @highscoresgroup.command(name="top")
    async def top(self, interaction: Interaction, clanname: str=None):
        sendable = Sendable(interaction)
        if clanname is None:
            clanname = await self.getdefaultclanname(sendable, comment=False)
        await highscores.top(sendable, clanname)

    @highscoresgroup.command(name="highscore")
    async def highscore(self, interaction: Interaction, clanname: str=None):
        sendable = Sendable(interaction)
        await highscores.highscore(sendable, clanname)

    @highscoresgroup.command(name="mapcontrol")
    async def mapcontrol(self, interaction: Interaction, clanname: str=None):
        sendable = Sendable(interaction)
        if clanname is None and ((clanname := await self.getdefaultclanname(sendable)) is None):
            clanname = ""
        await highscores.mapcontrol(sendable, clanname)

    async def getdefaultclanname(self, sendable: Sendable, comment=True) -> Union[str, None]:
        if sendable.guild is None:
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT name FROM clannames WHERE id=?", (sendable.guild.id,))
        try:
            clanname = cur.fetchall()[0][0]
        except IndexError:
            clanname = None
        if clanname is None and comment:
            await sendable.send("Please register a default clanname or provide a clan in the command.")
        elif clanname is not None:
            clanname = clanname.lower()
        return clanname


async def setup(client: commands.Bot):
    await client.add_cog(Highscores(client))
