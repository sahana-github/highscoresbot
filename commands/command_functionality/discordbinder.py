import sqlite3

import discord
from discord import User, Client

from commands.sendable import Sendable
from commands.interractions.discord_binder import DiscordBinder
from pathmanager import PathManager




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


async def unbindall(accountname: str, client: Client):
    with sqlite3.connect(PathManager().getpath("eventconfigurations.db")) as conn:
        cur = conn.cursor()
        cur.execute("SELECT discordid FROM discord_bindings WHERE pponame=?", (accountname,))
        userids = [row[0] for row in cur.fetchall()]
        cur.execute("DELETE FROM discord_bindings WHERE pponame=?", (accountname,))
        conn.commit()
    for userid in userids:
        try:
            user = await client.fetch_user(userid)
            if user is None:
                continue
            await user.send(f"{accountname} has unbound with your discord account!")
        except Exception as e:
            pass


async def showbindings(sendable: Sendable, userid: int):
    with sqlite3.connect(PathManager().getpath("eventconfigurations.db")) as conn:
        cur = conn.cursor()
        cur.execute("SELECT pponame FROM discord_bindings WHERE discordid=?", (userid,))
        pponames = [row[0] for row in cur.fetchall()]
    await sendable.send("Your discord account has been bound to the following ppo players: \n`" +
                        "\n".join(pponames) + "`")


async def removebinding(sendable: Sendable, ppousername: str, userid: int):
    with sqlite3.connect(PathManager().getpath("eventconfigurations.db")) as conn:
        cur = conn.cursor()
        result = cur.execute("DELETE FROM discord_bindings WHERE discordid=? AND pponame=?", (userid, ppousername))
        conn.commit()
    if result.rowcount:
        await sendable.send(f"Binding with player {ppousername} removed!")
    else:
        await sendable.send(f"Unable to unbind with {ppousername}, you might not have a binding with that user.")


async def unblock(sendable: Sendable, ppousername: str, userid: int):
    with sqlite3.connect(PathManager().getpath("eventconfigurations.db")) as conn:
        cur = conn.cursor()
        result = cur.execute("DELETE FROM discord_blocked WHERE pponame=? AND discordid=?", (ppousername, userid))
        conn.commit()
    if result.rowcount:
        await sendable.send(f"Unblocked {ppousername} from binding!")
    else:
        await sendable.send(f"unable to unblock {ppousername}. The player might not have been blocked at all.")


async def unblockall(sendable: Sendable, userid: int):
    with sqlite3.connect(PathManager().getpath("eventconfigurations.db")) as conn:
        cur = conn.cursor()
        result = cur.execute("DELETE FROM everything_discord_blocked WHERE discordid=?", (userid,))
        conn.commit()
    if result.rowcount:
        await sendable.send("you undid blocking everyone from binding with your account.")
    else:
        await sendable.send("You didn't block everyone from binding with your account.")
