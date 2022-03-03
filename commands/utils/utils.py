import asyncio
import csv
import sqlite3
import datetime
from typing import Union, List

import discord
from PIL import Image
from discord.ext.commands import Context
from numpy import isnan

from pathmanager import PathManager


def replacenan(list, replacement):
    for i in range(len(list)):
        if type(list[i]) == float and isnan(list[i]):
            list[i] = replacement
    return list


def tablify(layout, values, maxlength=2000):
    lengths = {}
    valuespluslayout = [layout] + values
    for i in range(len(layout)):
        lengths[i] = len(str(max(valuespluslayout, key=lambda x: len(str(x[i])))[i]))
    toptext = "|"
    for index, i in enumerate(layout):
        toptext += str(i) + " " * (lengths[index] - len(str(i))) + "|"
    toptext += "\n"
    messages = []
    message = "```\n" + toptext
    for row in values:
        rowtext = "|"
        for columnindex, column in enumerate(row):
            newtxt = str(column) + " " * (lengths[columnindex] - len(str(column)))
            rowtext += newtxt + "|"
        if len(message + rowtext + "```") < maxlength:
            message += rowtext + "\n"
        else:
            message += "```"
            messages.append(message)
            message = "```\n" + toptext + rowtext + "\n"
    message += "```"
    if message.count("\n") == 2 and len(messages) == 0:
        message = "No results found."
    messages.append(message)
    return messages


def getswarmpokemons() -> List[str]:
    """
    checks if the provided pokemon is a pokemon that can be in a swarm.
    :return: boolean if the pokemon is in the list of pokemon that can be in swarms.
    """
    swarmpokemonlist = open("commands/data/swarmpokemon.csv").read().split(",")
    swarmpokemonlist = [pokemon.lower() for pokemon in swarmpokemonlist]
    swarmpokemonlist = list(set(swarmpokemonlist))
    swarmpokemonlist.sort()
    return swarmpokemonlist


def getswarmlocations() -> List[str]:
    """
    checks if the provided location is a location where a swarm can happen.
    :param location: the provided location
    :return: boolean if location is in the list of locations where swarms can happen,
    """
    swarmlocationlist = open("commands/data/swarmlocations.csv").read().split(",")
    swarmlocationlist = [location.lower() for location in swarmlocationlist]
    swarmlocationlist = list(set(swarmlocationlist))  # remove duplicates just in case
    swarmlocationlist.sort()
    return swarmlocationlist


def isgoldrushlocation(location: str) -> bool:
    """
    checks if the provided location is a location where a goldrush can happen.
    :param location: the provided location
    :return: boolean if location is in the list of locations where a goldrush can happen.
    """
    goldrushlocationlist = open("commands/data/goldrushlocations.csv").read().split(",")
    return location in goldrushlocationlist


def getgoldrushlocations() -> list:
    """
    gets a list of locations where goldrushes can happen.
    :return:
    """
    return open("commands/data/goldrushlocations.csv").read().split(",")


def ishoneylocation(location: str) -> bool:
    """
    Checks if the provided location is a honeylocation.
    :param location:
    :return:
    """
    with sqlite3.connect("data.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM honeylocations WHERE location=?", (location,))
        return bool(cur.fetchall())


def gethoneylocations() -> list:
    with sqlite3.connect("data.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM honeylocations")
        return [row[0] for row in cur.fetchall()]


def istournamentprize(prize: str) -> list:
    with sqlite3.connect("data.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT prize FROM tournamentprizes WHERE prize=?", (prize,))
        return bool(cur.fetchall())


def haspermissions(roles: list, guild: int) -> bool:
    """
    checks if a role has permissions to adjust eventconfigurations for the provided guild.
    :param roles: a list of roles the user has.
    :param guild: the guildid of the guild.
    :return: boolean, true if user has permissions.
    """
    conn = sqlite3.connect("eventconfigurations.db")
    cur = conn.cursor()
    cur.execute("SELECT roleid FROM permissions WHERE guildid=?", (guild,))
    permissionslist = [row[0] for row in cur.fetchall()]
    conn.close()
    for role in roles:
        if role in permissionslist:
            return True
    return False


def getworldbosstime(path="worldbosstime.txt") -> datetime.datetime:
    """
    returns the datetime object of when the worldboss is.
    :param path: the path to worldbosstime.txt
    :return: datetime of when the worldboss is.
    """
    with open(path) as file:
        worldboss_time = int(file.readlines()[1])
    return datetime.datetime.fromtimestamp(worldboss_time)


def getworldbosstime(path="worldbosstime.txt") -> datetime.datetime:
    """
    returns the datetime object of when the worldboss is.
    :param path: the path to worldbosstime.txt
    :return: datetime of when the worldboss is.
    """
    with open(path) as file:
        worldboss_time = int(file.readlines()[1])
    return datetime.datetime.fromtimestamp(worldboss_time)

def worldbosssent(path: str="worldbosstime.txt") -> bool:
    """
    returns if the message 30 mins before worldboss already has been sent.
    :param path: the path to worldbosstime.txt
    :return: boolean, true if it has been sent.
    """
    with open(path) as file:
        sent = int(file.readlines()[0])
    return bool(sent)


def datehandler(datestring: str) -> str:
    """
    handle dates.
    Example input: 2021-1-8
    Example output:2021-01-08
    :param datestring: the date you want formatted.
    :return the date as a string of fixed length. will always be format yyyy-mm-dd
    """
    datelist = datestring.split("-")
    if len(datelist[1]) < 2:
        datelist[1] = "0" + str(datelist[1])
    if len(datelist[2]) < 2:
        datelist[2] = "0" + str(datelist[2])
    return "-".join(datelist)


def joinmessages(messages, maxlength=2000):
    allmessages = []
    newmsg = ""
    for message in messages:
        if len(newmsg + message) < maxlength:
            newmsg += message
        else:
            allmessages.append(newmsg)
            newmsg = ""
    if newmsg != "":
        allmessages.append(newmsg)
    return allmessages
