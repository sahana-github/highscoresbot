import asyncio
from typing import Callable, Union, Iterable, Tuple, List
import enchant
import discord_components
from discord.ext import commands
import sqlite3
from discord_components import DiscordComponents, Button, ButtonStyle
from commands.utils.utils import tablify, isswarmpokemon, isswarmlocation, isgoldrushlocation, getgoldrushlocations, \
    ishoneylocation, gethoneylocations, istournamentprize
from discord.ext.commands.context import Context


class Pmconfig(commands.Cog):
    """
    This class contains commands for the configuration of events in pm's.
    """
    def __init__(self, client):
        self.client = client
        self.databasepath = "./eventconfigurations.db"

    @commands.command(name="pmgoldrush")
    async def pmgoldrush(self, ctx: Context, *location: str):
        """
        The user will receive a pm if a goldrush happens at the provided location.
        It is checked if it is a valid location.
        :param ctx: discord context
        :param location: the location where the goldrush happens.
        """
        location = " ".join(location)
        location = location.lower()
        if not isgoldrushlocation(location):
            await ctx.send("a goldrush can not happen at that location! list of locations:"
                           "```" + "\n".join(getgoldrushlocations()) + "```")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO pmgoldrush(playerid, location) VALUES(?,?)", (ctx.author.id, location))
            conn.commit()
            await ctx.send(f"You now get a pm when a gold rush shows up at {location}.")
        except sqlite3.IntegrityError:
            await ctx.send("can not insert the same location twice!")
        finally:
            conn.close()

    @commands.command(name="pmhoney")
    async def pmhoney(self, ctx: Context, *location: str):
        """
        The user will receive a pm if honey gets spread at the provided location.
        :param ctx: discord context
        :param location: the location where the honey gets spread.
        :todo input validation for the location
        """
        location = " ".join(location)
        location = location.lower()
        if not ishoneylocation(location):
            spelling_data = enchant.PyPWL()
            for honeylocation in gethoneylocations():
                #print(location)

                spelling_data.add(honeylocation)
            suggestedlocations = spelling_data.suggest(location)
            await ctx.send("that is not a valid honeylocation! Spelling suggestions:\n```" +
                           "\n".join(suggestedlocations) + "```")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO pmhoney(playerid, location) VALUES(?,?)", (ctx.author.id, location))
            conn.commit()
            await ctx.send(f"You now get a pm when honey shows up at {location}.")
        except sqlite3.IntegrityError:
            await ctx.send("can not insert the same location twice!")
        finally:
            conn.close()

    @commands.command(name='pmswarm')
    async def pmswarm(self, ctx: Context):
        """
        starts the configuration of pming a swarm to the user.
        The user gets 3 options:
        1. location
        2. pokemon
        3. both
        With location the user gets a pm that a swarm appeared at that location.
        With pokemon the user gets a pm if one of the 2 swarm pokemon is the pokemon the user provided.
        With both the user only gets a pm if the provided pokemon shows up at the provided location.
        :param ctx: discord context
        There is inputvalidation for both the swarm location and the swarm pokemon.
        """
        location, pokemon = await self.inputgetter(ctx, label1="location",
                                             label2="pokemon",
                                             msg1="Please pick the location at which the swarm must appear:",
                                             msg2="Please pick what pokemon the swarm must contain:",
                                             buttonresponse="See https://pokemon-planet.com/swarms for a list of swarm"
                                                            " pokemon and locations.",
                                                   inputvalidation1=isswarmlocation,
                                                   inputvalidation2=isswarmpokemon,
                                                   inputvalidationmsg1="that is not a swarm location!",
                                                   inputvalidationmsg2="that is not a swarm pokemon!")

        if location is not None and pokemon is not None:
            query = "INSERT INTO pmswarm(playerid, location, pokemon, comparator) VALUES(?, ?, ?, '&')"
        elif location is not None or pokemon is not None:
            query = "INSERT INTO pmswarm(playerid, location, pokemon, comparator) VALUES(?, ?, ?, '|')"
        else:
            await ctx.send("failed to setup. Please try again")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute(query, (ctx.author.id, location, pokemon))
            conn.commit()
        except sqlite3.IntegrityError:
            await ctx.send("can not insert a duplicate configuration!")
            return
        finally:
            conn.close()
        if pokemon is not None and location is not None:
            await ctx.send(f"you will now get a pm if a {pokemon} shows up at {location}.")
        elif pokemon is not None:
            await ctx.send(f"you will now get a pm if a {pokemon} shows up in a swarm.")
        elif location is not None:
            await ctx.send(f"you will now get a pm if a swarm shows up at {location}.")

    @commands.command(name="pmworldboss")
    async def pmworldboss(self, ctx):
        """
        starts the configuration of pming a worldboss to the user.
        The user gets 3 options:
        1. location
        2. worldboss pokemon
        3. both
        With location the user gets a pm that a worldboss appeared at that location.
        With worldboss pokemon the user gets a pm if the worldboss provided shows up at any location.
        With both the user only gets a pm if the provided worldboss pokemon shows up at the provided location.
        There is inputvalidation for the worldboss pokemon, but not for the location.
        :param ctx: discord context
        """
        worldbosses = ['mew', 'articuno', 'suicune', 'darkrai', 'darkrai', 'mesprit', 'shaymin', 'latias', 'regigigas',
                       'uxie', 'entei', 'azelf', 'suicune', 'zapdos', 'cresselia', 'moltres', 'latios', 'heatran',
                       'heatran', 'azelf', 'raikou', "giratina", "yveltal"]
        buttonresponse = "The possible worldbosses are:\n" + ", ".join(worldbosses) + "\nMind spelling the location " \
                                                                                      "right since there is no check " \
                                                                                      "if the location actually exists"
        location, pokemon = await self.inputgetter(ctx, label1="location", label2="worldboss pokemon",
                               msg1="Please enter the location where the worldboss should spawn:",
                               msg2="Please enter the worldboss that should spawn:",
                               buttonresponse=buttonresponse,
                                                   inputvalidation2=worldbosses,
                                                   inputvalidationmsg2="That is not a valid worldboss!")

        if location is not None and pokemon is not None:
            query = "INSERT INTO pmworldboss(playerid, location, boss, comparator) VALUES(?, ?, ?, '&')"
        elif location is not None or pokemon is not None:
            query = "INSERT INTO pmworldboss(playerid, location, boss, comparator) VALUES(?, ?, ?, '|')"
        else:
            await ctx.send("failed to setup. Please try again.")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute(query, (ctx.author.id, location, pokemon))
            conn.commit()
        except sqlite3.IntegrityError:
            await ctx.send("can not insert a duplicate configuration!")
            return
        finally:
            conn.close()
        if pokemon is not None and location is not None:
            await ctx.send(f"you will now get a pm if a {pokemon} worldboss shows up at {location}.")
        elif pokemon is not None:
            await ctx.send(f"you will now get a pm if a {pokemon} worldboss shows up.")
        elif location is not None:
            await ctx.send(f"you will now get a pm if a worldboss shows up at {location}.")

    @commands.command(name="pmtournament")
    async def pmtournament(self, ctx):
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
        tournamenttypes = ["ubers", "self caught", "little cup", "monotype", "set level 100"]
        buttonresponse = "You can pick the following tournament types:\n" + ", ".join(tournamenttypes) + "\n" + \
                            "Mind that there is no spelling check present! So type the tournament prizes good. " \
                            "For example: `latias egg`, the amount does not matter."

        prize, tournament = await self.inputgetter(ctx,
                                                   label1="prize",
                                                   label2="tournament type",
                                                   msg1="enter the name of the prize:",
                                                   msg2="enter the name of the tournament:",
                                                   buttonresponse=buttonresponse,
                                                   inputvalidation1=istournamentprize,
                                                   inputvalidationmsg1="that is not an existing tournament prize!",
                                                   inputvalidation2=tournamenttypes,
                                                   inputvalidationmsg2="that is not an existing tournament!")

        if tournament is not None and prize is not None:
            query = "INSERT INTO pmtournament(playerid, tournament, prize, comparator) VALUES(?, ?, ?, '&')"
        elif tournament is not None or prize is not None:
            query = "INSERT INTO pmtournament(playerid, tournament, prize, comparator) VALUES(?, ?, ?, '|')"
        else:
            await ctx.send("failed to setup. please try again.")
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        try:
            cur.execute(query, (ctx.author.id, tournament, prize))
            conn.commit()
        except sqlite3.IntegrityError:
            await ctx.send("can not insert a duplicate configuration")
            return
        finally:
            conn.close()

        if prize is not None and tournament is not None:
            await ctx.send(f"You will now get a pm if the {tournament} tournament with the prize {prize} shows up.")
        elif prize is not None:
            await ctx.send(f"You will now get a pm if a tournament with the prize {prize} shows up.")
        elif tournament is not None:
            await ctx.send(f"You will now get a pm for the {tournament} tournament.")

    async def inputgetter(self, ctx: Context, label1: str, label2: str, msg1: str, msg2: str,
                          buttonresponse: str="beginning setup! respond within 30 seconds, else retype command.",
                          inputvalidation1: Union[Callable[[str], bool], Iterable] = None,
                          inputvalidation2: Union[Callable[[str], bool], Iterable] = None,
                          inputvalidationmsg1: str = None, inputvalidationmsg2: str = None
                          ) -> Tuple[Union[str, None], Union[str, None]]:
        """
        This function shows 3 buttons, if the button with name 'both' is pressed it asks for input via a message twice.
        Else it just asks for input of one of the 2 provided labels. The asking for input will fail after no response
        for 30 seconds. Then (None, None) will be returned.
        :param ctx: discord context
        :param label1: The label of the first button.
        :param label2: The label of the second button.
        :param msg1: The message to send when asking for the first input.
        :param msg2: The message to send when asking for the second input.
        :param buttonresponse: The response to send after the button press.
        :param inputvalidation1: either a list or a function. If it is an iterable it checks if the value is present in
                                                                                                          the iterable.
                                 If it is a function it validates the given string and returns True
                                                                                               if the value is allowed.
        :param inputvalidation2: either a list or a function. If it is an iterable it checks if the value is present in
                                                                                                          the iterable.
                                 If it is a function it validates the given string and returns True
                                                                                               if the value is allowed.
        :param inputvalidationmsg1: The message to send when the value is not allowed.
        :param inputvalidationmsg2: The message to send when the value is not allowed.
        :return: a tuple of 2 values. The first represents the first input, the second one represents the second input.
                Either one or both can be None. When 'None, None' is returned it means getting the input failed.
        """
        input1 = None
        input2 = None
        buttons = [Button(style=ButtonStyle.blue, label=label1),
                   Button(style=ButtonStyle.red, label=label2),
                   Button(style=ButtonStyle.green, label="both")]

        await ctx.send("what do you want to register for?", components=[buttons], )

        def check(res):
            return res.channel == ctx.channel and res.author == ctx.author and res.component.id in \
                   [button.id for button in buttons]
        res = await self.client.wait_for("button_click", check=check)
        if res.channel == ctx.channel and res.author == ctx.author:
            await res.respond(content=buttonresponse)
            try:
                if res.component.label == label1 or res.component.label == "both":
                    if (input1 := await self.__singleinput(ctx, msg1, inputvalidation1, inputvalidationmsg1)) is None:
                        return None, None
                if res.component.label == label2 or res.component.label == "both":
                    if (input2 := await self.__singleinput(ctx, msg2, inputvalidation2, inputvalidationmsg2)) is None:
                        return None, None
            except asyncio.exceptions.TimeoutError:
                await ctx.send("time limit of 30 seconds exceeded!")
                return None, None
            return input1, input2
        else:
            return None, None

    async def __singleinput(self, ctx: Context, msg1: str, inputvalidation: Union[Callable[[str], bool], Iterable],
                            inputvalidationmsg: str) -> Union[str, None]:
        """
        This method asks for a single input.
        :param ctx: discord context
        :param msg1: The message in where you ask for user input.
        :param inputvalidation: either a list or a function. If it is an iterable it checks if the value is present in
                                                                                                          the iterable.
                                 If it is a function it validates the given string and returns True
                                                                                               if the value is allowed.
        :param inputvalidationmsg: The message to send if the provided input does not match the inputvalidation.
        :return: the input or None.
        """
        await ctx.send(msg1)
        msg = await self.client.wait_for('message', check=lambda context: self.__check(ctx.author.id, context),
                                         timeout=30)
        input1 = msg.content.lower()
        # the value is not allowed
        if inputvalidation is not None and ((callable(inputvalidation) and not inputvalidation(input1))
                                             or (hasattr(inputvalidation, '__iter__') and
                                                 input not in inputvalidation)):

            if inputvalidationmsg is not None:
                await ctx.send(inputvalidationmsg)
            else:
                msg = "That value is not allowed."
                if hasattr(inputvalidation, '__iter__'):
                    msg += " Allowed values:\n" + ", ".join(inputvalidation)
                await ctx.send(msg)
            return None
        return input1

    def __check(self, originauthorid: int, newmsg: Context) -> bool:
        """
        checks if the authorid is equal to the userid of the message.
        :param originauthorid: the author id.
        :param newmsg: a discord message.
        :return: boolean
        """
        # and no it can't be static, gives errors. Or maybe it should be put in main or made a lambda.
        # @todo
        return originauthorid == newmsg.author.id

    @commands.command(name="removepmconfig")
    async def removepmconfig(self, ctx: Context):
        """
        Starts user interaction to remove pm configuration of certain events.
        Fails if the time limit of 30 seconds to respond has expired.
        Asks for either a list of id's or a single id, and deletes those. Note that the id's are just list indexes, it
        gets the values at those list indexes to delete the configurations.
        :param ctx: discord context.
        """
        buttons = [
            Button(style=ButtonStyle.blue, label="goldrush"),
            Button(style=ButtonStyle.blue, label="swarm"),
            Button(style=ButtonStyle.blue, label="worldboss"),
            Button(style=ButtonStyle.blue, label="honey"),
            Button(style=ButtonStyle.blue, label="tournament")]
        await ctx.send("what do you want to unregister for?", components=[buttons])

        buttonids = [button.id for button in buttons]
        def check(res):
            return res.channel == ctx.channel and res.author == ctx.author and \
                   res.component.id in buttonids
        res = await self.client.wait_for("button_click", check=check)
        if res.channel == ctx.channel and res.author == ctx.author:
            await res.respond(content="starting removal. respond within 30 seconds, else retype command.")
            conn = sqlite3.connect(self.databasepath)
            cur = conn.cursor()
            if res.component.label == "swarm":
                cur.execute("SELECT pokemon, location, comparator FROM pmswarm WHERE playerid = ?", (ctx.author.id,))
                layout = ["id", "pokemon", "location", "comparator"]
            elif res.component.label == "goldrush":
                cur.execute("SELECT location FROM pmgoldrush WHERE playerid = ?", (ctx.author.id,))
                layout = ["id", "location"]
            elif res.component.label == "honey":
                cur.execute("SELECT location FROM pmhoney WHERE playerid = ?", (ctx.author.id,))
                layout = ["id", "location"]
            elif res.component.label == "tournament":
                cur.execute("SELECT tournament, prize, comparator FROM pmtournament WHERE playerid=?", (ctx.author.id,))
                layout = ["id", "tournament", "prize", "comparator"]
            elif res.component.label == "worldboss":
                cur.execute("SELECT boss, location, comparator FROM pmworldboss WHERE playerid=?", (ctx.author.id,))
                layout = ["id", "worldboss", "location", "comparator"]
        else:
            return
        result = cur.fetchall()
        conn.close()
        originalresult = result
        result = [[str(id)] + list(result[id]) for id in range(len(result))]
        messages = tablify(layout, result)

        if len(messages) == 1 and messages[0] == "Nothing found to be sent.":
            await ctx.send(messages[0])
            return

        for message in messages:
            await ctx.send(message)

        ids = await self.__getids(ctx)  # @todo

        await self.__deleteids(ctx, ids, res.component.label, originalresult)

    async def __deleteids(self, ctx: Context, ids: Iterable, eventname: str, result: List[List]):
        """
        Deletes the provided configurations (ids) at the index of result.
        :param ctx: discord context
        :param ids: an iterable of ids to be deleted.
        :param eventname: the name of the event.
        :param result: A list of configurations.
        """
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        for id in ids:
            if eventname == "swarm":
                # pokemon, location, comparator
                query = "DELETE FROM pmswarm WHERE pokemon is ? AND location is ? AND comparator=? AND playerid=?"
            elif eventname == "worldboss":
                query = "DELETE FROM pmworldboss WHERE boss is ? AND location is ? AND comparator=? AND playerid=?"
            elif eventname == "goldrush":
                query = "DELETE FROM pmgoldrush WHERE location=? AND playerid=?"
            elif eventname == "tournament":
                query = "DELETE FROM pmtournament WHERE tournament is ? AND prize is? AND compatator=? AND playerid=?"
            elif eventname == "honey":
                query = "DELETE FROM pmhoney WHERE location=? AND playerid=?"
            try:
                cur.execute(query, list(result[id]) + [ctx.author.id])
            except IndexError:
                pass
        conn.commit()
        conn.close()
        await ctx.send("success!!!")

    async def __getids(self, ctx: Context) -> list:
        """
        gets a list of ids.
        :param ctx: discord context
        :return: a list of ids.
        """
        await ctx.send(
            "enter the id or id's (seperated by comma if multiple) for the event you no longer want to be registered for.")
        msg = await self.client.wait_for('message', check=lambda context: self.__check(ctx.author.id, context),
                                         timeout=30)
        ids = msg.content
        try:
            ids = [int(id.strip()) for id in ids.split(",")]
        except ValueError:  # @todo deal with this!
            await ctx.send("failed, input must be the id or id's(if multiple seperated by comma) of the event you want "
                           "to unregister for.\nplease try again.")
        return ids


def setup(client):
    client.add_cog(Pmconfig(client))
    #help(Button)
if __name__ == "__main__":
    print(help(discord_components.interaction.Interaction))