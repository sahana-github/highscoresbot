import datetime

import discord

from ppobyter.events.clanevent import ClanEvent
import sqlite3


class Roll(ClanEvent):
    """
    This event gets triggered when someone rolls something.
    """
    def __init__(self, player: str, pokemon: str, level: str, date: str = None):
        """
        calls the init of the superclass and sets the pokemon and the level of it that pokemon was rolled.
        Also inserts rolled pokemon into the database.
        :param player: the player that rolled something.
        :param pokemon: The pokemon that was rolled.
        :param level: The level of the rolled pokemon.
        :param date: the date the pokemon was rolled as a string. default today.
        """
        if date is None:
            date = str(datetime.datetime.now()).split()[0]
        self.date = date
        self.level = level
        self.pokemon = pokemon.lower()
        self.EVENTNAME = "roll"
        super(Roll, self).__init__(player)
        self.insertRoll()

    def insertRoll(self):
        """
        Inserts the roll into the database.
        """
        conn = sqlite3.connect(self.pathManager.getpath("ingame_data.db"))
        cur = conn.cursor()
        cur.execute("INSERT INTO rolls(player, pokemon, date) VALUES(?, ?, ?)", (self.player, self.pokemon, self.date))
        conn.commit()
        conn.close()

    def determineRecipients(self):
        """
        determines the channels the encounter must be sent to.
        :return:
        """
        self._determinechannelrecipients()

    def makeMessage(self) -> discord.embeds.Embed:
        """
        Makes the embed message to send to the channels.
        :return: discord embed
        """
        shiny = False
        if '[s]' in self.pokemon:
            shiny = True
        pokemonname = self.pokemon.replace("[s]", "")
        if shiny:
            gif = r"http://play.pokemonshowdown.com/sprites/ani-shiny/{}.gif".format(pokemonname)
        else:
            gif = r"http://play.pokemonshowdown.com/sprites/ani/{}.gif".format(pokemonname)
        embed = discord.Embed(title="Congratulations {}!".format(self.player),
                              description=f"{self.player} has rolled a level {self.level} {self.pokemon}!",
                              color=0xFF5733)
        embed.set_thumbnail(url=gif)
        return embed
