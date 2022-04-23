import sqlite3

from discord import Interaction

from commands.interractions.pmconfig.pmgoldrush import PmGoldrush
from commands.interractions.pmconfig.pmhoney import PmHoney
from commands.interractions.pmconfig.removepmconfig import RemovePmConfig
from commands.interractions.selectsview import SelectsView
from commands.sendable import Sendable
from commands.utils.utils import getgoldrushlocations, gethoneylocations, getswarmpokemons, getswarmlocations

databasepath = "./eventconfigurations.db"


async def pmgoldrush(sendable: Sendable):
    """
    The user will receive a pm if a goldrush happens at the provided location.
    It is checked if it is a valid location.
    :param ctx: discord context
    """
    view = SelectsView(sendable, options=getgoldrushlocations(),
                       selectoption=lambda locations: PmGoldrush(sendable, locations, databasepath))
    await sendable.send("for what locations do you want a pm when a goldrush pops up?", view=view)


async def pmhoney(sendable: Sendable):
    """
    The user will receive a pm if honey gets spread at the provided location.
    """
    view = SelectsView(sendable, options=gethoneylocations(),
                       selectoption=lambda locations: PmHoney(sendable, locations, databasepath))
    await sendable.send("for what locations do you want a pm when a honey gets spread?",
                                            view=view)

async def pmswarm(sendable: Sendable, pokemon: str, location: str):
    if pokemon is None and location is None:
        await sendable.send("select pokemon, location or both")
        return
    symbol = "|"
    if pokemon is not None and location is not None:
        symbol = "&"
    if pokemon is not None:
        pokemon = pokemon.lower()
        if pokemon not in getswarmpokemons():
            await sendable.send("not an available swarm pokemon. See "
                                                    "https://pokemon-planet.com/swarms for a list of available pokemon")
            return
    if location is not None:
        location = location.lower()
        if location not in getswarmlocations():
            await sendable.send("not an available swarm location. See "
                                                    "https://pokemon-planet.com/swarms for a list of available locations")
        # both not None, so we can start entering it in the database.
    query = "INSERT INTO pmswarm(playerid, location, pokemon, comparator) VALUES(?, ?, ?, ?)"

    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    try:
        cur.execute(query, (sendable.user.id, location, pokemon, symbol))
        conn.commit()
    except sqlite3.IntegrityError:
        await sendable.send("can not insert a duplicate configuration!")
        return
    finally:
        conn.close()

    if pokemon is not None and location is not None:
        await sendable.send(f"you will now get a pm if a {pokemon} shows up at {location}.")
    elif pokemon is not None:
        await sendable.send(f"you will now get a pm if a {pokemon} shows up in a swarm.")
    elif location is not None:
        await sendable.send(f"you will now get a pm if a swarm shows up at {location}.")


async def pmworldboss(sendable: Sendable, pokemon: str=None, location: str=None):
    """
    pm for when worldboss with specific requirements shows up.
    """

    if pokemon is None and location is None:
        await sendable.send("select pokemon, location or both")
        return
    symbol = "|"
    if pokemon is not None and location is not None:
        symbol = "&"
    query = "INSERT INTO pmworldboss(playerid, location, boss, comparator) VALUES(?, ?, ?, ?)"
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    try:
        cur.execute(query, (sendable.user.id, location, pokemon, symbol))
        conn.commit()
    except sqlite3.IntegrityError:
        await sendable.send("can not insert a duplicate configuration!")
        return
    finally:
        conn.close()
    if pokemon is not None and location is not None:
        await sendable.send(f"you will now get a pm if a {pokemon} worldboss shows up at {location}.")
    elif pokemon is not None:
        await sendable.send(f"you will now get a pm if a {pokemon} worldboss shows up.")
    elif location is not None:
        await sendable.send(f"you will now get a pm if a worldboss shows up at {location}.")



async def pmtournament(sendable: Sendable, prize: str=None, tournament: str=None):
    """
    starts the configuration of pming a tournament to the user.
    The user gets 3 options:
    1. prize
    2. tournament type
    3. both
    With prize the user gets a pm if a tournament with the specified prize shows up.
    with tournament type the user gets a pm if a tournament of the specified type shows up.
    With both the user only gets a pm if the provided tournament shows up with the specified price.
    There is inputvalidation for the tournament type, but not for the prize (yet)
    :param ctx: discord context
    :todo input validation for prize
    """
    if prize is None and tournament is None:
        await sendable.send("select tournamenttype, prize or both!")
    symbol = "|"
    if prize is not None and tournament is not None:
        symbol = "&"
    query = "INSERT INTO pmtournament(playerid, tournament, prize, comparator) VALUES(?, ?, ?, ?)"
    conn = sqlite3.connect(databasepath)
    cur = conn.cursor()
    try:
        cur.execute(query, (sendable.user.id, tournament, prize, symbol))
        conn.commit()
    except sqlite3.IntegrityError:
        await sendable.send("can not insert a duplicate configuration!")
        return
    finally:
        conn.close()

    if tournament is not None and prize is not None:
        await sendable.send(f"you will now get a pm if a {tournament} shows up with prize "
                                                f"{prize}.")
    elif tournament is not None:
        await sendable.send(f"you will now get a pm if a {tournament} starts.")
    elif prize is not None:
        await sendable.send(f"you will now get a pm if a tournament with prize {prize} starts.")


async def removepmconfig(sendable: Sendable):
    """
    Starts user interaction to remove pm configuration of certain events.
    Fails if the time limit of 30 seconds to respond has expired.
    Asks for either a list of id's or a single id, and deletes those. Note that the id's are just list indexes, it
    gets the values at those list indexes to delete the configurations.
    :param ctx: discord context.
    """
    await sendable.send("what event do you want to remove pmconfig of?",
                                            view=RemovePmConfig(sendable, databasepath))
