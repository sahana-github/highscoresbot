import datetime
import sqlite3

import discord

from commands.interractions.ingame_events.getchests import GetChests
from commands.interractions.ingame_events.getencounters import GetEncounters
from commands.interractions.ingame_events.getrolls import GetRolls
from commands.interractions.resultmessageshower import ResultmessageShower
from commands.sendable import Sendable
from commands.utils.utils import tablify, getworldbosstime
from highscores import getClanList
from pathmanager import PathManager


async def lastonline(sendable: Sendable, playername: str):
    if playername is None:
        with sqlite3.connect(PathManager().getpath("ingame_data.db")) as conn:
            cur = conn.cursor()
            cur.execute("SELECT max(timestamp) FROM activity")
            online = datetime.datetime.fromtimestamp(cur.fetchall()[0][0], datetime.timezone.utc)
            await sendable.send(
                f"last online check was at {online}. Give a playername with the command to see what"
                f"date the player was last online.")
        return
    playername = playername.lower()
    with sqlite3.connect(PathManager().getpath("ingame_data.db")) as conn:
        cur = conn.cursor()
        cur.execute("SELECT timestamp FROM activity WHERE playername=?", (playername,))
        try:
            timestamp = cur.fetchall()[0][0]
        except IndexError:
            await sendable.send(f"no information about last online of {playername}")
            return
        online = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
        await sendable.send(f"{playername} was last online at {str(online).split(' ')[0]}")


async def getencounters(sendable: Sendable, name: str):
    """
    gets the encounters
    :param ctx: message context
    :param name: either playername, pokemonname or a date
    """
    name = name.lower()
    await sendable.send(content="is that a pokemon, date, or player? Press the button to get a response!",
                         view=GetEncounters(sendable, name))


async def getchests(sendable: Sendable, argument: str):
    name = argument.lower()
    await sendable.send("is that a location, date, or player? Press the button to get a response! ",
                                            view=GetChests(sendable, name))


async def getrolls(sendable: Sendable, parameter: str):
    """
    Gets the rolls of a player, the rolls of a pokemon, or the rolls on a specific date.
    Timeout is 10 minutes, then the message gets deleted.
    :param ctx: discord context
    :param parameter: The pokemon, date or player
    """
    parameter = parameter.lower()
    await sendable.send(content="is that a pokemon, date, or player? Press the button to get a response! ",
                   view=GetRolls(sendable, parameter))


async def getclanencounters(sendable: Sendable, clanname: str):
    clanname = clanname.lower()
    conn = sqlite3.connect(PathManager().getpath(r"ingame_data.db"))
    cur = conn.cursor()

    clanlist = getClanList(clanname.lower())
    totalencounters = []
    for player in clanlist:
        cur.execute("SELECT Name, Encounters, Date FROM Encounters WHERE Name = ?", (player,))
        [totalencounters.append(row) for row in cur.fetchall()]
    totalencounters.sort(key=lambda x: x[2])
    resultmessages = tablify(["name", "pokemon", "date"], totalencounters, maxlength=1200)
    resultmessageshower = ResultmessageShower(resultmessages[::-1], sendable)
    await sendable.send(
        content=f"page {resultmessageshower.currentpage} of {resultmessageshower.maxpage}\n" +
                resultmessages[-1],
        view=resultmessageshower)


async def worldbosstime(sendable: Sendable):
    """
    gives the time untill the start of the worldboss.
    :param ctx: discord context
    """
    try:
        worldboss_datetime = getworldbosstime()
        timedifference = worldboss_datetime - datetime.datetime.now()
        embed = discord.Embed(title="worldboss",
                              description=f"The worldboss will start at <t:{str(int(worldboss_datetime.timestamp()))}>")
        embed.add_field(name="relative",
                        value=f"that is in {(timedifference.days * 86400 + timedifference.seconds) // 3600} hours "
                              f"and {(timedifference.seconds // 60) % 60} minutes\n")
        await sendable.send(embed=embed)
    except IndexError:
        await sendable.send("something went wrong!")
    except Exception as e:
        await sendable.send("uncaught exception.")
        raise e
