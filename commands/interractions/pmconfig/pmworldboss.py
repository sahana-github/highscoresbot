import sqlite3
from typing import Callable

import discord

from commands.interractions.selectsutility import SelectsUtility
from commands.interractions.selectsview import SelectsView



class GetPokemon(SelectsUtility):
    def __init__(self, ctx, oncallback: Callable[[str], None], options):
        super().__init__(ctx=ctx, options=options, max_selectable=1, min_selectable=1,
                        placeholder="select the worldboss you want a message for:")
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


class PmWorldboss(discord.ui.View):
    def __init__(self, ctx, databasepath):
        super(PmWorldboss, self).__init__()
        self.ctx = ctx
        self.databasepath = databasepath
        self.pokemon = None
        self.location = None
        self.both = False

    @discord.ui.button(label='Location', style=discord.ButtonStyle.green)
    async def location(self, button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        worldbosslocations = ["deep viridian forest", "deep viridian forest 2", "power plant", "diglett's cave",
                              "route 11", "route 12", "route 13", "route 14", "route 15", "route 16", "route 17",
                              "route 18", "mt ember", "berry forest", "route 23",  # end kanto
                              "route 26", "route 27", "route 29", "route 30", "route 31", "route 32", "route 33",
                              "route 34", "ilex forest", "route 35", "national park", "route 36", "route 37",
                              "route 38", "route 39", "route 42", "route 43", "route 44", "mossy cave", "route 45",
                              "route 46", "route 48",  # end johto
                              "route 28", "route 101", "route 102", "route 103", "route 104", "route 110", "route 111",
                              "route 112", "route 113", "route 114", "route 115", "route 116", "rusturf tunnel",
                              "route 117", "route 118", "route 119", "route 120", "route 121", "route 123",  # end hoenn
                              "route 201", "route 202", "route 203", "route 204", "route 205", "route 206", "route 207",
                              "route 208", "route 209", "route 210 a", "route 210 b", "route 211", "route 212 a",
                              "route 212 b", "route 224"  # end sinnoh
                              ]
        await self.ctx.send("please select the location: (sorted from kanto-johto)",
                            view=SelectsView(self.ctx, worldbosslocations, self.worldbosslocationmaker))

    @discord.ui.button(label="Pokemon", style=discord.ButtonStyle.green)
    async def pokemon(self, button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        await self.ctx.send("please select the worldboss pokemon: ",
                            view=SelectsView(self.ctx, ['articuno', 'azelf', 'cresselia', 'darkrai', 'entei',
                                                        'giratina', 'heatran', 'latias', 'latios', 'mesprit', 'mew',
                                                        'moltres', 'raikou', 'regigigas', 'shaymin', 'suicune', 'uxie',
                                                        'yveltal', 'zapdos'], self.worldbosspokemonmaker))

    @discord.ui.button(label="both", style=discord.ButtonStyle.green)
    async def both(self, button, interaction: discord.Interaction):
        if not await self.isOwner(interaction): return
        self.both = True
        await self.ctx.send("please select the worldboss pokemon: ",
                            view=SelectsView(self.ctx, ['articuno', 'azelf', 'cresselia', 'darkrai', 'entei',
                                                        'giratina', 'heatran', 'latias', 'latios', 'mesprit', 'mew',
                                                        'moltres', 'raikou', 'regigigas', 'shaymin', 'suicune', 'uxie',
                                                        'yveltal', 'zapdos'], self.worldbosspokemonmaker))

    def worldbosslocationmaker(self, options):
        return GetLocation(self.ctx, oncallback=self.__onlocationcallback, options=options)

    def worldbosspokemonmaker(self, options):
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
                await self.ctx.send("please select the worldboss pokemon: ",
                                    view=SelectsView(self.ctx, ['mew', 'articuno', 'suicune', 'darkrai', 'darkrai', 'mesprit', 'shaymin', 'latias', 'regigigas',
                       'uxie', 'entei', 'azelf', 'suicune', 'zapdos', 'cresselia', 'moltres', 'latios', 'heatran',
                       'heatran', 'azelf', 'raikou', "giratina", "yveltal"],
                                                     self.worldbosspokemonmaker))
                return
            elif self.location is None:
                worldbosslocations = ["deep viridian forest", "deep viridian forest 2", "power plant", "diglett's cave",
                                      "route 11", "route 12", "route 13", "route 14", "route 15", "route 16",
                                      "route 17",
                                      "route 18", "mt ember", "berry forest", "route 23",  # end kanto
                                      "route 26", "route 27", "route 29", "route 30", "route 31", "route 32",
                                      "route 33",
                                      "route 34", "ilex forest", "route 35", "national park", "route 36", "route 37",
                                      "route 38", "route 39", "route 42", "route 43", "route 44", "mossy cave",
                                      "route 45",
                                      "route 46", "route 48",  # end johto
                                      "route 28", "route 101", "route 102", "route 103", "route 104", "route 110",
                                      "route 111",
                                      "route 112", "route 113", "route 114", "route 115", "route 116", "rusturf tunnel",
                                      "route 117", "route 118", "route 119", "route 120", "route 121", "route 123",
                                      # end hoenn
                                      "route 201", "route 202", "route 203", "route 204", "route 205", "route 206",
                                      "route 207",
                                      "route 208", "route 209", "route 210 a", "route 210 b", "route 211",
                                      "route 212 a",
                                      "route 212 b", "route 224"  # end sinnoh
                                      ]
                await self.ctx.send("please select the worldboss location: (sorted from kanto-johto)",
                                    view=SelectsView(self.ctx, worldbosslocations, self.worldbosslocationmaker))
                return
            # both not None, so we can start entering it in the database.
        query = "INSERT INTO pmworldboss(playerid, location, boss, comparator) VALUES(?, ?, ?, ?)"

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
            await self.ctx.send(f"you will now get a pm if a {self.pokemon} worldboss shows up at {self.location}.")
        elif self.pokemon is not None:
            await self.ctx.send(f"you will now get a pm if a {self.pokemon} worldboss shows up.")
        elif self.location is not None:
            await self.ctx.send(f"you will now get a pm if a worldboss shows up at {self.location}.")

    async def isOwner(self, interaction: discord.Interaction) -> bool:
        if interaction.guild.id != self.ctx.guild.id or interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("only the user who used the command can use these buttons!")
            return False
        return True