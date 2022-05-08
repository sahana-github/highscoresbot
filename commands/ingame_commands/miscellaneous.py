from commands.command_functionality.discordbinder import ingamecmd_help
from commands.command_functionality import miscellaneous
from commands.sendable import Sendable
from ppobyter.ingame_commands.context import Context


async def helpcmd(ctx: Context, sendable: Sendable):
    await ingamecmd_help(sendable)


async def worldboss(ctx: Context, sendable: Sendable, playername):
    await miscellaneous.worldboss(sendable, playername=playername)


async def clanlist(ctx: Context, sendable: Sendable, clanname: str):
    await miscellaneous.clanlist(sendable, clanname)