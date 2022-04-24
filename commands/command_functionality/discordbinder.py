import discord
from discord import User

from commands.sendable import Sendable
from commands.interractions.discord_binder import DiscordBinder


async def bind(sendable: Sendable, accountname: str, userid: int):
    embed = discord.Embed(title="Accountbinding",
                              description=f"{accountname} has requested to bind his ppo account with your discord account!")
    embed.add_field(name="what does this mean?",
                    value="That means that the commands done in any local chat ingame (like `.lle nightraiders`) "
                          "would be sent to your discord account.", inline=False)
    embed.add_field(name="this wasn't me",
                    value="you could deny this specific ppo user from binding with your discord account,"
                          " and he won't be able to send future requests to bind to your user account (you can undo this with a command on discord).",
                    inline=False)
    embed.add_field(name="I don't want any message about this in the future",
                    value="you can press `prevent all accountbinding in the future` if you don't want any messages"
                          " like this one at all anymore. This can be undone with `{future_command}` in discord",
                    inline=False)
    view = DiscordBinder(accountname, userid)
    await sendable.send(embed=embed, view=view)
