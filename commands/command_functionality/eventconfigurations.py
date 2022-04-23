import asyncio
import re

import discord
from discord import NotFound, Forbidden, app_commands, Interaction
from discord.ext import commands
import sqlite3
from commands.interractions.eventconfig.register import Register
from commands.interractions.playerconfig.playerconfig import PlayerConfig
from commands.interractions.playerconfig.removememberconfig import RemoveMemberConfig
from commands.interractions.resultmessageshower import ResultmessageShower
from commands.interractions.selectsview import SelectsView
from commands.sendable import Sendable
from commands.utils.utils import haspermissions, tablify
from discord.utils import escape_mentions, MISSING
from typing import Union

databasepath = "./eventconfigurations.db"


async def __eventnamecheck(sendable: Sendable, eventname: str) -> bool:
    """
    Checks if the provided eventname is a existing event, and shows what events are possible if the eventname is
    invalid.
    :param ctx: discord context
    :param eventname: the eventname.
    :return boolean, True if the eventname is valid.
    """
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    cur.execute("SELECT eventname FROM eventnames WHERE eventname=?", (eventname,))
    result = cur.fetchall()
    if len(result) == 0:
        cur.execute("SELECT eventname FROM eventnames")
        eventnames = [row[0] for row in cur.fetchall()]
        conn.close()
        await sendable.send(f"invalid eventname '{eventname}'! Possible events:\n" + ", ".join(eventnames))
        return False
    conn.close()
    return True



async def setperms(sendable: Sendable, role: discord.Role):
    """
    This command gives permission to the specified role to adjust eventconfigurations for this server.
    Only useable by administrators of the server.
    :param ctx: discord context
    :param role: the role id or the role mention. Union[int, str]
    """
    if not sendable.user.guild_permissions.administrator:
        await sendable.send("only administrators can use this command!")
        return
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    cur.execute("INSERT INTO permissions(guildid, roleid) VALUES(?,?)", (sendable.guild.id, role.id))
    conn.commit()
    conn.close()
    await sendable.send("role successfully given permissions.")


async def removeperms(sendable: Sendable, role: discord.Role):
    """
    Removes the permissions of a role to adjust eventconfigurations for this server.
    Only useable by administrators of the server.
    :param ctx: discord context
    :param role: the role id or the role mention. Union[int, str]
    """
    with sqlite3.connect(databasepath) as conn:
        cur = conn.cursor()
        result = cur.execute("DELETE FROM permissions WHERE guildid=? AND roleid=?", (sendable.guild.id, role.id))
        conn.commit()
    if result.rowcount:
        await sendable.send("Role successfully removed from permissions.")
    else:
        await sendable.send("that role had no permissions.")


