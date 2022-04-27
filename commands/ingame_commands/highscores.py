from commands.command_functionality import highscores
from commands.sendable import Sendable
from ppobyter.ingame_commands.context import Context
import asyncio

def get_clancommands():
    cmddict = {}
    for cmdname, cmd in highscores.get_clancommands().items():
        def makecmd(cmd):
            return lambda ctx, sendable, clanname: asyncio.run(cmd(sendable, clanname))
        cmddict[cmdname] = makecmd(cmd)
    return cmddict
