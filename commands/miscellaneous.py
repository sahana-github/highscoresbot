import io
import json
import sqlite3
import random
from threading import Thread

import discord
from PIL import Image, ImageDraw, ImageFont
from discord import ClientUser
from discord.ext import commands
import datetime
import asyncio

from discord_components import ButtonStyle, Button
from commands.utils.utils import getworldbosstime, tablify, ResultmessageShower

from discord.ext.commands.context import Context

from commands.utils.scroller import ImgWithText, Scroller
from highscores import getClanList
from ppobyter.marketplace.item import Item
from ppobyter.marketplace.pokemon import Pokemon


class Miscellaneous(commands.Cog):
    def __init__(self, client: discord.ext.commands.bot):
        self.client: discord.ext.commands.bot.Bot = client
        self.client.loop.create_task(self.status_task())
        self.invitelink = "https://discord.com/login?redirect_to=" \
                          "%2Foauth2%2Fauthorize%3Fclient_id%3D733434249771745401%26permissions%3D2048%26redirect_uri" \
                          "%3Dhttps%253A%252F%252Fdiscordapp.com%252Foauth2%252Fauthorize%253F%2526" \
                          "permissions%253D141312%2526client_id%253D733434249771745401%2526scope%253Dbot%26scope%3Dbot"

    @commands.command(name="worldbosstime")
    async def worldbosstime(self, ctx: Context):
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
            await ctx.send(embed=embed)
        except IndexError:
            await ctx.send("something went wrong!")
        except Exception as e:
            await ctx.send("uncaught exception.")
            print(e)


    @commands.command(name="clanlist")
    async def clanlist(self, ctx: Context, clanname: str):
        """
        gives a list of players that are in the provided clan.
        :param ctx: discord context
        :param clanname: the name of the clan you want the clanlist from.
        """
        clanname = clanname.lower()
        result = getClanList(clanname)
        result.sort()
        if result:
            await ctx.send(f"clanlist of {clanname}: \n" + ", ".join(result))
        else:
            await ctx.send("no results found for that clanname.")

    @commands.command(name="invite")
    async def invite(self, ctx: Context):
        """
        gives the invitelink to the support server and of the bot.
        :param ctx: discord context
        """
        embed = discord.Embed()
        embed.description = "this is the [invite link]" \
                            "({})"  \
                            "\n also join the [support server](https://discord.gg/PmXY35aqgH)".format(self.invitelink)
        await ctx.send(embed=embed)

    @commands.command(name="setdefault")
    async def setdefault(self, ctx: Context, clanname: str = None):
        """
        sets a default for the highscores commands. If the clanname is not provided the default will be removed.
        :param ctx: discord context
        :param clanname: the clan you want to set as default for the highscores commands.
        """
        clanname = clanname.lower()
        if ctx.guild is None:
            await ctx.send("this command can't be used in pm.")
            return
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("insufficient permissions to use this command. Ask a server administrator!")
            return
        id = ctx.guild.id
        conn = sqlite3.connect("highscores.db")
        cur = conn.cursor()
        if clanname is not None:
            try:
                cur.execute("INSERT INTO clannames(id, name) VALUES(?,?)", (id, clanname))
            except sqlite3.IntegrityError:
                cur.execute("UPDATE clannames SET name=? WHERE id=?", (clanname, id))
            msg = await ctx.send(f"{clanname} registered as default!")
        else:
            cur.execute("UPDATE clannames SET name = NULL WHERE id=?", (id,))
            msg = await ctx.send("default has been removed!")
        try:
            conn.commit()
        except Exception as e:
            print(e)
            await msg.delete()
            await ctx.send("Something went wrong. Developer is informed.")
            raise e

    @commands.command(name="worldboss")
    async def worldboss(self, ctx: Context, playername: str):
        """
        shows a list of worldbosses a player participated in.
        :param ctx: discord context
        :param playername: the player of who you want to see the worldbosses he/she participated in.
        """
        viewquery = """
        CREATE VIEW participants
        AS
        SELECT worldbossid, count(*) as amount FROM worldboss_dmg GROUP BY worldbossid;
        """
        selectquery = """
        SELECT worldboss.worldbossname, worldboss_dmg.damage, worldboss.date, rankings.position, participants.amount
        FROM worldboss_dmg, worldboss, participants, rankings
        WHERE worldboss_dmg.playername=?
        AND worldboss.id = worldboss_dmg.worldbossid AND worldboss_dmg.worldbossid = participants.worldbossid
        AND rankings.playername=worldboss_dmg.playername AND rankings.worldbossid = worldboss_dmg.worldbossid
        """
        rankingsquery = """
        CREATE VIEW rankings
        AS
        SELECT rank() OVER (PARTITION BY  worldbossid ORDER BY damage DESC) as position, * FROM worldboss_dmg
        """
        playername = playername.lower()
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        try:
            cur.execute("DROP VIEW participants")
            cur.execute("DROP VIEW rankings")
        except sqlite3.OperationalError:
            pass  # already exists.
        cur.execute(viewquery)
        cur.execute(rankingsquery)
        cur.execute(selectquery, (playername,))

        result = cur.fetchall()
        cur.execute("DROP VIEW participants")
        cur.execute("DROP VIEW rankings")
        messages = tablify(["worldboss", "damage", "date", "rank", "participants"], result)
        messageshower = ResultmessageShower(self.client, messages[::-1], ctx, 600)
        await messageshower.loop()

    @commands.command(name="servercount")
    async def servercount(self, ctx: Context):
        await ctx.send("i'm in {0} servers.".format(str(len(self.client.guilds))))

    @commands.command(name="gmsearch")
    async def gmsearch(self, ctx: Context, *searchstring):
        searchstring = " ".join(searchstring)
        if not searchstring:
            await ctx.send("use .gmsearch manaphy for example, where manaphy is the pokemon you search for.")
            return
        msg = await ctx.send("queued up for gm search.")
        if ctx.guild is None:
            # is pm
            ispm = 1
            fetchid = ctx.author.id
        else:
            ispm = 0
            # is guild
            fetchid = ctx.channel.id
        conn = sqlite3.connect("eventconfigurations.db")
        cur = conn.cursor()
        result = cur.execute("INSERT INTO gmsearch(msgid, fetchid, isdm, searchstring, timestamp) VALUES(?,?,?,?,?)",
                    (msg.id, fetchid, ispm, searchstring, int(datetime.datetime.now().timestamp())))
        print(result.lastrowid)
        conn.commit()

        while True:
            await asyncio.sleep(5)
            cur.execute("SELECT page, content FROM gmsearchresult WHERE responseid=?", (result.lastrowid,))
            #cur.execute("SELECT page, content FROM gmsearchresult WHERE responseid=?", (result.lastrowid,))
            if gmsearches := cur.fetchall():
                print("results are in!")
                break
        pages = []
        if gmsearches[0][1] is None:
            await ctx.send("the search didn't return any items/pokemon!")
            return
        for row in gmsearches:
            item = Item.from_dict(dict(json.loads(row[1].replace("'", '"'))))
            embed = discord.Embed(title=item.itemname,
                                  description=f"amount: {item.amount}")
            embed.add_field(name="price", value=item.price)
            embed.add_field(name="seller", value=item.seller)
            if item.isPokemon():
                def generate_img(pokemon):
                    return lambda: self.__generate_img(pokemon)
                img = generate_img(item.pokemon)
            else:
                img = None
            pages.append(ImgWithText(img, embed))
        c = Scroller(self.client, pages, ctx)
        await c.loop()




        #print(gmsearches)

    def __generate_img(self, pokemon: Pokemon):
        # all sprites come from https://github.com/PokeAPI/sprites
        if pokemon is None:
            print("warning: None")
            return
        img = Image.open(r"base_pokemon.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(r"memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.ttf",
                                  15)
        # font = ImageFont.load_default()
        draw.text((79, 478), pokemon.helditem, (255, 255, 255), font=font)  # held item
        draw.text((363, 95), f"{pokemon.pokemonnumber}", (255, 255, 255), font=font)  # pokemon number
        draw.text((83, 375), f"Lv {pokemon.level} {pokemon.pokemonname}", font=font)
        draw.text((363, 172), pokemon.nature, (255, 255, 255), font=font)  # nature
        draw.text((363, 210), f"{pokemon.happiness}", (255, 255, 255), font=font)  # happiness
        draw.text((363, 247), f"{pokemon.ability}", (255, 255, 255), font=font)  # ability
        draw.text((363, 285), pokemon.catcher, (255, 255, 255), font=font)  # catcher
        draw.text((363, 331), f"{pokemon.hp}", (255, 255, 255), font=font)  # calculated hp
        draw.text((363, 408), f"{pokemon.atk}", (255, 255, 255), font=font)  # calculated atk
        draw.text((363, 445), f"{pokemon.defense}", (255, 255, 255), font=font)  # calculated def
        draw.text((363, 484), f"{pokemon.spatk}", (255, 255, 255), font=font)  # calculated spatk
        draw.text((363, 520), f"{pokemon.spdef}", (255, 255, 255), font=font)  # calculated spdef
        draw.text((363, 557), f"{pokemon.speed}", (255, 255, 255), font=font)  # calculated speed

        draw.text((400, 331), f"({pokemon.hpiv})", (219, 225, 165), font=font)  # hp iv
        draw.text((400, 408), f"({pokemon.atkiv})", (219, 225, 165), font=font)  # atk iv
        draw.text((400, 445), f"({pokemon.defiv})", (219, 225, 165), font=font)  # def iv
        draw.text((400, 484), f"({pokemon.spatkiv})", (219, 225, 165), font=font)  # spatk iv
        draw.text((400, 520), f"({pokemon.spdefiv})", (219, 225, 165), font=font)  # spdef iv
        draw.text((400, 557), f"({pokemon.speediv})", (219, 225, 165), font=font)  # speed iv

        draw.text((435, 331), f"({pokemon.hpev})", (182, 219, 180), font=font)  # hp ev
        draw.text((435, 408), f"({pokemon.atkev})", (182, 219, 180), font=font)  # atk ev
        draw.text((435, 445), f"({pokemon.defev})", (182, 219, 180), font=font)  # def ev
        draw.text((435, 484), f"({pokemon.spatkev})", (182, 219, 180), font=font)  # spatk ev
        draw.text((435, 520), f"({pokemon.spdefev})", (182, 219, 180), font=font)  # spdef ev
        draw.text((435, 557), f"({pokemon.speedev})", (182, 219, 180), font=font)  # speed ev
        try:  # adding sprite of the pokemon.
            sprite = Image.open(r"sprites/pokemon/" + str(pokemon.pokemonnumber) + ".png")
            sprite = sprite.resize((200,200))
            for y in range(sprite.height):
                for x in range(sprite.width):
                    pixel = sprite.getpixel((x, y))
                    if pixel == 0 or pixel == 9:
                        sprite.putpixel((x, y), (233, 235, 233))
            img.paste(sprite, (48, 128))
        except Exception as e:
            print(f"exception with {pokemon.pokemonname} when adding sprite for pokemon", e)
        if pokemon.helditem != "none":
            try:
                helditem = Image.open(r"sprites/items/" + str(pokemon.helditem).replace(" ", "-") + ".png")
                helditem = helditem.resize((46, 44))
                img.paste(helditem, (22, 470))
            except Exception as e:
                print(f"exception when adding held item. Held item: {pokemon.helditem}", e)
        return img

    @commands.command(name="about")
    async def about(self, ctx: Context):
        embed = discord.Embed(title="About Us", description="Who are we?", color=0xFF5733)
        embed.add_field(name="Green", value="One of the founders of the bot along with Kevin. Currently not working "
                                            "on the project anymore.")
        embed.add_field(name="Kevin123456#2069", value="One of the founders of the bot along with Green. "
                                                       "Feel free to pm me if you have any questions.")
        embed.add_field(name="Degjay", value="Funds the machine the bot is run on. Making this bot free to use. "
                                             "Also has his own bot called evobot which shows the evolutionary line of "
                                             "pokemon.")
        embed.add_field(name="Patreon", value="Come support as us at Patreon - https://www.patreon.com/highscores_bot")
        embed.add_field(name="Source", value="The sourcecode is available at https://github.com/graatje/highscoresbot")
        await ctx.send(embed=embed)

    @commands.command(name="help")
    async def help(self, ctx: Context, command: str = None):
        """
        This shows help on the commands.
        :param ctx: discord context
        :param command: the name of the command you want to see the help message from.
        """
        if command is not None:
            command = command.lower()
        embed = None
        if type(self.client.command_prefix) == list:
            prefix = random.choice(self.client.command_prefix)
        else:
            prefix = self.client.command_prefix
        if command is None:
            helpcmd = HelpCommand()
            buttons = [Button(style=ButtonStyle.blue, label="<<"),
                       Button(style=ButtonStyle.blue, label="<"),
                       Button(style=ButtonStyle.red, label=">"),
                       Button(style=ButtonStyle.red, label=">>")]
            msg = await ctx.send(embed=helpcmd.change_page(0), components=[buttons], )
            def check(res):
                return res.channel == ctx.channel and res.author == ctx.author and \
                    res.component.id in [button.id for button in buttons]
            while True:
                try:
                    res = await self.client.wait_for("button_click", check=check, timeout=60)
                    if res.component.label == "<":
                        await res.edit_origin(embed=helpcmd.change_page(-1))
                    elif res.component.label == ">":
                        await res.edit_origin(embed=helpcmd.change_page(1))
                    elif res.component.label == "<<":
                        await res.edit_origin(embed=helpcmd.change_page(1, True))
                    elif res.component.label == ">>":
                        await res.edit_origin(embed=helpcmd.change_page(helpcmd.max_page, True))
                except asyncio.TimeoutError:
                    await msg.delete()
                    break
        elif command == "setperms":
            embed = discord.Embed(title=f"{prefix}setperms",
                                  description=f"{prefix}setperms <role>", color=0xFF5733)
            embed.add_field(name="Use",
                            value="this gives permissions to the specified role to adjust eventconfigurations for this "
                                  "server. You can use either a role mention or a role id.")
        elif command == "getclanencounters":
            embed = discord.Embed(title=f"{prefix}getclanencounters",
                                  description=f"{prefix}getclanencounters <clanname>", color=0xFF5733)
            embed.add_field(name="Use",
                            value="This command gets encounters of a clan, they are sorted by day but not sorted by "
                                  "time the encounter happened")
        elif command == "getrolls":
            embed = discord.Embed(title=f"{prefix}getrolls",
                                  description=f"{prefix}getrolls <parameter>", color=0xFF5733)
            embed.add_field(name="Use",
                            value="This command gets the rolls of either a pokemon, a date or a player. "
                                  "The bot has been keeping track of rolls since the 10th of october 2021.\n"
                                  "1. Player, the name you provided was a player.\n"
                                  "2. Date, the name you provided in the command was a date. Must be format yyyy-mm-dd"
                                  f"\nExample '{prefix}getrolls 2021-10-11' for the 11th of october 2021."
                                  "\n3. Pokemon, the name you provided was a pokemon.")

        elif command == "removeperms":
            embed = discord.Embed(title=f"{prefix}removeperms",
                                  description=f"{prefix}removeperms <role>")
            embed.add_field(name="Use",
                            value="Removes the permissions to adjust settings for this server of the specified role")
        elif command == "register":
            embed = discord.Embed(title=f"{prefix}register",
                                  description=f"{prefix}register <eventname> <channel>")
            embed.add_field(name="Use",
                            value="this command registers an event that will be announced when it "
                                  "occures in the specified channel. "
                                  "If the channel is not specified the event will be registered in the channel where"
                                  " the command was used.")
        elif command == "unregister":
            embed = discord.Embed(title=f"{prefix}unregister",
                                  description=f"{prefix}unregister <eventname>")
            embed.add_field(name="Use",
                            value="You will no longer receive messages from the event of the specified eventname "
                                  "after use. If the eventname is `all` no events will be announced in that server anymore.")
        elif command == "setpingrole":
            embed = discord.Embed(title=f"{prefix}setpingrole",
                                  description=f"{prefix}setpingrole <eventname> <role>")
            embed.add_field(name="Use",
                            value="Pings the specified role when this event occures. The role can also be the role id.")
        elif command == "removeping":
            embed = discord.Embed(title=f"{prefix}removeping",
                                  description=f"{prefix}removeping <eventname>")
            embed.add_field(name="Use",
                            value="Removes the role to ping of the specified event.")
        elif command == "settime":
            embed = discord.Embed(title=f"{prefix}settime",
                                  description=f"{prefix}settime <eventname> <time_in_channel>")
            embed.add_field(name="Use",
                            value="Sets the time in minutes that the message of the event should stay in the channel. "
                                  "When the time is not specified the current set time will be removed if present.")
        elif command == "registerclan":
            embed = discord.Embed(title=f"{prefix}registerclan",
                                  description=f"{prefix}registerclan <clanname>")
            embed.add_field(name="Use",
                            value="The provided clan will be set to receive encounters/elite4/chests "
                                  "for if those are set. You are able to register multiple clans. You are also able to "
                                  "register `all`. Then you will receive any announcement of an event based on clans of"
                                  " players.")
        elif command == "unregisterclan":
            embed = discord.Embed(title=f"{prefix}unregisterclan",
                                  description=f"{prefix}unregisterclan <clanname>")
            embed.add_field(name="Use",
                            value="The provided clan will be removed from the registered clans, which means that you"
                                  " will no longer receive encounters/elite4/chests from those events if they are set."
                                  f" If you do `{prefix}unregisterclan all` everything will be removed unless `all` is "
                                  f"already set with `{prefix}registerclan all`.")
        elif command == "showregistrations":
            embed = discord.Embed(title=f"{prefix}showregistrations",
                                  description=f"{prefix}showregistrations")
            embed.add_field(name="Use",
                            value="Shows the events you are registered for, the time the messages of that event will "
                                  "stay in the channel, and the role that gets pinged when that event happens.")
        elif command == "getperms":
            embed = discord.Embed(title=f"{prefix}getperms",
                                  description=f"{prefix}getperms")
            embed.add_field(name="Use",
                            value="Shows what roles have permissions to adjust settings for eventconfigurations.")
        elif command == "getclanregistrations":
            embed = discord.Embed(title=f"{prefix}getclanregistrations",
                                  description=f"{prefix}getclanregistrations")
            embed.add_field(name="Use",
                            value="Shows the clans that are registered for this server.")
            # eventconfig for pm
        elif command == "pmgoldrush":
            embed = discord.Embed(title=f"{prefix}pmgoldrush",
                                  description=f"{prefix}pmgoldrush <location>")
            embed.add_field(name="Use",
                            value="You get a pm if a goldrush at the location you provided in the command shows up.")
        elif command == "pmhoney":
            embed = discord.Embed(title=f"{prefix}pmhoney",
                                  description=f"{prefix}pmhoney <location>")
            embed.add_field(name="Use",
                            value="You get a pm if honey gets spread at the location you provided in the command."
                                  "Mind your spelling! locations do not get checked if they actually exist (yet)! "
                                  "Capitalization does not matter.")
        elif command == "pmswarm":
            embed = discord.Embed(title=f"{prefix}pmswarm",
                                  description=f"{prefix}pmswarm")
            embed.add_field(name="Use",
                            value="This starts the configuration of pming a swarm under certain conditions like"
                                  " location and pokemon", inline=False)
            embed.add_field(name="Location",
                            value="If you just pick location you will get a pm if a swarm at that location shows up.")
            embed.add_field(name="Pokemon",
                            value="If you pick pokemon you will get a pm if a swarm with this pokemon shows up.")
            embed.add_field(name="Both",
                            value="If you pick both you will get a pm if the pokemon you picked shows up at the "
                                  "location you picked.")
        elif command == "pmworldboss":
            embed = discord.Embed(title=f"{prefix}pmworldboss",
                                  description=f"{prefix}pmworldboss")
            embed.add_field(name="Use",
                            value="This starts the configuration of pming a worldboss under certain conditions like "
                                  "location and pokemon", inline=False)
            embed.add_field(name="Location", value="If you just pick location you will get a pm "
                                                   "if a worldboss at that location shows up.")
            embed.add_field(name="Worldboss pokemon",
                            value="If you pick worldboss pokemon you will get a pm if this worldboss pokemon shows up.")
            embed.add_field(name="Both",
                            value="If you pick both you will get a pm if the worldboss you picked shows up at the "
                                  "location you picked.")
        elif command == "pmtournament":
            embed = discord.Embed(title=f"{prefix}pmtournament", description=f"{prefix}pmtournament")
            embed.add_field(name="Use",
                            value="This starts the configuration of pming a tournament under certain conditions like "
                                  " location and prize", inline=False)
            embed.add_field(name="Prize",
                            value="If you just pick prize you will get a pm if a tournament with the provided prize "
                                  "will start")
            embed.add_field(name="Tournament type",
                            value="You will get a pm if this kind of tournament will start like 'set level 100'")
            embed.add_field(name="Both",
                            value="If you pick both you will get a pm if the kind of tournament you picked will start "
                                  "with the prize you picked.")
        elif command == "removepmconfig":
            embed = discord.Embed(title=f"{prefix}removepmconfig",
                                  description=f"{prefix}removepmconfig")
            embed.add_field(name="Use",
                            value="lets you remove an event of the type you provided, shows a list of the events of"
                                  "  that type you are currently registered for. Then lets you type the id of the "
                                  "event(s) you want to be unregistered for. Example: ```1,3```")

            # highscores commands
        elif command == "top":
            embed = discord.Embed(title="top", color=0xFFAFC9)
            embed.add_field(name="top <clanname(optional)>",
                            value="shows top 9 from a highscore (+ clan if specified or registered). ",
                            inline=False)

        elif command == "achievements":
            embed = discord.Embed(title="achievements <clanname>",
                                  description="shows achievements highscore of a clan.",
                                  color=0xFFAFC9)

        elif command == "bestclans":
            embed = discord.Embed(title="bestclans <clanname(optional)>",
                                  description="shows top 9 of most exp of a clan", color=0xFFAFC9)

        elif command == "btwins":
            embed = discord.Embed(title="btwins <clanname>",
                                  description="shows the highscore of the most battletower wins of a clan",
                                  color=0xFFAFC9)

        elif command == "btwinstreak":
            embed = discord.Embed(title="btwinstreak <clanname>",
                                  description="shows top battletower winstreak of a clan.", color=0xFFAFC9)

        elif command == "clanlist":
            embed = discord.Embed(title="clanlist <clanname>", description="gives a clanlist of the clan specified.",
                                  color=0xFFAFC9)

        elif command == "cwplayers":
            embed = discord.Embed(title="cwplayers <clanname>", description="shows top clan war players of a clan.",
                                  color=0xFFAFC9)

        elif command == "cwwins":
            embed = discord.Embed(title="cwwins <clanname>", description="shows top clan war wins of a clan",
                                  color=0xFFAFC9)

        elif command == "dex":
            embed = discord.Embed(title="dex <clanname>",
                                  description="shows the highscore of the most pokemon caught of a clan.",
                                  color=0xFFAFC9)

        elif command == "evoboxes":
            embed = discord.Embed(title="evoboxes <clanname>",
                                  description="shows highscore of most evolutional stone boxes opened.", color=0xFFAFC9)

        elif command == "exp":
            embed = discord.Embed(title="exp <clanname>", description="shows most total exp highscore of a clan.",
                                  color=0xFFAFC9)

        elif command == "fishing":
            embed = discord.Embed(title="fishing <clanname>",
                                  description="shows the fishing highscore, "
                                              "the players with the highest fishing level of a clan.",
                                  color=0xFFAFC9)

        elif command == "getplayer":
            embed = discord.Embed(title="getplayer <playername>", description="shows all highscores a player is in.",
                                  color=0xFFAFC9)

        elif command == "help":
            embed = discord.Embed(title="help <commandname(optional)>",
                                  description="shows the help message, with no commandname specified it sends all "
                                              "possible commands.",
                                  color=0xFFAFC9)

        elif command == "invitelink" or command == "invite":
            embed = discord.Embed(title="invite",
                                  description="gives a link to invite this bot, also gives a link to the supportserver."
                                  , color=0xFFAFC9)

        elif command == "playerconfig":
            embed = discord.Embed(title="playerconfig",
                                  description="With this command you can add players, remove players and show players."
                                              "After adding a player the player acts as if the player would be in a "
                                              "registered clan for your server. So it shows encounters, opened "
                                              "chests etc if those are registered for your server.")
        elif command == "links":
            embed = discord.Embed(title="links", description="gives some usefull links.", color=0xFFAFC9)

        elif command == "lle":
            embed = discord.Embed(title="lle <clanname>",
                                  description="Also known as highscore of shame. Shows the highscore of legendless "
                                              "encounters of a clan.",
                                  color=0xFFAFC9)

        elif command == "mapcontrol":
            embed = discord.Embed(title="mapcontrol <clanname(optional)>",
                                  description="Gives the top 9 of the 3 mapcontrol area's + the specified clan if there"
                                              " is 1.",
                                  color=0xFFAFC9)

        elif command == "mining":
            embed = discord.Embed(title="mining", description="gives the mining highscore of a clan.", color=0xFFAFC9)

        elif command == "mysteryboxes":
            embed = discord.Embed(title="mysteryboxes",
                                  description="shows the highscore of most mystery boxes opened of a clan.",
                                  color=0xFFAFC9)

        elif command == "pokeboxes":
            embed = discord.Embed(title="pokeboxes",
                                  description="shows the highscore of most pokemon boxes opened of a clan.",
                                  color=0xFFAFC9)

        elif command == "pp":
            embed = discord.Embed(title="pp <clanname>",
                                  description="shows the highscore of most philanthropist points of a clan. ",
                                  color=0xFFAFC9)

        elif command == "setdefault":
            embed = discord.Embed(title="setdefault <clanname>",
                                  description="sets a default for most commands that require a clan, "
                                              "so you don't have to type the clanname when doing the command."
                                              "If the clanname is not provided the default gets removed.",
                                  color=0xFFAFC9)

        elif command == "richestclans":
            embed = discord.Embed(title="richestclans <clanname(optional)>",
                                  description="gives the top 9 richest clans + the clanname specified if there is 1.",
                                  color=0xFFAFC9)

        elif command == "tmboxes":
            embed = discord.Embed(title="tmboxes <clanname>",
                                  description="shows the highscore of most tmboxes opened of a clan.", color=0xFFAFC9)

        elif command == "toprichest":
            embed = discord.Embed(title="toprichest <clanname>",
                                  description="shows the top richest players of a clan.",
                                  color=0xFFAFC9)

        elif command == "wbdmg":
            embed = discord.Embed(title="wbdmg <clanname>",
                                  description="shows the players that did the most worldboss damage of a clan.",
                                  color=0xFFAFC9)

        elif command == "weeklyexp":
            embed = discord.Embed(title="weeklyexp <clanname>",
                                  description="shows the highscore of weeklyexp of a clan.", color=0xFFAFC9)

        elif command == "worldboss":
            embed = discord.Embed(title="worldboss <playername>",
                                  description="Shows the world bosses a player participated in. "
                                              "Updates within 15 minutes after you refreshed. "
                                              "You must be within the top 1000 worldbossdamage highscore to be visible "
                                              "with this command.",
                                  color=0xFFAFC9)

        elif command == "getclan":
            embed = discord.Embed(title="getclan <clanname>",
                                  description="shows a collection of highscores a clan is in. containing: "
                                              "top richest clans, top exp clans and all map control areas.",
                                  color=0xFFAFC9)

        elif command == "getchests":
            embed = discord.Embed(title="getchests <parameter>",
                                  description="Shows the chests opened, you can select what you want the chests sorted"
                                              " by by clicking the buttons.", color=0xFFAFC9)
        elif command == "getencounters":
            embed = discord.Embed(title=f"{prefix}getencounters", description=f"{prefix}getencounters <name>",
                                  color=0xFF5733)

            embed.add_field(name="Use",
                            value="Shows you the pokemons encountered on that date, pokemons encountered by a specific "
                                  "player or a specific pokemon that has been captured by players.\n"
                                  "The bot has been keeping track since about 15 december 2020.")


        elif command == "worldbosstime":
            embed = discord.Embed(title=f"{prefix}worldbosstime",
                                  description=f"{prefix}worldbosstime")
            embed.add_field(name="Use",
                            value="gives the time untill the worldboss appears.")
        if embed is not None:
            await ctx.send(embed=embed)

    @commands.command(name="testcommand")
    async def testcommand(self, ctx):
        self.__generate_img(None)
        # embed = discord.Embed(title="[1] Lv 100 Manaphy", description='3000000')
        # #embed.
        # embed.add_field(name="stat", value="\n\n\n\n\nspeed", inline=True)
        # embed.add_field(name="base", value="hp: 300\natk: 310\ndef: 310\nspatk: 310\nspdef:310\nspeed:310", inline=True)
        # embed.add_field(name="iv's", value="31\n31\n31\n31\n31\n31", inline=True)
        # embed.add_field(name="ev's", value="131\n251\n31\n31\n31\n31", inline=True)
        #
        # await ctx.send(embed=embed)

    async def status_task(self):
        await self.client.wait_until_ready()
        while True:

            await self.client.change_presence(activity=
                                              discord.Activity(type=discord.ActivityType.watching, name="?about"))
            await asyncio.sleep(60)
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                        name=".help"))
            await asyncio.sleep(60)


