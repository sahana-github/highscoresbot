import asyncio
import datetime
import json
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import discord
from commands.interractions.miscellaneous.gmsearch import ImgWithText, GMSearch
from commands.interractions.miscellaneous.help_cmd import HelpCmd
from commands.interractions.resultmessageshower import ResultmessageShower
from commands.interractions.selectsview import SelectsView
from commands.sendable import Sendable
from commands.utils.utils import tablify
from highscores import getClanList
from pathmanager import PathManager
from ppobyter.marketplace.item import Item
from ppobyter.marketplace.pokemon import Pokemon


def __generate_img(pokemon: Pokemon):
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
        sprite = sprite.resize((200, 200))
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
            helditem = Image.open(r"sprites/items/" + str(pokemon.helditem.lower()).replace(" ", "-") + ".png")
            helditem = helditem.resize((46, 44))
            img.paste(helditem, (22, 470))
        except Exception as e:
            print(f"exception when adding held item. Held item: {pokemon.helditem}", e)
    return img


async def clanlist(sendable: Sendable, clanname: str):
    """
    gives a list of players that are in the provided clan.
    :param ctx: discord context
    :param clanname: the name of the clan you want the clanlist from.
    """
    clanname = clanname.lower()
    result = getClanList(clanname)
    result.sort()
    if result:
        await sendable.send(f"clanlist of {clanname}: \n" + ", ".join(result))
    else:
        await sendable.send("no results found for that clanname.")


async def invite(sendable: Sendable):
    invitelink = "https://discord.com/login?redirect_to=" \
            "%2Foauth2%2Fauthorize%3Fclient_id%3D733434249771745401%26permissions%3D2048%26redirect_uri" \
            "%3Dhttps%253A%252F%252Fdiscordapp.com%252Foauth2%252Fauthorize%253F%2526" \
            "permissions%253D141312%2526client_id%253D733434249771745401%2526scope%253Dbot%26scope%3Dbot"
    embed = discord.Embed()
    embed.description = "this is the [invite link]" \
                        "({})" \
                        "\n also join the [support server](https://discord.gg/PmXY35aqgH)".format(invitelink)

    await sendable.send(embed=embed)


async def setdefault(sendable: Sendable, clanname: str=None):
    """
    sets a default for the highscores commands. If the clanname is not provided the default will be removed.
    :param ctx: discord context
    :param clanname: the clan you want to set as default for the highscores commands.
    """
    clanname = clanname.lower()
    if sendable.guild is None:
        await sendable.send("this command can't be used in pm.")
        return
    if not sendable.user.guild_permissions.administrator:
        await sendable.send(
            "insufficient permissions to use this command. Ask a server administrator!")
        return
    id = sendable.guild.id
    conn = sqlite3.connect("highscores.db")
    cur = conn.cursor()
    if clanname is not None:
        try:
            cur.execute("INSERT INTO clannames(id, name) VALUES(?,?)", (id, clanname))
        except sqlite3.IntegrityError:
            cur.execute("UPDATE clannames SET name=? WHERE id=?", (clanname, id))
        msg = await sendable.send(f"{clanname} registered as default!")
    else:
        cur.execute("UPDATE clannames SET name = NULL WHERE id=?", (id,))
        msg = await sendable.send("default has been removed!")
    try:
        conn.commit()
    except Exception as e:
        print(e)
        await msg.delete()
        await sendable.send("Something went wrong. Developer is informed.")
        raise e

async def worldboss(sendable: Sendable, playername: str):
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
    conn = sqlite3.connect(PathManager().getpath("data.db"))
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
    messageshower = ResultmessageShower(messages, sendable)
    await sendable.send(f"page {messageshower.currentpage} of {messageshower.maxpage}" +
                   messages[messageshower.currentpage-1], view=messageshower)


async def gmsearch(sendable: Sendable, searchstring: str):
    if len(searchstring) > 80:
        await sendable.send("the max length for the item to search for is 80 characters!")
        return
    if not searchstring:
        await sendable.send("use .gmsearch manaphy for example, where manaphy is the pokemon you search for.")
        return
    await sendable.send("queued up for gm search.")
    if sendable.guild is None:
        # is pm
        ispm = 1
        fetchid = sendable.user.id
    else:
        ispm = 0
        # is guild
        fetchid = sendable.channel.id
    conn = sqlite3.connect("eventconfigurations.db")
    cur = conn.cursor()
    result = cur.execute("INSERT INTO gmsearch(msgid, fetchid, isdm, searchstring, timestamp) VALUES(?,?,?,?,?)",
                (None, fetchid, ispm, searchstring, int(datetime.datetime.now().timestamp())))
    conn.commit()

    for i in range(500):
        await asyncio.sleep(5)
        cur.execute("SELECT page, content FROM gmsearchresult WHERE responseid=?", (result.lastrowid,))
        if gmsearches := cur.fetchall():
            print("results are in!")
            break
    else:
        await sendable.send("something broke. This will be resolved soon.")
        raise TimeoutError("Gmsearch failed! No results incomming.")
    pages = []
    if gmsearches[0][1] is None:
        if sendable.channel is not None:
            await sendable.channel.send("the search didn't return any items/pokemon!")
        else:
            await sendable.user.send("the search didn't return any items/pokemon!")
        return
    for row in gmsearches:
        item = Item.from_dict(dict(json.loads(row[1].replace("'", '"'))))
        embed = discord.Embed(title=item.itemname,
                              description=f"amount: {item.amount}")
        embed.add_field(name="price", value=item.price)
        embed.add_field(name="seller", value=item.seller)

        if item.isPokemon():
            def generate_img(pokemon):
                return lambda: __generate_img(pokemon)
            img = generate_img(item.pokemon)
        else:
            try:
                img = Image.open(r"sprites/items/" + str(item.itemname.lower()).replace(" ", "-") + ".png")
            except Exception as e:
                print(f"failed to load img for item: {item.itemname}", e)
                img = None
        pages.append(ImgWithText(img, embed))

    view = GMSearch(sendable, messages=pages)
    await view.initial_send()


async def help(sendable: Sendable):
    """
    This shows help on the commands.
    :param ctx: discord context
    :param command: the name of the command you want to see the help message from.
    """
    conn = sqlite3.connect("eventconfigurations.db")
    cur = conn.cursor()
    cur.execute("SELECT helpcategories.name, helpcommands.commandname, helpcommands.embed "
                "FROM helpcommands LEFT OUTER JOIN helpcategories ON helpcommands.category = helpcategories.id")
    result = cur.fetchall()
    conn.close()

    labels = []
    for row in result:
        label = row[1]
        if row[0] is not None:
            label += f" ({row[0]})"
        labels.append(label)
    view = SelectsView(sendable, labels, lambda options: HelpCmd(sendable, options))
    embed = discord.Embed(title="about", description="donations, source code")
    embed.add_field(name="Donations",
                    value="Highscores bot costs 49 usd to keep operational every month, which means highscores bot has cost 882 usd in total so far, without any compensation. Please consider [donating](https://www.patreon.com/highscores_bot) to keep highscores bot operational!")
    embed.add_field(name="source code",
                    value="highscores bot is open source! view the source code on [github](https://github.com/graatje/highscoresbot)")
    await sendable.send(embed=embed)
    await sendable.send("Select the command(s) you need help with! Commands are sorted by category.", view=view)
