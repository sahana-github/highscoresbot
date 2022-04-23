from discord import app_commands, Interaction
from discord.ext import commands
from commands.command_functionality import pmconfig
from commands.interractions.pmconfig.pmswarm import swarmpokemonautocomplete, swarmlocationautocomplete
from commands.interractions.pmconfig.pmtournament import tournamenttypeautocomplete, tournamentprizeautocomplete
from commands.interractions.pmconfig.pmworldboss import worldbosspokemonautocomplete, worldbosslocationautocomplete
from commands.sendable import Sendable


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
        sendable = Sendable(interaction)
        await pmconfig.pmgoldrush(sendable)

    @pmconfiggroup.command(name="pmhoney")
    async def pmhoney(self, interaction: Interaction):
        sendable = Sendable(interaction)
        await pmconfig.pmhoney(sendable)

    @pmconfiggroup.command(name='pmswarm')
    @app_commands.autocomplete(pokemon=swarmpokemonautocomplete,
                               location=swarmlocationautocomplete)
    async def pmswarm(self, interaction: Interaction, pokemon: str = None, location: str = None):
        sendable = Sendable(interaction)
        await pmconfig.pmswarm(sendable, pokemon, location)

    @pmconfiggroup.command(name="pmworldboss")
    @app_commands.autocomplete(pokemon=worldbosspokemonautocomplete,
                               location=worldbosslocationautocomplete)
    async def pmworldboss(self, interaction: Interaction, pokemon: str=None, location: str=None):
        sendable = Sendable(interaction)
        await pmconfig.pmworldboss(sendable, pokemon, location)

    @pmconfiggroup.command(name="pmtournament")
    @app_commands.autocomplete(tournament=tournamenttypeautocomplete,
                               prize=tournamentprizeautocomplete
                               )
    async def pmtournament(self, interaction: Interaction, prize: str = None, tournament: str = None):
        sendable = Sendable(interaction)
        await pmconfig.pmtournament(sendable, prize, tournament)

    @pmconfiggroup.command(name="removepmconfig")
    async def removepmconfig(self, interaction: Interaction):
        sendable = Sendable(interaction)
        await pmconfig.removepmconfig(sendable)


async def setup(client):
    await client.add_cog(Pmconfig(client))
