import inspect
import sqlite3
from typing import List, Callable, Any, Optional, Union, Coroutine, Awaitable

from discord import Client, User

from commands.sendable import Sendable
from ppobyter.ingame_commands.context import Context
from ppobyter.ingame_commands.ppochat import PPOChat


class IngamecommandClient:
    def __init__(self, prefix, discordclient: Client, scopes: List[PPOChat]=None):
        """

        :param prefix:
        :param scopes: what chats to receive messages from. Available chats:
                                                                    ["trade", "local", "english", "non-english"]
        """
        if scopes is None:
            scopes = [PPOChat.LOCAL_CHAT]
        self.discordclient = discordclient
        self.prefix = prefix
        self.scopes = scopes
        self.commands = {}
        self.binding_not_required_commands = []

    async def on_message(self, ctx: Context):
        """
        checks if the message context contains a command, and executes that command if it is a command.
        :param ctx: message context
        :return:
        """
        if ctx.chat not in self.scopes:
            return
        if ctx.message[0] != self.prefix:
            return
        splittedcmd = ctx.message[len(self.prefix):].split(" ")
        cmd = self.commands.get(splittedcmd[0], None)
        if cmd is None:
            return
        ctx.setClient(self.discordclient)
        ctx.setIngameCommandClient(self)
        if splittedcmd[0] in self.binding_not_required_commands:
            users = []
            user = await self._fetch_user(discord_id=int(splittedcmd[1]), requestinguser=ctx.user)
            if user is not None:
                users.append(user)
        else:
            users = await self._fetch_discord_users(ctx.user)
        await self.invoke_command(ctx, cmd, users, splittedcmd[1:])

    async def invoke_command(self, ctx: Context,
                             command: Callable[[Context, Sendable, Optional[Any]], Union[None, Awaitable[Any]]],
                             users: List[User],
                             args: List[Any]):
        """
        executes the given command on the users.
        :param ctx: the command context.
        :param command: the command to be executed.
        :param users: list of users to send the command to.
        :param args: arguments to pass to the function
        :return:
        """
        for user in users:
            try:
                if inspect.iscoroutinefunction(command):
                    await command(ctx, Sendable(user), *args)
                else:
                    command(ctx, Sendable(user), *args)
            except Exception as e:
                print(e)

    async def _fetch_user(self, discord_id: int, requestinguser: str):
        with sqlite3.connect(r"../eventconfigurations.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM everything_discord_blocked WHERE discordid=?", (discord_id,))
            if cur.fetchall():
                return
            cur.execute("SELECT * FROM discord_blocked WHERE discordid=? AND pponame=?",
                        (discord_id, requestinguser))
            if cur.fetchall():
                return
        try:
            return await self.discordclient.fetch_user(discord_id)
        except Exception as e:
            pass

    async def _fetch_discord_users(self, ppo_username) -> List[User]:
        with sqlite3.connect(r"../eventconfigurations.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT discordid FROM discord_bindings WHERE pponame=?", (ppo_username,))
            userids = [row[0] for row in cur.fetchall()]
        users = []
        for userid in userids:
            try:
                user = await self.discordclient.fetch_user(userid)
                if user not in users:
                    users.append(user)
            except Exception as e:
                pass
        return users

    def register_command(self, commandname, action, binding_not_required=False):
        if self.commands.get(commandname) is not None:
            raise ValueError("command already registered!")
        self.commands[commandname] = action
        if binding_not_required:
            self.binding_not_required_commands.append(commandname)
