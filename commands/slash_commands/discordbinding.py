from discord import Client, app_commands, Interaction
from discord.ext import commands
from commands.command_functionality import discordbinder
from commands.command_functionality.discordbinder import ingamecmd_help
from commands.sendable import Sendable


class DiscordBinding(commands.Cog):
    def __init__(self, client: commands.bot.Bot):
        self.client = client

    discordbindinggroup = app_commands.Group(name="discord_binding_group",
                                             description="ability to use commands ingame that get sent to discord.")

    @discordbindinggroup.command(name="showbindings")
    async def showbindings(self, interaction: Interaction):
        await discordbinder.showbindings(Sendable(interaction), interaction.user.id)

    @discordbindinggroup.command(name="removebinding")
    async def removebinding(self, interaction: Interaction, ppousername: str):
        await discordbinder.removebinding(Sendable(interaction), ppousername, interaction.user.id)

    @discordbindinggroup.command(name="unblock")
    async def unblock(self, interaction: Interaction, ppousername: str):
        await discordbinder.unblock(Sendable(interaction), ppousername, interaction.user.id)

    @discordbindinggroup.command(name="unblockall")
    async def unblockall(self, interaction: Interaction):
        """
        enables requesting account bindings if they got disabled. Individual blocked players will remain
        """
        await discordbinder.unblockall(Sendable(interaction), interaction.user.id)

    @discordbindinggroup.command(name="help")
    async def help(self, interaction: Interaction):
        await ingamecmd_help(Sendable(interaction))


async def setup(client):
    await client.add_cog(DiscordBinding(client))