class HelpCommand:
    def __init__(self):
        self.page = 1
        self.max_page = 11

    def change_page(self, movement, absolute=False):
        if absolute:
            newpage = movement
        else:
            newpage = self.page + movement
        if newpage > self.max_page:
            self.page = 1
        elif newpage < 1:
            self.page = self.max_page
        else:
            self.page = newpage
        return self.getembed()

    def getembed(self):
        if self.page == 1:
            embed = discord.Embed(title="Help", description='Channel Registrations', color=0xEE8700)
            embed.add_field(name=".register <event> <channel(optional>",
                            value="this will configure a channel so a message will be sent to that channel when "
                                  "that event happens. When the channel is not specified the channel where the "
                                  "command has been used is set.",
                            inline=False)
            embed.add_field(name=".unregister <event>",
                            value="this will remove the announcement of an event from a channel",
                            inline=False)
            embed.add_field(name=".registerclan <clanname>",
                            value="Registers a clan. "
                                  "This is needed if you want to make the bot announce encounters of your clan or "
                                  "announce if someone of your clan has beat the elite 4."
                                  "\nUse `.registerclan all` as clanname if you want to receive all encounters, elite 4"
                                  " messages etc.", inline=False)
            embed.add_field(name=".unregisterclan <clanname>",
                            value="Unregisters a clan, you will no longer receive encounters, "
                                  "elite4 etc for this clan.", inline=False)
            embed.add_field(name=".showclanregistrations",
                            value="shows the currently registered clans.", inline=False)
            embed.add_field(name=".showregistrations",
                            value="Shows you all registered channels in your server together with the time the message is allowed to be in the channel.",
                            inline=False)
            embed.add_field(name=".settime <event> <time>",
                            value="this will delete a specific event after a certain amount of time. Time is in minutes. If the time is not specified in the command, the message won't be removed from a channel anymore. this is the default.",
                            inline=False)
            embed.add_field(name=".setpingrole <eventname> <role>",
                            value="Please note that the bot needs the permission 'mention @ everyone, @ here and all roles' to be able to ping. Adds a role to ping for certain messages.",
                            inline=False)
            embed.add_field(name=".removeping <eventname>", value="Removes a role to ping for certain messages.",
                            inline=False)
            embed.add_field(name=".playerconfig", value="adds players as if they are in a registered clan.",
                            inline=False)
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 2:  # encounter queries
            embed = discord.Embed(title="Help", description='Encounter Queries', color=0xEE8700)
            embed.add_field(name=f".getrolls <parameter>", value="Gets the rolls of a player, a date or a pokemon."
                                                                 " Format of a date is yyyy-mm-dd")
            embed.add_field(name=".getencounters <name>",
                            value="Shows you the pokemons encountered on that date, pokemons encountered by a specific "
                                  "player or a specific pokemon that has been captured by players.",
                            inline=False)

            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 3:  # chest queries
            embed = discord.Embed(title="Help", description='Treasure Chest Queries', color=0xEE8700)
            embed.add_field(name=".getchests", value="Shows the chests opened, you can select what you want the "
                                                     "chests sorted by.",
                            inline=False)
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        # if self.page == 14:  # player queries
        #     embed = discord.Embed(title="Help", description='Player Queries', color=0xEE8700)
        #     embed.add_field(name=".compareplayers <player1> <player2> <mode>",
        #                     value="Compare 2 players' stats (encounters and chests). The mode is set to default all but you can change it with 'encounters' or 'chests'",
        #                     inline=False)
        #     embed.add_field(name=".getstats <name>",
        #                     value="gets your score based on encounters and chests, shiny common: 2 points, shiny uncommon: 3 points, shiny rare: 6 points, legendary: 8 points, shiny very rare: 12 points, shiny extremely rare: 20 points, shiny legendary: 40 points",
        #                     inline=False)
        #     embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 5:
            embed = discord.Embed(title="Help", description='Permission Commands', color=0xEE8700)
            embed.add_field(name=".getperms",
                            value="Shows what roles have permissions to adjust settings for eventconfigurations.",
                            inline=False)
            embed.add_field(name=".setperms @Role",
                            value="This gives permissions to the specified role to adjust eventconfigurations for this server.",
                            inline=False)
            embed.add_field(name=".removeperms @role",
                            value="Removes the permissions for the specified role to adjust eventconfigurations for this server.")
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 6:
            embed = discord.Embed(title="Help", description='Pm Notification Settings', color=0xEE8700)
            embed.add_field(name=".pmgoldrush <location>", value="Gives you a pm a goldrush happens at a location"
                                                                 " you registered for.", inline=False)
            embed.add_field(name=".pmhoney <location>", value="Gives you a pm if honey gets spread at a location "
                                                              "you registered for.", inline=False)
            embed.add_field(name=".pmworldboss", value="begins the setup for pming a worldboss to you. This can be "
                                                       "a worldboss pokemon, worldboss location or a combination of"
                                                       " both.", inline=False)
            embed.add_field(name=".pmswarm", value="begins the setup for pming a swarm to you. This can be pokemon,"
                                                   " a swarm location or a combination of both.", inline=False)
            embed.add_field(name=".pmtournament", value="begins the setup for pming a tournament to you. This can "
                                                        "be done by tournament type, tournament prize or a "
                                                        "combination of both.", inline=False)
            embed.add_field(name=".removepmconfig", value="Shows an optionmenu to removes pm configuration for events.",
                            inline=False)
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 7:
            embed = discord.Embed(title="Help", description='Highscores Commands', color=0xEE8700)
            embed.add_field(name=".top <clanname(optional)>",
                            value="shows top 9 from a highscore (+ clan if specified or registered)", inline=False)
            embed.add_field(name=".achievements <clanname>",
                            value="shows achievements highscore of a clan. This highscore usually is max 13 hours old",
                            inline=False)
            embed.add_field(name=".bestclans <clanname(optional)>", value="shows top 9 of most exp of a clan",
                            inline=False)
            embed.add_field(name=".btwins <clanname>",
                            value="shows the highscore of the most battletower wins of a clan", inline=False)
            embed.add_field(name=".btwinstreak <clanname>", value="shows top battletower winstreak of a clan",
                            inline=False)
            embed.add_field(name=".clanlist <clanname>", value="gives a clanlist of the clan specified",
                            inline=False)
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 8:
            embed = discord.Embed(title="Help", description='Highscores Commands', color=0xEE8700)
            embed.add_field(name=".cwplayers <clanname>", value="shows top clan war players of a clan",
                            inline=False)
            embed.add_field(name=".cwwins <clanname>", value="shows top clan war wins of a clan", inline=False)
            embed.add_field(name=".dex <clanname>",
                            value="shows the highscore of the most pokemon caught of a clan", inline=False)
            embed.add_field(name=".evoboxes <clanname>",
                            value="shows highscore of most evolutional stone boxes opened", inline=False)
            embed.add_field(name=".exp <clanname>", value="shows most total exp highscore of a clan", inline=False)
            embed.add_field(name=".fishing <clanname>",
                            value="shows the fishing highscore, the players with the highest fishing level of a clan",
                            inline=False)
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 9:
            embed = discord.Embed(title="Help", description='Highscores Commands', color=0xEE8700)
            embed.add_field(name=".getplayer <playername>", value="shows all highscores a player is in",
                            inline=False)
            embed.add_field(name=".lle <clanname>",
                            value="Also known as highscore of shame. Shows the highscore of legendless encounters of a clan",
                            inline=False)
            embed.add_field(name=".mapcontrol <clanname(optional)>",
                            value="Gives the top 9 of the 3 mapcontrol area's + the specified clan if there is 1",
                            inline=False)
            embed.add_field(name=".mining", value="gives the mining highscore of a clan", inline=False)
            embed.add_field(name=".mysteryboxes",
                            value="shows the highscore of most mystery boxes opened of a clan", inline=False)
            embed.add_field(name=".pokeboxes", value="shows the highscore of most pokemon boxes opened of a clan",
                            inline=False)
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 10:
            embed = discord.Embed(title="Help", description='Highscores Commands', color=0xEE8700)
            embed.add_field(name=".pp <clanname>",
                            value="shows the highscore of most philanthropist points of a clan. This highscore usually is max 13 hours old",
                            inline=False)
            embed.add_field(name=".richestclans <clanname(optional)>",
                            value="gives the top 9 richest clans + the clanname specified if there is 1",
                            inline=False)
            embed.add_field(name=".tmboxes <clanname>",
                            value="shows the highscore of most tmboxes opened of a clan", inline=False)
            embed.add_field(name=".toprichest <clanname>", value="shows the top richest players of a clan",
                            inline=False)
            embed.add_field(name=".setdefault <clanname>",
                            value="sets a default clanname for highscores commands. When no clan is provided "
                                  "it removes the default.", inline=False)
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 11:
            embed = discord.Embed(title="Help", description='Highscores Commands', color=0xEE8700)
            embed.add_field(name=".wbdmg <clanname>",
                            value="shows the players that did the most worldboss damage of a clan", inline=False)
            embed.add_field(name=".weeklyexp <clanname>", value="shows the highscore of weeklyexp of a clan",
                            inline=False)
            embed.add_field(name=".worldboss <playername>",
                            value="Shows the world bosses a player participated in. Within 15 minutes to update",
                            inline=False)
            embed.add_field(name=".getclan <clanname>",
                            value="shows a collection of highscores a clan is in. containing: top richest clans, top exp clans and all map control areas",
                            inline=False)
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        if self.page == 4:
            embed = discord.Embed(title="Help", description='Other Commands', color=0xEE8700)
            embed.add_field(name=".worldbosstime", value="Shows time left for World Boss to spawn", inline=False)
            embed.add_field(name=".invite", value="Sends you the invite link for our bot.", inline=False)
            embed.set_footer(text="Page {} of {}".format(str(self.page), str(self.max_page)))

        return embed


def setup(client):

    client.remove_command('help')
    client.add_cog(Miscellaneous(client))
