import inspect
import sqlite3
from typing import List

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

    async def on_message(self, ctx: Context):
        if ctx.chat not in self.scopes:
            return
        if ctx.message[0] != self.prefix:
            return
        splittedcmd = ctx.message[len(self.prefix):].split(" ")
        cmd = self.commands.get(splittedcmd[0], None)
        if cmd is None:
            return

        if splittedcmd[0] == "bind":
            users = [await self._fetch_user(discord_id=int(splittedcmd[1]), requestinguser=ctx.user)]
        else:
            users = await self._fetch_discord_users(ctx.user)
        await self.invoke_command(ctx, cmd, users, splittedcmd[1:])

    async def invoke_command(self, ctx, command, users, args, requirepermissions=True):
        for user in users:
            print(type(command))
            if inspect.iscoroutinefunction(command):
                await command(ctx, Sendable(user), *args)
            else:
                command(ctx, Sendable(user), *args)

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

    def register_command(self, commandname, action):
        if self.commands.get(commandname) is not None:
            raise ValueError("command already registered!")
        self.commands[commandname] = action