async def getperms(sendable: Sendable):
    """
    Gets the roles that have permission to adjust eventconfigurations.
    :param ctx: discord context
    """
    with sqlite3.connect(databasepath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT roleid FROM permissions WHERE guildid=?", (sendable.guild.id,))
        result = cur.fetchall()
    message = ""
    for role in result:
        role = sendable.guild.get_role(int(role[0]))
        if role is not None:
            message += str(role) + "\n"
    message = escape_mentions(message)
    if message != "":
        await sendable.send(message)
    else:
        await sendable.send("no permissions set.")


async def register(sendable: Sendable, channel: discord.TextChannel = None):
    """
    Registers an event at the specified channel. If the channel is not specified the channel is the channel the
    command is used from.
    :param ctx: discord context
    :param channel: The channel to send the event to. Default channel where command was used.
    """
    if not haspermissions([role.id for role in sendable.user.roles], sendable.guild.id) and not\
            sendable.user.guild_permissions.administrator:
        await sendable.send("insufficient permissions to use this command!")
        return
    chan = channel if channel is not None else sendable.channel
    with sqlite3.connect(databasepath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT eventname FROM eventnames")
        eventnames = [row[0] for row in cur.fetchall()]
    eventnames.sort()
    view = SelectsView(sendable, eventnames, lambda options: Register(sendable, options, chan,
                                                                      databasepath))
    await sendable.send(f"Select events you want a message for in {chan.mention}", view=view)


async def settime(sendable: Sendable, eventname: str, time: int = None):
    """
    Sets the time in minutes the event should stay in the channel. Default removes the time, so the message won't
    get deleted anymore.
    :param ctx: Discord context
    :param eventname: The name of the event
    :param time: the time the message of the event should stay in the channel. Default None.
    """
    if not haspermissions([role.id for role in sendable.user.roles], sendable.guild.id) and not\
            sendable.user.guild_permissions.administrator:
        await sendable.send("insufficient permissions to use this command!")
        return
    eventname = eventname.lower()
    try:
        if time is not None:
            time = int(time)
    except ValueError:
        await sendable.send("please provide a valid time!")
        return
    if not await __eventnamecheck(sendable, eventname):
        return
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    cur.execute("UPDATE eventconfig SET alivetime=? WHERE guildid=? AND eventname=?",
                (time, sendable.guild.id, eventname))
    conn.commit()
    conn.close()
    if time is not None:
        await sendable.send(f"messages for the {eventname} event will be removed after {time} minutes. "
                       f"Note that the event must first be registered in the clan for it to have an effect.")
    else:
        await sendable.send(f"messages for the {eventname} event won't be removed after a certain time anymore.")


async def getclanregistrations(sendable: Sendable):
    with sqlite3.connect(databasepath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT clan FROM clanconfig WHERE guildid=?", (sendable.guild.id,))
        clans = list(set([row[0] for row in cur.fetchall()]))
    await sendable.send("The following clans have been registered for this server:\n" + "\n".join(clans))


async def showregistrations(sendable: Sendable, client: discord.Client):
    with sqlite3.connect(databasepath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT eventname, channel, pingrole, alivetime FROM eventconfig WHERE guildid=?",
                    (sendable.guild.id,))
        result = cur.fetchall()
    result = [list(row) for row in result]
    for row in result:
        if row[1] is not None:
            try:
                chan = await client.fetch_channel(row[1])
                chan = str(chan)
            except NotFound:
                chan = "not found"
            except Forbidden:
                chan = "no permissions"
            except Exception as e:
                print(e)
                chan = "unknown"
        else:
            chan = "not available"
        row[1] = chan

        if row[2] is not None:
            try:
                role = sendable.guild.get_role(int(row[2]))
            except Exception as e:
                print("fetching role failed.")
                print(e)
                role = "failed to fetch role"
        else:
            role = None
        if role is not None:
            row[2] = str(role)
        else:
            row[2] = "not available"
    messages = tablify(["eventname", "channel", "pingrole", "alivetime"], result)
    view = MISSING
    if len(messages) > 1:
        view = ResultmessageShower(messages, interaction=sendable)
    await sendable.send(messages[0], view=view)


async def unregisterclan(sendable: Sendable, clanname: str):
    """
    removes a clan from clanregistrations. So elite4/encounters/chests won't be announced in the server if a player
    with that clan triggers that event.
    :param ctx: discord context
    :param clanname: The clanname
    """
    if not haspermissions([role.id for role in sendable.user.roles], sendable.guild.id) and not\
            sendable.user.guild_permissions.administrator:
        await sendable.send("insufficient permissions to use this command!")
        return
    clanname = clanname.lower()
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    cur.execute("SELECT * FROM clanconfig WHERE guildid=? AND clan=?", (sendable.guild.id, clanname))
    allregistered = bool(cur.fetchall())
    if clanname == "all" and not allregistered:
        cur.execute("DELETE FROM clanconfig WHERE guildid=?", (sendable.guild.id,))
    else:
        cur.execute("DELETE FROM clanconfig WHERE guildid=? AND clan=?", (sendable.guild.id, clanname))
    conn.commit()
    conn.commit()
    cur.execute("SELECT clan FROM clanconfig WHERE guildid=?", (sendable.guild.id,))
    clans = [row[0] for row in cur.fetchall()]
    conn.close()
    await sendable.send(f"configuration for {clanname} removed!\n"
                                            "remaining clans: ```\n" + "\n".join(clans) + "```")


async def registerclan(sendable: Sendable, clanname: str):
    """
    registers a clan to the server, then if the event(s) are registered, chests, encounters and elite 4 (among
    others) will be sent to the server if the member who caused the event is part of the clan that is registered.
    :param ctx: discord context
    :param clanname: The name of the clan.
    """
    if not haspermissions([role.id for role in sendable.user.roles], sendable.guild.id) and not\
            sendable.user.guild_permissions.administrator:
        await sendable.response.send_message("insufficient permissions to use this command!")
        return
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO clanconfig(guildid, clan) VALUES(?, ?)", (sendable.guild.id, clanname.lower()))
        conn.commit()
        await sendable.send(f"{clanname} registered!")
    except sqlite3.OperationalError as e:
        print(e)
        await sendable.send("something went wrong." + str(e))
    except sqlite3.IntegrityError:
        await sendable.send("Unable to register that clanname! Is it already registered maybe?")
    finally:
        conn.close()


async def unregister(sendable: Sendable, eventname: str):
    """
    Sets the channel of the provided event to null, that way the provided event will not be sent anymore to that
    server.
    :param ctx: discord context
    :param eventname: the name of the event
    """
    if not haspermissions([role.id for role in sendable.user.roles], sendable.guild.id) and not \
            sendable.user.guild_permissions.administrator:
        await sendable.send("insufficient permissions to use this command!")
        return
    if eventname != "all":
        if not await __eventnamecheck(sendable, eventname):
            return
    eventname = eventname.lower()
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    if eventname == "all":
        result = cur.execute("UPDATE eventconfig SET channel=null WHERE guildid=?", (sendable.guild.id,))
    else:
        result = cur.execute(
            "UPDATE eventconfig SET channel=null WHERE guildid=? AND eventname=?", (sendable.guild.id, eventname))
    conn.commit()
    conn.close()
    if result.rowcount:
        await sendable.send(f"The {eventname} event will no longer be announced.")
    else:
        await sendable.send(f"The {eventname} was not configured already.")


async def setpingrole(sendable: Sendable, eventname: str, pingrole: discord.Role):
    """
    Adds a ping of the provided role to the event message.
    :param ctx: discord context
    :param eventname: The name of the event.
    :param pingrole: The role id or the role mention.
    """
    if not haspermissions([role.id for role in sendable.user.roles], sendable.guild.id) and not\
            sendable.user.guild_permissions.administrator:
        await sendable.send("insufficient permissions to use this command!")
        return
    eventname = eventname.lower()
    if not await __eventnamecheck(sendable, eventname):
        return
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    result = cur.execute("UPDATE eventconfig SET pingrole=? WHERE guildid=? AND eventname=?",
                         (pingrole.id, sendable.guild.id, eventname))
    if not result.rowcount:
        cur.execute("INSERT INTO eventconfig(guildid, eventname, channel, pingrole) VALUES(?, ?, null, ?)",
                    (sendable.guild.id, eventname, pingrole.id))
    conn.commit()
    conn.close()
    await sendable.send("pingrole set!")


async def removeping(sendable: Sendable, eventname: str):
    """
    Removes the ping of the provided event for the guild it was used in.
    :param ctx: discord context
    :param eventname: the name of the event.
    """
    if not haspermissions([role.id for role in sendable.user.roles], sendable.guild.id) and not\
            sendable.user.guild_permissions.administrator:
        await sendable.send("insufficient permissions to use this command!")
        return
    eventname = eventname.lower()
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    cur.execute("UPDATE eventconfig SET pingrole=null WHERE guildid=? AND eventname=?", (sendable.guild.id, eventname))
    conn.commit()
    conn.close()
    await sendable.send("pingrole removed if it was set!")




async def __add_member(sendable: Sendable, player: str):
    if not haspermissions([role.id for role in sendable.user.roles], sendable.guild.id) and not\
            sendable.user.guild_permissions.administrator:
        await sendable.send("insufficient permissions to use this command!")
        return
    membername = player.lower()
    with sqlite3.connect(databasepath) as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO memberconfig(guildid, playername) VALUES(?,?)", (sendable.guild.id, membername))
        except sqlite3.IntegrityError:
            await sendable.send("player has already been registered for this guild!")
            return
        conn.commit()
        await sendable.send(f"`{membername}` added to configuration for this server!")

async def __show_members(sendable: Sendable):
    with sqlite3.connect(databasepath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT playername FROM memberconfig WHERE guildid=?", (sendable.guild.id,))
        members = [row[0] for row in cur.fetchall()]

    msg = "```\n" + "\n".join(members) + "```"
    await sendable.send(msg)

async def __remove_member(sendable: Sendable):
    if not haspermissions([role.id for role in sendable.user.roles], sendable.guild.id) and not \
            sendable.user.guild_permissions.administrator:
        await sendable.send("insufficient permissions to use this command!")
        return
    with sqlite3.connect(databasepath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT playername FROM memberconfig WHERE guildid=?", (sendable.guild.id,))
        members = [row[0] for row in cur.fetchall()]
    if members:
        def removeMemberConfigMaker(memberlist):
            return RemoveMemberConfig(memberlist, databasepath, sendable)
        view = SelectsView(sendable, members, removeMemberConfigMaker)
        await sendable.send(content=f"page {view.currentpage} of {view.maxpage}", view=view)

    else:
        await sendable.send("no members registered for playerconfig.")


async def playerconfig(sendable: Sendable, player: str=None):
    """
    add players, remove players and show players that act as if a player is in a clan.
    :param ctx: discord context
    """
    playerconfig = PlayerConfig(__add_member, __remove_member, __show_members, sendable,
                                player=player)
    await sendable.send("what do you want to do?", view=playerconfig)
