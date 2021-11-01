import csv
import sqlite3
import datetime
from typing import Union, List
from pathmanager import PathManager


def tablify(layout: list, values: List[List]):
    """
    puts stuff in a table
    example input: layout=["name", "balance"], values=[["hank", "5000"], ["berend", "4000"]]
    :param layout: a list of the layout
    :param values: a list of lists with a simular length as the layout.
    :return: list of messages in table form
    """
    values = [list(i) for i in values]
    length = {}
    for i in range(len(layout)):
        length[i] = len(layout[i])

    for i in range(len(values)):
        for j in range(len(values[i])):
            if len(str(values[i][j])) > length[j]:
                length[j] = len(str(values[i][j]))

    resultmessages = []
    result = "```\n"
    for i in range(len(layout)):
        while len(layout[i]) < length[i]:
            layout[i] += " "
        result += layout[i] + "|"
    result += "\n"

    for row in values:
        newrow = ""
        for i in range(len(row)):
            while len(str(row[i])) < length[i]:
                row[i] = str(row[i]) + " "
            newrow += str(row[i]) + "|"
        if len(result + newrow + "\n```") < 2000:
            result += newrow + "\n"
        else:
            resultmessages.append(result + "```")
            result = "```\n"
            result += newrow + "\n"
    result += "```"
    if result.count("\n") < 3 and len(resultmessages) == 0:
        result = "Nothing found to be sent."
    resultmessages.append(result)
    return resultmessages


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

if __name__ == "__main__":
    isswarmlocation("gyarados")
