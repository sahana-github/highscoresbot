from commands.command_functionality import ingame_events
from commands.sendable import Sendable
from ppobyter.ingame_commands.context import Context


async def lastonline(ctx: Context, sendable: Sendable, playername=None):
    if playername == "":
        playername = None
    await ingame_events.lastonline(sendable, playername)


async def getclanencounters(ctx: Context, sendable: Sendable, clanname: str):
    await ingame_events.getclanencounters(sendable, clanname)
