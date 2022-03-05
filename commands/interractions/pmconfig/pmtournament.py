import sqlite3
from typing import Callable, Awaitable, List

import discord
from discord.ext.commands import Context

from commands.interractions.selectsutility import SelectsUtility
from commands.interractions.selectsview import SelectsView
from commands.utils.utils import gettournamentprizes


class GetTournament(SelectsUtility):
    """
    class for selecting a tournament type. Class calls oncallback when a selection is made.
    """
    def __init__(self, ctx: Context, oncallback: Callable[[str], Awaitable[None]], options: List[str]):
        super().__init__(ctx=ctx, options=options, max_selectable=1, min_selectable=1,
                        placeholder="select the tournament type you want a message for:")
        self.oncallback = oncallback

    async def callback(self, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        tournamenttype = self.values[0]
        await interaction.response.edit_message(content=f"{tournamenttype} selected", view=None)
        await self.oncallback(tournamenttype)


class GetPrize(SelectsUtility):
    """
    class for selecting a prize. Class calls oncallback when a selection is made.
    """
    def __init__(self, ctx: Context, oncallback: Callable[[str], Awaitable[None]], options: List[str]):
        super().__init__(ctx=ctx, options=options, max_selectable=1, min_selectable=1,
                         placeholder="select the prize you want a message for:")
        self.oncallback = oncallback

    async def callback(self, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        prize = self.values[0]
        await interaction.response.edit_message(content=f"{prize} selected", view=None)
        await self.oncallback(prize)


class PmTournament(discord.ui.View):
    """
    view for pmtournament
    """
    def __init__(self, ctx: Context, databasepath: str):
        """

        :param ctx:
        :param databasepath: path to the eventconfig database.
        """
        super(PmTournament, self).__init__()
        self.ctx = ctx
        self.databasepath = databasepath
        self.tournament = None
        self.prize = None
        self.both = False

    @discord.ui.button(label='tournamenttype', style=discord.ButtonStyle.green)
    async def tournamenttype(self, button: discord.Button, interaction: discord.Interaction):
        """
        user registers for a specific tournament type showing up.
        :param button:
        :param interaction:
        :return:
        """
        await self._tournamenttype(button, interaction)

    async def _tournamenttype(self, button: discord.Button, interaction):
        """
        so it can be called inside the class without it being affected by the decorator.
        :param button:
        :param interaction:
        :return:
        """
        if not await self.isOwner(interaction): return
        tournamenttypes = ["ubers", "self caught", "little cup", "monotype", "set level 100"]
        await self.ctx.send("please select the tournament type: ",
                            view=SelectsView(self.ctx, tournamenttypes, self.tournamentmaker))

    @discord.ui.button(label="prize", style=discord.ButtonStyle.green)
    async def prize(self, button, interaction: discord.Interaction):
        """
        user registers for a specific tournament prize showing up.
        :param button:
        :param interaction:
        :return:
        """
        await self._prize(button=button, interaction=interaction)

    async def _prize(self, button, interaction):
        """
        so it can be called inside the class without it being affected by the decorator.
        :param button:
        :param interaction:
        :return:
        """
        if not await self.isOwner(interaction): return
        await self.ctx.send("please select the prize: ",
                            view=SelectsView(self.ctx, gettournamentprizes(), self.tournamentprizemaker))

    @discord.ui.button(label="both", style=discord.ButtonStyle.green)
    async def both(self, button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        self.both = True
        await self._tournamenttype(button, interaction)

    def tournamentmaker(self, options: List[str]):
        return GetTournament(self.ctx, oncallback=self.__ontournamenttypecallback, options=options)

    def tournamentprizemaker(self, options: List[str]):
        return GetPrize(self.ctx, oncallback=self.__onprizecallback, options=options)

    async def __ontournamenttypecallback(self, tournamenttype):
        self.tournament = tournamenttype
        await self.__onanycallback()

    async def __onprizecallback(self, prize):
        self.prize = prize
        await self.__onanycallback()

    async def __onanycallback(self):
        symbol = "|"
        if self.both:
            symbol = "&"
            if self.prize is None:
                await self.ctx.send("please select the prize: ",
                                    view=SelectsView(self.ctx, gettournamentprizes(), self.tournamentprizemaker))
                return
            elif self.tournament is None:
                await self.ctx.send("please select the prize: ",
                                    view=SelectsView(self.ctx, gettournamentprizes(), self.tournamentprizemaker))
                return
            # both not None, so we can start entering it in the database.
        query = "INSERT INTO pmtournament(playerid, tournament, prize, comparator) VALUES(?, ?, ?, ?)"

        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute(query, (self.ctx.author.id, self.tournament, self.prize, symbol))
            conn.commit()
        except sqlite3.IntegrityError:
            await self.ctx.send("can not insert a duplicate configuration!")
            return
        finally:
            conn.close()

        if self.tournament is not None and self.prize is not None:
            await self.ctx.send(f"you will now get a pm if a {self.tournament} shows up with prize {self.prize}.")
        elif self.tournament is not None:
            await self.ctx.send(f"you will now get a pm if a {self.tournament} starts.")
        elif self.prize is not None:
            await self.ctx.send(f"you will now get a pm if a tournament with prize {self.prize} starts.")

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        if interaction.guild.id != self.ctx.guild.id or interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True