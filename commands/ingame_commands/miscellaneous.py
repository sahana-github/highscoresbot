from commands.command_functionality.discordbinder import ingamecmd_help
from commands.sendable import Sendable
from ppobyter.ingame_commands.context import Context


async def helpcmd(ctx: Context, sendable: Sendable):
    await ingamecmd_help(sendable, list(ctx.ingamecommandclient.commands.keys()))
