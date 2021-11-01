import re
from discord.ext import commands
import sqlite3
from commands.utils import haspermissions, tablify
from discord.utils import escape_mentions
from typing import Union
from discord.ext.commands.context import Context


class Eventconfigurations(commands.Cog):
    """
    This class contains commands for eventconfiguration for channels
    """
    def __init__(self, client: commands.bot.Bot):
        self.client = client
        self.databasepath = "./eventconfigurations.db"

    @commands.guild_only()
    @commands.command(name="setperms")
    async def setperms(self, ctx: Context, role: Union[int, str]):
        """
        This command gives permission to the specified role to adjust eventconfigurations for this server.
        Only useable by administrators of the server.
        :param ctx: discord context
        :param role: the role id or the role mention.
        """
        if not ctx.message.author.guild_permissions.administrator:
            await ctx.send("only administrators can use this command!")
        try:
            if match := re.search(pattern=r"(?<=<@&)([0-9]+)(?=>)", string=role):
                role = match.group()
            if ctx.guild.get_role(int(role)) is None:
                raise ValueError("is no role.")
        except ValueError:
            await ctx.send("please enter a valid role or role id!")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("INSERT INTO permissions(guildid, roleid) VALUES(?,?)", (ctx.guild.id, role))
        conn.commit()
        conn.close()
        await ctx.send("role successfully given permissions.")

    @commands.guild_only()
    @commands.command(name="removeperms")
    async def removeperms(self, ctx: Context, role: Union[int, str]):
        """
        Removes the permissions of a role to adjust eventconfigurations for this server.
        Only useable by administrators of the server.
        :param ctx: discord context
        :param role: the role id or the role mention.
        """
        try:
            if match := re.search(pattern=r"(?<=<@&)([0-9]+)(?=>)", string=role):
                role = match.group()
            if ctx.guild.get_role(int(role)) is None:
                raise ValueError("is no role.")
        except ValueError:
            await ctx.send("please enter a valid role or role id!")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        result = cur.execute("DELETE FROM permissions WHERE guildid=? AND roleid=?", (ctx.guild.id, role))
        conn.commit()
        conn.close()
        if result.rowcount:
            await ctx.send("Role successfully removed from permissions.")
        else:
            await ctx.send("that role had no permissions.")

    @commands.guild_only()
    @commands.command(name="getperms")
    async def getperms(self, ctx: Context):
        """
        Gets the roles that have permission to adjust eventconfigurations.
        :param ctx: discord context
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT roleid FROM permissions WHERE guildid=?", (ctx.guild.id,))
        result = cur.fetchall()
        message = ""
        for role in result:
            role = ctx.guild.get_role(int(role[0]))
            if role is not None:
                message += str(role) + "\n"
        message = escape_mentions(message)
        await ctx.send(message)

    @commands.guild_only()
    @commands.command(name="register")
    async def register(self, ctx: Context, eventname: str, channel: Union[str, None] = None):
        """
        Registers an event at the specified channel. If the channel is not specified the channel is the channel the
        command is used from.
        :param ctx: discord context
        :param eventname: The name of the event that should be announced in the provided channel. Default is ctx.channel
        (the channel where the command was used)
        :param channel: The channel to send the event to.
        """
        eventname = eventname.lower()
        if not haspermissions([role.id for role in ctx.message.author.roles], ctx.guild.id) and not\
                ctx.message.author.guild_permissions.administrator:
            await ctx.send("insufficient permissions to use this command!")
            return
        if not await self.__eventnamecheck(ctx, eventname):
            return
        if channel is None:
            channel = ctx.channel.id
            chan = ctx.channel
        elif match := re.search(r"(?<=<#)([0-9]+)(?=>)", channel):
            try:
                chan = await self.client.fetch_channel(int(match.group()))
                if chan.guild.id != ctx.guild.id:
                    raise Exception("user tries to register an event at another guild.")
                channel = int(match.group())
            except:
                await ctx.send("i have no access to that channel! are you sure that is a channel?")
                return
        else:
            await ctx.send("please provide a valid channel to register for that event.")
            return

        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()

        try:
            result = cur.execute("UPDATE eventconfig SET channel=? WHERE guildid=? AND eventname=?", (channel, ctx.guild.id, eventname))
            if not result.rowcount:  # no rows affected by previous statement.
                cur.execute("INSERT INTO eventconfig(guildid, eventname, channel) VALUES(?, ?, ?)", (ctx.guild.id, eventname, channel))
            conn.commit()
            await chan.send(
                f"This channel has been properly configured for sending the {eventname} event {ctx.author.mention}!")
        except sqlite3.IntegrityError:
            await ctx.send("event already registered in this channel!")
        finally:
            conn.close()

    @commands.guild_only()
    @commands.command(name="settime")
    async def settime(self, ctx: Context, eventname: str, time: int = None):
        """
        Sets the time in minutes the event should stay in the channel. Default removes the time, so the message won't
        get deleted anymore.
        :param ctx: Discord context
        :param eventname: The name of the event
        :param time: the time the message of the event should stay in the channel. Default None.
        """
        if not haspermissions([role.id for role in ctx.message.author.roles], ctx.guild.id) and not\
                ctx.message.author.guild_permissions.administrator:
            await ctx.send("insufficient permissions to use this command!")
            return
        try:
            if time is not None:
                time = int(time)
        except ValueError:
            await ctx.send("please provide a valid time!")
            return
        if not await self.__eventnamecheck(ctx, eventname):
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("UPDATE eventconfig SET alivetime=? WHERE guildid=? AND eventname=?", (time, ctx.guild.id, eventname))
        conn.commit()
        conn.close()
        if time is not None:
            await ctx.send(f"messages for the {eventname} event will be removed after {time} minutes. "
                           f"Note that the event must first be registered in the clan for it to have an effect.")
        else:
            await ctx.send(f"messages for the {eventname} event won't be removed after a certain time anymore.")

    @commands.guild_only()
    @commands.command(name="setpingrole")
    async def setpingrole(self, ctx: Context, eventname: str, pingrole: Union[str, int]):
        """
        Adds a ping of the provided role to the event message.
        :param ctx: discord context
        :param eventname: The name of the event.
        :param pingrole: The role id or the role mention.
        """
        if not haspermissions([role.id for role in ctx.message.author.roles], ctx.guild.id) and not\
                ctx.message.author.guild_permissions.administrator:
            await ctx.send("insufficient permissions to use this command!")
            return
        try:
            if match := re.search(pattern=r"(?<=<@&)([0-9]+)(?=>)", string=pingrole):
                pingrole = match.group()
            role = ctx.guild.get_role(int(pingrole))
            if role is None:
                raise ValueError("is no role.")
        except ValueError:
            await ctx.send("please enter a valid role or role id!")
            return
        if not await self.__eventnamecheck(ctx, eventname):
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        result = cur.execute("UPDATE eventconfig SET pingrole=? WHERE guildid=? AND eventname=?", (pingrole, ctx.guild.id, eventname))
        if not result.rowcount:
            cur.execute("INSERT INTO eventconfig(guildid, eventname, channel, pingrole) VALUES(?, ?, null, ?)", (ctx.guild.id, eventname, pingrole))
        conn.commit()
        conn.close()
        await ctx.send("pingrole set!")

    @commands.guild_only()
    @commands.command(name="removeping")
    async def removeping(self, ctx: Context, eventname: str):
        """
        Removes the ping of the provided event for the guild it was used in.
        :param ctx: discord context
        :param eventname: the name of the event.
        """
        if not haspermissions([role.id for role in ctx.message.author.roles], ctx.guild.id) and not\
                ctx.message.author.guild_permissions.administrator:
            await ctx.send("insufficient permissions to use this command!")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("UPDATE eventconfig SET pingrole=null WHERE guildid=? AND eventname=?", (ctx.guild.id, eventname))
        conn.commit()
        conn.close()
        await ctx.send("pingrole removed if it was set!")

    @commands.guild_only()
    @commands.command(name="unregister")
    async def unregister(self, ctx: Context, eventname: str):
        """
        Sets the channel of the provided event to null, that way the provided event will not be sent anymore to that
        server.
        :param ctx: discord context
        :param eventname: the name of the event
        """
        if not haspermissions([role.id for role in ctx.message.author.roles], ctx.guild.id) and not\
                ctx.message.author.guild_permissions.administrator:
            await ctx.send("insufficient permissions to use this command!")
            return
        if not await self.__eventnamecheck(ctx, eventname):
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        result = cur.execute("UPDATE eventconfig SET channel=null WHERE guildid=? AND eventname=?", (ctx.guild.id, eventname))
        conn.commit()
        conn.close()
        if result.rowcount:
            await ctx.send(f"The {eventname} event will no longer be announced.")
        else:
            await ctx.send(f"The {eventname} was not configured already.")

    @commands.guild_only()
    @commands.command(name="registerclan")
    async def registerclan(self, ctx: Context, clanname: str):
        """
        registers a clan to the server, then if the event(s) are registered, chests, encounters and elite 4 (among
        others) will be sent to the server if the member who caused the event is part of the clan that is registered.
        :param ctx: discord context
        :param clanname: The name of the clan.
        """
        if not haspermissions([role.id for role in ctx.message.author.roles], ctx.guild.id) and not\
                ctx.message.author.guild_permissions.administrator:
            await ctx.send("insufficient permissions to use this command!")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO clanconfig(guildid, clan) VALUES(?, ?)", (ctx.guild.id, clanname.lower()))
            conn.commit()
            await ctx.send(f"{clanname} registered!")
        except sqlite3.OperationalError as e:
            print(e)
            await ctx.send("something went wrong." + str(e))
        except sqlite3.IntegrityError:
            await ctx.send("Unable to register that clanname! Is it already registered maybe?")
        finally:
            conn.close()

    @commands.guild_only()
    @commands.command(name="getclanregistrations", aliases=["showclanregistrations"])
    async def getclanregistrations(self, ctx: Context):
        """
        shows the clans that are registered in the server where the command is used.
        :param ctx: discord context
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT clan FROM clanconfig WHERE guildid=?", (ctx.guild.id,))
        clans = list(set([row[0] for row in cur.fetchall()]))
        conn.close()
        await ctx.send("The following clans have been registered for this server: \n" + ", ".join(clans))

    @commands.guild_only()
    @commands.command(name="unregisterclan")
    async def unregisterclan(self, ctx: Context, clanname: str):
        """
        removes a clan from clanregistrations. So elite4/encounters/chests won't be announced in the server if a player
        with that clan triggers that event.
        :param ctx: discord context
        :param clanname: The clanname
        """
        if not haspermissions([role.id for role in ctx.message.author.roles], ctx.guild.id) and not\
                ctx.message.author.guild_permissions.administrator:
            await ctx.send("insufficient permissions to use this command!")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("DELETE FROM clanconfig WHERE guildid=? AND clan=?", (ctx.guild.id, clanname.lower()))
        await ctx.send(f"configuration for {clanname} removed!")
        conn.commit()
        cur.execute("SELECT clan FROM clanconfig WHERE guildid=?", (ctx.guild.id,))
        clans = [row[0] for row in cur.fetchall()]
        conn.close()
        await ctx.send("remaining clans: ```\n" + "\n".join(clans) + "```")

    @commands.guild_only()
    @commands.command(name="showregistrations")
    async def showregistrations(self, ctx: Context):
        """
        Shows a collection of events, together with the role that gets pinged, the time it remains in the channel,
        and the channel it gets sent to.
        :param ctx: discord context
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT eventname, channel, pingrole, alivetime FROM eventconfig WHERE guildid=?", (ctx.guild.id,))
        result = cur.fetchall()
        result = [list(row) for row in result]
        for row in result:
            if row[1] is not None:
                try:
                    chan = await self.client.fetch_channel(row[1])
                    chan = str(chan)
                except:
                    chan = "not available"
            else:
                chan = "not available"
            row[1] = chan

            if row[2] is not None:
                try:
                    role = ctx.guild.get_role(int(row[2]))
                except:
                    role = "failed to fetch role"
            else:
                role = None
            if role is not None:
                row[2] = str(role)
            else:
                row[2] = "not available"
        messages = tablify(["eventname", "channel", "pingrole", "alivetime"], result)
        for message in messages:
            await ctx.send(message)

    async def __eventnamecheck(self, ctx: Context, eventname: str):
        """
        Checks if the provided eventname is a existing event, and shows what events are possible if the eventname is
        invalid.
        :param ctx: discord context
        :param eventname: the eventname.
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT eventname FROM eventnames WHERE eventname=?", (eventname,))
        result = cur.fetchall()
        if len(result) == 0:
            cur.execute("SELECT eventname FROM eventnames")
            eventnames = [row[0] for row in cur.fetchall()]
            conn.close()
            await ctx.send(f"invalid eventname '{eventname}'! Possible events:\n" + ", ".join(eventnames))
            return False
        conn.close()
        return True


def setup(client):
    client.add_cog(Eventconfigurations(client))
