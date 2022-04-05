import sqlite3

import discord
from discord import app_commands, Interaction
from discord.app_commands import Choice
from discord.ext import commands
from commands.interractions.pmconfig.pmgoldrush import PmGoldrush
from commands.interractions.pmconfig.pmhoney import PmHoney
from commands.interractions.pmconfig.pmswarm import PmSwarm
from commands.interractions.pmconfig.pmtournament import PmTournament
from commands.interractions.pmconfig.pmworldboss import PmWorldboss
from commands.interractions.pmconfig.removepmconfig import RemovePmConfig
from commands.interractions.selectsview import SelectsView
from commands.utils.utils import getgoldrushlocations, gethoneylocations, gettournamentprizes, getswarmpokemons, \
    getswarmlocations
from discord.ext.commands.context import Context


class Pmconfig(commands.Cog):
    """
    This class contains commands for the configuration of events in pm's.
    """
    def __init__(self, client):
        self.client = client
        self.databasepath = "./eventconfigurations.db"

    pmconfiggroup = app_commands.Group(name="pmconfig", description="deals with sending ingame events to channels")

    @pmconfiggroup.command(name="pmgoldrush")
    async def pmgoldrush(self, interaction: Interaction):
        """
        The user will receive a pm if a goldrush happens at the provided location.
        It is checked if it is a valid location.
        :param ctx: discord context
        """
        view = SelectsView(interaction, options=getgoldrushlocations(),
                           selectoption=lambda locations: PmGoldrush(interaction, locations, self.databasepath))
        await interaction.response.send_message("for what locations do you want a pm when a goldrush pops up?", view=view)

    @pmconfiggroup.command(name="pmhoney")
    async def pmhoney(self, interaction: Interaction):
        """
        The user will receive a pm if honey gets spread at the provided location.
        """
        view = SelectsView(interaction, options=gethoneylocations(),
                           selectoption=lambda locations: PmHoney(interaction, locations, self.databasepath))
        await interaction.response.send_message("for what locations do you want a pm when a honey gets spread?",
                                                view=view)

    @pmconfiggroup.command(name='pmswarm')
    async def pmswarm(self, interaction: Interaction, pokemon: str=None, location: str=None):
        """
        @todo input validation once again
        """
        if pokemon is None and location is None:
            await interaction.response.send_message("select pokemon, location or both")
            return
        symbol = "|"
        if pokemon is not None and location is not None:
            symbol = "&"
        if pokemon is not None:
            pokemon = pokemon.lower()
            if pokemon not in getswarmpokemons():
                await interaction.response.send_message("not an available swarm pokemon. See "
                                                        "https://pokemon-planet.com/swarms for a list of available pokemon")
                return
        if location is not None:
            location = location.lower()
            if location not in getswarmlocations():
                await interaction.response.send_message("not an available swarm location. See "
                                                        "https://pokemon-planet.com/swarms for a list of available locations")
            # both not None, so we can start entering it in the database.
        query = "INSERT INTO pmswarm(playerid, location, pokemon, comparator) VALUES(?, ?, ?, ?)"

        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute(query, (interaction.user.id, location, pokemon, symbol))
            conn.commit()
        except sqlite3.IntegrityError:
            await interaction.response.send_message("can not insert a duplicate configuration!")
            return
        finally:
            conn.close()

        if pokemon is not None and location is not None:
            await interaction.response.send_message(f"you will now get a pm if a {pokemon} shows up at {location}.")
        elif pokemon is not None:
            await interaction.response.send_message(f"you will now get a pm if a {pokemon} shows up in a swarm.")
        elif location is not None:
            await interaction.response.send_message(f"you will now get a pm if a swarm shows up at {location}.")

    @pmconfiggroup.command(name="pmworldboss")
    async def pmworldboss(self, interaction: Interaction, pokemon: str=None, location: str=None):
        """
        ????
        """

        if pokemon is None and location is None:
            await interaction.response.send_message("select pokemon, location or both")
            return
        symbol = "|"
        if pokemon is not None and location is not None:
            symbol = "&"
        query = "INSERT INTO pmworldboss(playerid, location, boss, comparator) VALUES(?, ?, ?, ?)"
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute(query, (interaction.user.id, location, pokemon, symbol))
            conn.commit()
        except sqlite3.IntegrityError:
            await interaction.response.send_message("can not insert a duplicate configuration!")
            return
        finally:
            conn.close()
        if pokemon is not None and location is not None:
            await interaction.response.send_message(f"you will now get a pm if a {pokemon} worldboss shows up at {location}.")
        elif pokemon is not None:
            await interaction.response.send_message(f"you will now get a pm if a {pokemon} worldboss shows up.")
        elif location is not None:
            await interaction.response.send_message(f"you will now get a pm if a worldboss shows up at {location}.")

    @pmconfiggroup.command(name="pmtournament")
    @app_commands.choices(tournament=[Choice(name=i, value=i)
                                      for i in ["ubers", "self caught", "little cup", "monotype", "set level 100"]]
                          )
    async def pmtournament(self, interaction: Interaction, prize: str=None, tournament: str=None):
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
        if prize is None and tournament is None:
            await interaction.response.send_message("select tournamenttype, prize or both!")
        symbol = "|"
        if prize is not None and tournament is not None:
            symbol = "&"
        query = "INSERT INTO pmtournament(playerid, tournament, prize, comparator) VALUES(?, ?, ?, ?)"
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute(query, (interaction.user.id, tournament, prize, symbol))
            conn.commit()
        except sqlite3.IntegrityError:
            await interaction.response.send_message("can not insert a duplicate configuration!")
            return
        finally:
            conn.close()

        if tournament is not None and prize is not None:
            await interaction.response.send_message(f"you will now get a pm if a {tournament} shows up with prize "
                                                    f"{prize}.")
        elif tournament is not None:
            await interaction.response.send_message(f"you will now get a pm if a {tournament} starts.")
        elif prize is not None:
            await interaction.response.send_message(f"you will now get a pm if a tournament with prize {prize} starts.")




    @pmconfiggroup.command(name="removepmconfig")
    async def removepmconfig(self, interaction: Interaction):
        """
        Starts user interaction to remove pm configuration of certain events.
        Fails if the time limit of 30 seconds to respond has expired.
        Asks for either a list of id's or a single id, and deletes those. Note that the id's are just list indexes, it
        gets the values at those list indexes to delete the configurations.
        :param ctx: discord context.
        """
        await interaction.response.send_message("what event do you want to remove pmconfig of?",
                                                view=RemovePmConfig(interaction, self.databasepath))


async def setup(client):
    await client.add_cog(Pmconfig(client))
