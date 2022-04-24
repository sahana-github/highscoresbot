from commands.sendable import Sendable
from ppobyter.ingame_commands.context import Context
from commands.command_functionality import discordbinder


async def bind(ctx: Context, sendable: Sendable, userid: int):
    await discordbinder.bind(sendable, ctx.user, userid)


async def unbind(ctx: Context, sendable: Sendable, userid: int):
    await discordbinder.removebinding(sendable, ctx.user, userid)


async def unbindall(ctx: Context, sendable: Sendable):
    await discordbinder.unbindall(ctx.user, ctx.client)
