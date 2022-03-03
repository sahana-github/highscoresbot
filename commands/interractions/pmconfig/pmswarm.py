import sqlite3
from typing import Callable

import discord

from commands.interractions.selectsutility import SelectsUtility
from commands.interractions.selectsview import SelectsView
from commands.utils.utils import getswarmpokemons, getswarmlocations


class GetPokemon(SelectsUtility):
    def __init__(self, ctx, oncallback: Callable[[str], None], options):
        super().__init__(ctx=ctx, options=options, max_selectable=1, min_selectable=1,
                        placeholder="select the pokemon you want a message for:")
        self.oncallback = oncallback

    async def callback(self, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        pokemon = self.values[0]
        await interaction.response.edit_message(content=f"{pokemon} selected", view=None)
        await self.oncallback(pokemon)

class GetLocation(SelectsUtility):
    def __init__(self, ctx, oncallback: Callable[[str], None], options):
        super().__init__(ctx=ctx, options=options, max_selectable=1, min_selectable=1,
                         placeholder="select the location you want a message for:")
        self.oncallback = oncallback

    async def callback(self, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        location = self.values[0]
        await interaction.response.edit_message(content=f"{location} selected", view=None)
        await self.oncallback(location)


class PmSwarm(discord.ui.View):
    def __init__(self, ctx, databasepath):
        super(PmSwarm, self).__init__()
        self.ctx = ctx
        self.databasepath = databasepath
        self.pokemon = None
        self.location = None
        self.both = False

    @discord.ui.button(label='Location', style=discord.ButtonStyle.green)
    async def location(self, button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        await self.ctx.send("please select the location: ",
                            view=SelectsView(self.ctx, getswarmlocations(), self.swarmlocationmaker))

    @discord.ui.button(label="Pokemon", style=discord.ButtonStyle.green)
    async def pokemon(self, button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        await self.ctx.send("please select the pokemon: ",
                            view=SelectsView(self.ctx, getswarmpokemons(), self.swarmpokemonmaker))

    @discord.ui.button(label="both", style=discord.ButtonStyle.green)
    async def both(self, button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        self.both = True
        await self.ctx.send("please select the pokemon: ",
                            view=SelectsView(self.ctx, getswarmpokemons(), self.swarmpokemonmaker))

    def swarmlocationmaker(self, options):
        return GetLocation(self.ctx, oncallback=self.__onlocationcallback, options=options)

    def swarmpokemonmaker(self, options):
        return GetPokemon(self.ctx, oncallback=self.__onpokemoncallback, options=options)

    async def __onpokemoncallback(self, pokemon):
        self.pokemon = pokemon
        await self.__onanycallback()

    async def __onlocationcallback(self, location):
        self.location = location
        await self.__onanycallback()

    async def __onanycallback(self):
        symbol = "|"
        if self.both:
            symbol = "&"
            if self.pokemon is None:
                await self.ctx.send("please select the pokemon: ",
                                    view=SelectsView(self.ctx, getswarmpokemons(), self.swarmpokemonmaker))
                return
            elif self.location is None:
                await self.ctx.send("please select the location: ",
                                    view=SelectsView(self.ctx, getswarmlocations(), self.swarmlocationmaker))
                return
            # both not None, so we can start entering it in the database.
        query = "INSERT INTO pmswarm(playerid, location, pokemon, comparator) VALUES(?, ?, ?, ?)"

        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute(query, (self.ctx.author.id, self.location, self.pokemon, symbol))
            conn.commit()
        except sqlite3.IntegrityError:
            await self.ctx.send("can not insert a duplicate configuration!")
            return
        finally:
            conn.close()

        if self.pokemon is not None and self.location is not None:
            await self.ctx.send(f"you will now get a pm if a {self.pokemon} shows up at {self.location}.")
        elif self.pokemon is not None:
            await self.ctx.send(f"you will now get a pm if a {self.pokemon} shows up in a swarm.")
        elif self.location is not None:
            await self.ctx.send(f"you will now get a pm if a swarm shows up at {self.location}.")

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        if interaction.guild.id != self.ctx.guild.id or interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True