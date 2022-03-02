"""
This file runs the bot for processing commands and handles errors when those happen in commands.
"""
import os
import discord.ext.commands
from discord.ext.commands import CommandNotFound
from discord.ext.commands.errors import MissingRequiredArgument, CommandInvokeError, NoPrivateMessage
from discord.errors import Forbidden, NotFound
import traceback
from discord.ext.commands.context import Context


client = discord.ext.commands.Bot(command_prefix=[".", "?"])

# cog_files = ['commands.eventconfig', 'commands.pmconfig', 'commands.highscores', 'commands.miscellaneous',
#              'commands.ingame_events']
cog_files = ['commands.eventconfig', 'commands.highscores']

@client.event
async def on_command_error(ctx: Context, error: Exception):
    """
    handles errors, and sends those to the error channel if the exception is not handled in another way.
    When missing a required argument the help command for the command that was attempted to be used will be send.
    :param ctx: discord context.
    :param error: the exception that has to be handled.
    :raises: error: The exception if it could not be handled.
    """
    if isinstance(error, CommandNotFound):
        return
    elif isinstance(error, CommandInvokeError):
        if isinstance(error.original, Forbidden):
            try:
                await ctx.author.send("I lack permissions to send messages in there! Contact a server administrator.")
            except Forbidden:
                await ctx.send("I lack permissions to send you messages in pm!")
            return
        elif isinstance(error.original, NotFound):
            return
        else:
            await send_error(ctx, error)
    elif isinstance(error, MissingRequiredArgument):
        cmd = client.get_command("help")
        await cmd(ctx, str(ctx.command))
        return
    elif isinstance(error, NoPrivateMessage):
        await ctx.send("this command can only be used in discord servers!")
        return
    raise error


async def send_error(ctx: Context, error: Exception, channelid: int = 893831090454790154):
    """
    this sends an error to the channel provided in the function, including some debug information.
    :param ctx: discord context
    :param error: the exception that has to be sent to the channel.
    :param channelid: The channel the error must be sent to.
    """
    chan = await client.fetch_channel(channelid)
    embed = discord.Embed(title="Error!")
    arguments = [str(i) for i in ctx.args[2:]]
    txt = " ".join(arguments)
    if txt == "":
        txt = "no arguments."
    embed.add_field(name=str(ctx.command), value=txt, inline=False)
    origin = "```" + ''.join(traceback.format_exception(error.__class__, error, error.__traceback__)) + "```"

    await chan.send(embed=embed)
    temp = "```"
    for line in origin.split("\n"):
        print(line)
        if len(temp + line) < 1995:
            temp += line + "\n"
        else:
            temp += "```"
            await chan.send(temp)
            temp = "```"
    if temp != "```":
        await chan.send(temp + "```")


@client.event
async def on_ready():
    """
    waits for the client to get ready and adds DiscordComponents.
    :return:
    """
    await client.wait_until_ready()

for cog_file in cog_files:  # load in all commands.
    client.load_extension(cog_file)
    print("%s has loaded." % cog_file)


if __name__ == "__main__":
    client.run(os.environ.get("token"))
