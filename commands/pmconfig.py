import asyncio
from typing import Callable, Union, Iterable, Tuple, List
import enchant
from discord.ext import commands
import sqlite3

from commands.interractions.pmconfig.pmgoldrush import PmGoldrush
from commands.interractions.pmconfig.pmhoney import PmHoney
from commands.interractions.pmconfig.pmswarm import PmSwarm
from commands.interractions.pmconfig.pmtournament import PmTournament
from commands.interractions.pmconfig.pmworldboss import PmWorldboss
from commands.interractions.pmconfig.removepmconfig import RemovePmConfig
from commands.interractions.selectsview import SelectsView
from commands.utils.utils import getgoldrushlocations, gethoneylocations
from discord.ext.commands.context import Context


class Pmconfig(commands.Cog):
    """
    This class contains commands for the configuration of events in pm's.
    """
    def __init__(self, client):
        self.client = client
        self.databasepath = "./eventconfigurations.db"

    @commands.command(name="pmgoldrush")
    async def pmgoldrush(self, ctx: Context):
        """
        The user will receive a pm if a goldrush happens at the provided location.
        It is checked if it is a valid location.
        :param ctx: discord context
        :param location: the location where the goldrush happens.
        """
        view = SelectsView(ctx, options=getgoldrushlocations(),
                           selectoption=lambda locations: PmGoldrush(ctx, locations, self.databasepath))
        await ctx.send("for what locations do you want a pm when a goldrush pops up?", view=view)


    @commands.command(name="pmhoney")
    async def pmhoney(self, ctx: Context, *location: str):
        """
        The user will receive a pm if honey gets spread at the provided location.
        :param ctx: discord context
        :param location: the location where the honey gets spread.
        :todo input validation for the location
        """
        view = SelectsView(ctx, options=gethoneylocations(),
                           selectoption=lambda locations: PmHoney(ctx, locations, self.databasepath))
        await ctx.send("for what locations do you want a pm when a honey gets spread?", view=view)

    @commands.command(name='pmswarm')
    async def pmswarm(self, ctx: Context):
        """
        starts the configuration of pming a swarm to the user.
        The user gets 3 options:
        1. location
        2. pokemon
        3. both
        With location the user gets a pm that a swarm appeared at that location.
        With pokemon the user gets a pm if one of the 2 swarm pokemon is the pokemon the user provided.
        With both the user only gets a pm if the provided pokemon shows up at the provided location.
        :param ctx: discord context
        There is inputvalidation for both the swarm location and the swarm pokemon.
        """
        await ctx.send("ok", view=PmSwarm(ctx, self.databasepath))


    @commands.command(name="pmworldboss")
    async def pmworldboss(self, ctx):
        """
        starts the configuration of pming a worldboss to the user.
        The user gets 3 options:
        1. location
        2. worldboss pokemon
        3. both
        With location the user gets a pm that a worldboss appeared at that location.
        With worldboss pokemon the user gets a pm if the worldboss provided shows up at any location.
        With both the user only gets a pm if the provided worldboss pokemon shows up at the provided location.
        There is inputvalidation for the worldboss pokemon, but not for the location.
        :param ctx: discord context
        """
        await ctx.send("ok", view=PmWorldboss(ctx, self.databasepath))


    @commands.command(name="pmtournament")
    async def pmtournament(self, ctx):
        """
        starts the configuration of pming a tournament to the user.
        The user gets 3 options:
        1. prize
        2. tournament type
        3. both
        With prize the user gets a pm if a tournament with the specified prize shows up.
        with tournament type the user gets a pm if a tournament of the specified type shows up.
        With both the user only gets a pm if the provided tournament shows up with the specified price.
        There is inputvalidation for the tournament type, but not for the prize (yet)
        :param ctx: discord context
        :todo input validation for prize
        """
        await ctx.send("ok", view=PmTournament(ctx, self.databasepath))



    @commands.command(name="removepmconfig")
    async def removepmconfig(self, ctx: Context):
        """
        Starts user interaction to remove pm configuration of certain events.
        Fails if the time limit of 30 seconds to respond has expired.
        Asks for either a list of id's or a single id, and deletes those. Note that the id's are just list indexes, it
        gets the values at those list indexes to delete the configurations.
        :param ctx: discord context.
        """
        await ctx.send("ok", view=RemovePmConfig(ctx, self.databasepath))




def setup(client):
    client.add_cog(Pmconfig(client))
    #help(Button)