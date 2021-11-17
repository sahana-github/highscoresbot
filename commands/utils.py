import csv
import sqlite3
import datetime
from typing import Union, List

from numpy import isnan

from pathmanager import PathManager


def replacenan(list, replacement):
    for i in range(len(list)):
        if type(list[i]) == float and isnan(list[i]):
            list[i] = replacement
    return list


def tablify(layout, values):
    lengths = {}
    values = [layout] + values
    for i in range(len(layout)):
        lengths[i] = len(str(max(values, key=lambda x: len(str(x[i])))[i]))
    messages = []
    message = "```\n"
    for row in values:
        rowtext = "|"
        for columnindex, column in enumerate(row):
            newtxt = str(column) + " " * (lengths[columnindex] - len(str(column)))
            rowtext += newtxt + "|"
        if len(message + rowtext + "```") < 2000:
            message += rowtext + "\n"
        else:
            message += "```"
            messages.append(message)
            message = "```\n" + rowtext + "\n"
    message += "```"
    if message.count("\n") == 2 and len(messages) == 0:
        message = "No results found."
    messages.append(message)
    return messages


def isswarmpokemon(pokemon: str) -> bool:
    """
    checks if the provided pokemon is a pokemon that can be in a swarm.
    :param pokemon: the provided pokemon.
    :return: boolean if the pokemon is in the list of pokemon that can be in swarms.
    """
    swarmpokemonlist = open("commands/data/swarmpokemon.csv").read().split(",")
    return pokemon in swarmpokemonlist


def isswarmlocation(location: str) -> bool:
    """
    checks if the provided location is a location where a swarm can happen.
    :param location: the provided location
    :return: boolean if location is in the list of locations where swarms can happen,
    """
    swarmlocationlist = open("commands/data/swarmlocations.csv").read().split(",")
    return location in swarmlocationlist


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


def worldbosssent(path: str="worldbosstime.txt") -> bool:
    """
    returns if the message 30 mins before worldboss already has been sent.
    :param path: the path to worldbosstime.txt
    :return: boolean, true if it has been sent.
    """
    with open(path) as file:
        sent = int(file.readlines()[0])
    return bool(sent)


def getClan(playername: str) -> Union[str, None]:
    """
    gets the clan of a player.
    :param playername: the player you want the clanname of.
    :return: either the clan of the player or None
    """
    pathmanager = PathManager()
    highscoresconn = sqlite3.connect(pathmanager.getpath("highscores.db"))
    highscorescur = highscoresconn.cursor()
    highscorescur.execute(open(pathmanager.getpath("clanquery.txt")).read() + "?", (playername,))
    try:
        clan = [row[0] for row in highscorescur.fetchall()][0]
        if clan == "":
            return
    except IndexError:
        return
    finally:
        highscoresconn.close()
    return clan


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


if __name__ == "__main__":

    tablify(['Rank', 'Username', 'Clan', 'Experience Gained'],
            [[6, 'benmin', 'nightraiders', '98,190,538'], [8, 'parkero983', 'nightraiders', '89,307,878'], [10, 'fornix', 'nightraiders', '70,838,769'], [11, 'bambamy', 'nightraiders', '69,041,279'], [14, 'dittokarma', 'nightraiders', '65,512,980'], [15, 'forgottenpassword', 'nightraiders', '65,308,742'], [18, 'kataraqueen', 'nightraiders', '58,932,300'], [42, 'hyp3rbolo', 'nightraiders', '42,494,644'], [45, 'ssswiipo', 'nightraiders', '41,877,547'], [59, 'gcoupe2011', 'nightraiders', '32,802,679'], [62, 'bchef', 'nightraiders', '32,173,011'], [67, 'youngblood', 'nightraiders', '31,680,794'], [68, 'ilickedyoursaltlamp', 'nightraiders', '31,204,928'], [82, 'knackeredfarmer', 'nightraiders', '27,081,724'], [83, 'vleeks', 'nightraiders', '26,985,321'], [88, 'o', 'nightraiders', '25,815,959'], [99, 'xxxtenicals', 'nightraiders', '24,549,762'], [118, 'julianozz7', 'nightraiders', '21,969,772'], [127, 'oskay1911', 'nightraiders', '20,967,576'], [128, 'hippohello', 'nightraiders', '20,891,241'], [143, 'tawniere', 'nightraiders', '19,206,001'], [193, 'bigbootyhunter', 'nightraiders', '16,110,168'], [207, 'omegadance', 'nightraiders', '14,829,212'], [229, 'hellblazer', 'nightraiders', '13,656,733'], [231, 'demonicdrake', 'nightraiders', '13,520,272'], [235, 'mathln110', 'nightraiders', '13,294,365'], [301, 'doritho', 'nightraiders', '10,404,674'], [350, 'frankenstein2018', 'nightraiders', '9,047,235'], [421, 'murlander', 'nightraiders', '7,314,597'], [479, 'marshing', 'nightraiders', '6,033,791'], [707, 'andreasthekingdk', 'nightraiders', '3,087,258']])
