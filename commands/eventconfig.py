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
from commands.utils.utils import haspermissions, tablify
from discord.utils import escape_mentions, MISSING
from typing import Union


class Eventconfigurations(commands.Cog):
    """
    This class contains commands for eventconfiguration for channels
    """
    def __init__(self, client: commands.bot.Bot):
        self.client = client
        self.databasepath = "./eventconfigurations.db"

    eventconfiggroup = app_commands.Group(name="eventconfig",
                                          description="configurate ingame events to be sent in certain channels")

    @eventconfiggroup.command(name="setperms")
    async def setperms(self, interaction: Interaction, role: discord.Role):
        """
        This command gives permission to the specified role to adjust eventconfigurations for this server.
        Only useable by administrators of the server.
        :param ctx: discord context
        :param role: the role id or the role mention. Union[int, str]
        """
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("only administrators can use this command!")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("INSERT INTO permissions(guildid, roleid) VALUES(?,?)", (interaction.guild.id, role.id))
        conn.commit()
        conn.close()
        await interaction.response.send_message("role successfully given permissions.")

    @eventconfiggroup.command(name="removeperms")
    async def removeperms(self, interaction: Interaction, role: discord.Role):
        """
        Removes the permissions of a role to adjust eventconfigurations for this server.
        Only useable by administrators of the server.
        :param ctx: discord context
        :param role: the role id or the role mention. Union[int, str]
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        result = cur.execute("DELETE FROM permissions WHERE guildid=? AND roleid=?", (interaction.guild.id, role.id))
        conn.commit()
        conn.close()
        if result.rowcount:
            await interaction.response.send_message("Role successfully removed from permissions.")
        else:
            await interaction.response.send_message("that role had no permissions.")

    @eventconfiggroup.command(name="getperms")
    async def getperms(self, interaction: Interaction):
        """
        Gets the roles that have permission to adjust eventconfigurations.
        :param ctx: discord context
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT roleid FROM permissions WHERE guildid=?", (interaction.guild.id,))
        result = cur.fetchall()
        message = ""
        for role in result:
            role = interaction.guild.get_role(int(role[0]))
            if role is not None:
                message += str(role) + "\n"
        message = escape_mentions(message)
        if message != "":
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message("no permissions set.")

    @eventconfiggroup.command(name="register")
    async def register(self, interaction: Interaction, channel: discord.TextChannel = None):
        """
        Registers an event at the specified channel. If the channel is not specified the channel is the channel the
        command is used from.
        :param ctx: discord context
        :param channel: The channel to send the event to. Default channel where command was used.
        """
        if not haspermissions([role.id for role in interaction.user.roles], interaction.guild.id) and not\
                interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("insufficient permissions to use this command!")
            return
        chan = channel if channel is not None else interaction.channel
        with sqlite3.connect(self.databasepath) as conn:
            cur = conn.cursor()
            cur.execute("SELECT eventname FROM eventnames")
            eventnames = [row[0] for row in cur.fetchall()]
        eventnames.sort()
        view = SelectsView(interaction, eventnames, lambda options: Register(interaction, options, chan,
                                                                             self.databasepath))
        await interaction.response.send_message(f"Select events you want a message for in {chan.mention}", view=view)

    @eventconfiggroup.command(name="settime")
    async def settime(self, interaction: Interaction, eventname: str, time: int = None):
        """
        Sets the time in minutes the event should stay in the channel. Default removes the time, so the message won't
        get deleted anymore.
        :param ctx: Discord context
        :param eventname: The name of the event
        :param time: the time the message of the event should stay in the channel. Default None.
        """
        if not haspermissions([role.id for role in interaction.user.roles], interaction.guild.id) and not\
                interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("insufficient permissions to use this command!")
            return
        eventname = eventname.lower()
        try:
            if time is not None:
                time = int(time)
        except ValueError:
            await interaction.response.send_message("please provide a valid time!")
            return
        if not await self.__eventnamecheck(interaction, eventname):
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("UPDATE eventconfig SET alivetime=? WHERE guildid=? AND eventname=?",
                    (time, interaction.guild.id, eventname))
        conn.commit()
        conn.close()
        if time is not None:
            await interaction.response.send_message(f"messages for the {eventname} event will be removed after {time} minutes. "
                           f"Note that the event must first be registered in the clan for it to have an effect.")
        else:
            await interaction.response.send_message(f"messages for the {eventname} event won't be removed after a certain time anymore.")

    @eventconfiggroup.command(name="setpingrole")
    async def setpingrole(self, interaction: Interaction, eventname: str, pingrole: discord.Role):
        """
        Adds a ping of the provided role to the event message.
        :param ctx: discord context
        :param eventname: The name of the event.
        :param pingrole: The role id or the role mention.
        """
        if not haspermissions([role.id for role in interaction.user.roles], interaction.guild.id) and not\
                interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("insufficient permissions to use this command!")
            return
        eventname = eventname.lower()
        if not await self.__eventnamecheck(interaction, eventname):
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        result = cur.execute("UPDATE eventconfig SET pingrole=? WHERE guildid=? AND eventname=?",
                             (pingrole.id, interaction.guild.id, eventname))
        if not result.rowcount:
            cur.execute("INSERT INTO eventconfig(guildid, eventname, channel, pingrole) VALUES(?, ?, null, ?)",
                        (interaction.guild.id, eventname, pingrole.id))
        conn.commit()
        conn.close()
        await interaction.response.send_message("pingrole set!")

    @eventconfiggroup.command(name="removeping")
    async def removeping(self, interaction: Interaction, eventname: str):
        """
        Removes the ping of the provided event for the guild it was used in.
        :param ctx: discord context
        :param eventname: the name of the event.
        """
        if not haspermissions([role.id for role in interaction.user.roles], interaction.guild.id) and not\
                interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("insufficient permissions to use this command!")
            return
        eventname = eventname.lower()
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("UPDATE eventconfig SET pingrole=null WHERE guildid=? AND eventname=?", (interaction.guild.id, eventname))
        conn.commit()
        conn.close()
        await interaction.response.send_message("pingrole removed if it was set!")

    @eventconfiggroup.command(name="unregister")
    async def unregister(self, interaction: Interaction, eventname: str):
        """
        Sets the channel of the provided event to null, that way the provided event will not be sent anymore to that
        server.
        :param ctx: discord context
        :param eventname: the name of the event
        """
        if not haspermissions([role.id for role in interaction.user.roles], interaction.guild.id) and not\
                interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("insufficient permissions to use this command!")
            return
        if eventname != "all":
            if not await self.__eventnamecheck(interaction, eventname):
                return
        eventname = eventname.lower()
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        if eventname == "all":
            result = cur.execute("UPDATE eventconfig SET channel=null WHERE guildid=?", (interaction.guild.id,))
        else:
            result = cur.execute(
                "UPDATE eventconfig SET channel=null WHERE guildid=? AND eventname=?", (interaction.guild.id, eventname))
        conn.commit()
        conn.close()
        if result.rowcount:
            await interaction.response.send_message(f"The {eventname} event will no longer be announced.")
        else:
            await interaction.response.send_message(f"The {eventname} was not configured already.")

    @eventconfiggroup.command(name="registerclan")
    async def registerclan(self, interaction: Interaction, clanname: str):
        """
        registers a clan to the server, then if the event(s) are registered, chests, encounters and elite 4 (among
        others) will be sent to the server if the member who caused the event is part of the clan that is registered.
        :param ctx: discord context
        :param clanname: The name of the clan.
        """
        if not haspermissions([role.id for role in interaction.user.roles], interaction.guild.id) and not\
                interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("insufficient permissions to use this command!")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO clanconfig(guildid, clan) VALUES(?, ?)", (interaction.guild.id, clanname.lower()))
            conn.commit()
            await interaction.response.send_message(f"{clanname} registered!")
        except sqlite3.OperationalError as e:
            print(e)
            await interaction.response.send_message("something went wrong." + str(e))
        except sqlite3.IntegrityError:
            await interaction.response.send_message("Unable to register that clanname! Is it already registered maybe?")
        finally:
            conn.close()

    @eventconfiggroup.command(name="getclanregistrations")
    async def getclanregistrations(self, interaction: Interaction):
        """
        shows the clans that are registered in the server where the command is used.
        :param ctx: discord context
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT clan FROM clanconfig WHERE guildid=?", (interaction.guild.id,))
        clans = list(set([row[0] for row in cur.fetchall()]))
        conn.close()
        await interaction.response.send_message("The following clans have been registered for this server: \n" +
                                                ", ".join(clans))

    async def __remove_member(self, interaction: Interaction):
        if not haspermissions([role.id for role in interaction.user.roles], interaction.guild.id) and not \
                interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("insufficient permissions to use this command!")
            return
        with sqlite3.connect(self.databasepath) as conn:
            cur = conn.cursor()
            cur.execute("SELECT playername FROM memberconfig WHERE guildid=?", (interaction.guild.id,))
            members = [row[0] for row in cur.fetchall()]
        if members:
            def removeMemberConfigMaker(memberlist):
                return RemoveMemberConfig(memberlist, self.databasepath, interaction)
            view = SelectsView(interaction, members, removeMemberConfigMaker)
            await interaction.response.send_message(content=f"page {view.currentpage} of {view.maxpage}", view=view)

        else:
            await interaction.response.send_message("no members registered for playerconfig.")

    @eventconfiggroup.command(name="unregisterclan")
    async def unregisterclan(self, interaction: Interaction, clanname: str):
        """
        removes a clan from clanregistrations. So elite4/encounters/chests won't be announced in the server if a player
        with that clan triggers that event.
        :param ctx: discord context
        :param clanname: The clanname
        """
        if not haspermissions([role.id for role in interaction.user.roles], interaction.guild.id) and not\
                interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("insufficient permissions to use this command!")
            return
        clanname = clanname.lower()
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT * FROM clanconfig WHERE guildid=? AND clan=?", (interaction.guild.id, clanname))
        allregistered = bool(cur.fetchall())
        if clanname == "all" and not allregistered:
            cur.execute("DELETE FROM clanconfig WHERE guildid=?", (interaction.guild.id,))
        else:
            cur.execute("DELETE FROM clanconfig WHERE guildid=? AND clan=?", (interaction.guild.id, clanname))
        conn.commit()
        conn.commit()
        cur.execute("SELECT clan FROM clanconfig WHERE guildid=?", (interaction.guild.id,))
        clans = [row[0] for row in cur.fetchall()]
        conn.close()
        await interaction.response.send_message(f"configuration for {clanname} removed!\n"
                                                "remaining clans: ```\n" + "\n".join(clans) + "```")

    @eventconfiggroup.command(name="showregistrations")
    async def showregistrations(self, interaction: Interaction):
        """
        Shows a collection of events, together with the role that gets pinged, the time it remains in the channel,
        and the channel it gets sent to.
        :param ctx: discord context
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT eventname, channel, pingrole, alivetime FROM eventconfig WHERE guildid=?", (interaction.guild.id,))
        result = cur.fetchall()
        result = [list(row) for row in result]
        for row in result:
            if row[1] is not None:
                try:
                    chan = await self.client.fetch_channel(row[1])
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
                    role = interaction.guild.get_role(int(row[2]))
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
            view = ResultmessageShower(messages, interaction=interaction)
        await interaction.response.send_message(messages[0], view=view)

    # config for adding individual playernames, this way clanevents act as if the player is in a clan the discord server
    # is registered for.
    @eventconfiggroup.command(name="playerconfig")
    async def playerconfig(self, interaction: Interaction, player: str=None):
        """
        add players, remove players and show players that act as if a player is in a clan.
        :param ctx: discord context
        """
        playerconfig = PlayerConfig(self.__add_member, self.__remove_member, self.__show_members, interaction,
                                    player=player)
        await interaction.response.send_message("what do you want to do?", view=playerconfig)

    async def __add_member(self, interaction: Interaction, player: str):
        if not haspermissions([role.id for role in interaction.user.roles], interaction.guild.id) and not\
                interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("insufficient permissions to use this command!")
            return
        membername = player.lower()
        with sqlite3.connect(self.databasepath) as conn:
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO memberconfig(guildid, playername) VALUES(?,?)", (interaction.guild.id, membername))
            except sqlite3.IntegrityError:
                await interaction.response.send_message("player has already been registered for this guild!")
                return
            conn.commit()
            await interaction.response.send_message(f"`{membername}` added to configuration for this server!")

    async def __show_members(self, interaction: Interaction):
        with sqlite3.connect(self.databasepath) as conn:
            cur = conn.cursor()
            cur.execute("SELECT playername FROM memberconfig WHERE guildid=?", (interaction.guild.id,))
            members = [row[0] for row in cur.fetchall()]

        msg = "```\n" + "\n".join(members) + "```"
        await interaction.response.send_message(msg)

    async def __eventnamecheck(self, interaction: Interaction, eventname: str) -> bool:
        """
        Checks if the provided eventname is a existing event, and shows what events are possible if the eventname is
        invalid.
        :param ctx: discord context
        :param eventname: the eventname.
        :return boolean, True if the eventname is valid.
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT eventname FROM eventnames WHERE eventname=?", (eventname,))
        result = cur.fetchall()
        if len(result) == 0:
            cur.execute("SELECT eventname FROM eventnames")
            eventnames = [row[0] for row in cur.fetchall()]
            conn.close()
            await interaction.response.send_message(f"invalid eventname '{eventname}'! Possible events:\n" + ", ".join(eventnames))
            return False
        conn.close()
        return True


async def setup(client):
    await client.add_cog(Eventconfigurations(client))
