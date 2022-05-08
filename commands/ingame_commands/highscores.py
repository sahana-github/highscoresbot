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


def get_top10commands():
    cmddict = {}
    for cmdname, cmd in highscores.get_top10cmds().items():
        def makecmd(cmd):
            return lambda ctx, sendable, clanname=None: asyncio.run(cmd(sendable, clanname))
        cmddict[cmdname] = makecmd(cmd)
    return cmddict


async def getplayer(ctx: Context, sendable: Sendable, username: str):
    await highscores.getplayer(sendable, username)


async def mapcontrol(ctx: Context, sendable: Sendable, clanname=None):
    if clanname == "":
        clanname = None
    await highscores.mapcontrol(sendable, clanname)


async def getclan(ctx: Context, sendable: Sendable, clanname):
    await highscores.getclan(sendable, clanname)
