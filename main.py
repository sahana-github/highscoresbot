"""
This file runs the bot for processing commands and handles errors when those happen in commands.
"""
import os

from discord import errors
from discord.ext import commands
import discord.ext.commands
from discord.ext.commands import CommandNotFound, errors
from discord.ext.commands._types import BotT
from discord.ext.commands.errors import MissingRequiredArgument, CommandInvokeError, NoPrivateMessage
from discord.errors import Forbidden, NotFound
import traceback
from discord.ext.commands.context import Context








class Main(commands.Bot):
    def __init__(self, token):
        self.cog_files = ["commands.ingame_events", "commands.highscores", "commands.eventconfig",
                          "commands.miscellaneous", "commands.pmconfig"]
        intents = discord.Intents.default()
        intents.message_content = False
        super().__init__([".", "?"], intents=intents)
        self.__token = token

    async def on_ready(self):
        """
        waits for the client to get ready and adds DiscordComponents.
        :return:
        """
        for cog_file in self.cog_files:  # load in all commands
            await self.load_extension(cog_file)
            print("%s has loaded." % cog_file)
        await self.wait_until_ready()

    async def invoke(self, ctx: Context[BotT], /) -> None:
        """|coro|

        Invokes the command given under the invocation context and
        handles all the internal event dispatch mechanisms.

        .. versionchanged:: 2.0

            ``ctx`` parameter is now positional-only.

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to invoke.
        """
        if ctx.command is not None:
            self.dispatch('command', ctx)
            try:
                if await self.can_run(ctx, call_once=True):
                    await ctx.send("warning: All commands will move to slash commands soon.")
                    await ctx.command.invoke(ctx)
                else:
                    raise errors.CheckFailure('The global check once functions failed.')
            except errors.CommandError as exc:
                await ctx.command.dispatch_error(ctx, exc)
            else:
                self.dispatch('command_completion', ctx)
        elif ctx.invoked_with:
            exc = errors.CommandNotFound(f'Command "{ctx.invoked_with}" is not found')
            self.dispatch('command_error', ctx, exc)

    async def on_command_error(self, ctx: Context, error: Exception):
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
                    await ctx.author.send(
                        "I lack permissions to send messages in there! Contact a server administrator.")
                except Forbidden:
                    await ctx.send("I lack permissions to send you messages in pm!")
                return
            elif isinstance(error.original, NotFound):
                return
            else:
                await self.send_error(ctx, error)
        elif isinstance(error, MissingRequiredArgument):
            cmd = self.get_command("help")
            await cmd(ctx, str(ctx.command))
            return
        elif isinstance(error, NoPrivateMessage):
            await ctx.send("this command can only be used in discord servers!")
            return
        raise error

    async def send_error(self, ctx: Context, error: Exception, channelid: int = 893831090454790154):
        """
        this sends an error to the channel provided in the function, including some debug information.
        :param ctx: discord context
        :param error: the exception that has to be sent to the channel.
        :param channelid: The channel the error must be sent to.
        """
        chan = await self.fetch_channel(channelid)
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

    def run(self, *args, **kwargs):
        super(Main, self).run(token=self.__token, *args, **kwargs)


if __name__ == "__main__":
    Main(os.environ.get("token")).run()
