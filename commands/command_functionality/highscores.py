import sqlite3
from typing import Union, List

from discord import User
from discord.ext import commands
from discord.ext.commands import Command

from commands.interractions.highscore_command import HighscoreCommand
from commands.interractions.resultmessageshower import ResultmessageShower
from commands.interractions.selectsview import SelectsView
from commands.interractions.top_command import TopCommand
from commands.sendable import Sendable
from commands.utils.utils import joinmessages, tablify
from highscores import allhighscores, AncMapcontrol, BzMapcontrol, BestClans, RichestClans, SafariMapcontrol, \
    clanhighscores
from highscores.highscore import Highscore


async def getdefaultclanname(interaction, comment=True) -> Union[str, None]:
    if interaction.guild is None:
        return
    conn = sqlite3.connect("highscores.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM clannames WHERE id=?", (interaction.guild.id,))
    try:
        clanname = cur.fetchall()[0][0]
    except IndexError:
        clanname = None
    if clanname is None and comment:
        await interaction.response.send_message("Please register a default clanname or provide a clan in the command.")
    elif clanname is not None:
        clanname = clanname.lower()
    return clanname


async def getplayer(sendable: Sendable, username: str):
    """
    gets a collection of highscores a player is in.
    :param ctx: discord context
    :param username: the name of the player you want info from.
    """
    username = username.lower()
    allmessages = []
    for highscore in allhighscores:
        highscore = highscore()
        try:
            values = highscore.getDbValues(query="SELECT * FROM {0} WHERE username=?".format(highscore.NAME),
                                           params=[username])
            if (newmessages := tablify(highscore.LAYOUT, values))[0] != "No results found.":
                allmessages += newmessages
        except sqlite3.OperationalError:
            pass

    allmessages = joinmessages(allmessages)

    if len(allmessages) == 0:
        await sendable.send("or {0} is not in any highscore or he does not exist.".format(username))
    else:
        view = ResultmessageShower(allmessages, sendable)
        await sendable.send(allmessages[0], view=view)


async def getclan(sendable: Sendable, clanname: str):
    clanname = clanname.lower()
    getclanhighscores = [(SafariMapcontrol, "Safari zone mapcontrol"),
                         (AncMapcontrol, "Ancient cave mapcontrol"),
                         (BzMapcontrol, "Battle zone mapcontrol"),
                         (BestClans, "Top clan experience"),
                         (RichestClans, "Top richest clans")]
    allmessages = []
    for highscore, name in getclanhighscores:
        highscore = highscore()
        values = highscore.getDbValues(f"SELECT * FROM {highscore.NAME}")
        for i in values:
            if i[1] == clanname:
                allmessages.append(name)
                allmessages += tablify(highscore.LAYOUT, [i])
                break
    allmessages = joinmessages(allmessages)
    if not allmessages:
        await sendable.send(f"The clan {clanname} is not in the highscores or does not exist.")
        return

    view = ResultmessageShower(allmessages, sendable)
    await sendable.send(allmessages[0], view=view)


async def top(sendable: Sendable, clanname: str=None):
    """
    shows top 9 + the provided clan if available.
    :param ctx: discord context
    :param clanname: the clanname, default none, clannamehandler gets clan from db if none.
    """
    highscoresdict = {}
    for highscore in allhighscores:
        highscore = highscore()
        highscoresdict[highscore.NAME] = highscore

    def highscoreselectionmaker(highscores):
        return TopCommand(sendable, highscores, clanname)

    view = SelectsView(sendable, highscoresdict, highscoreselectionmaker)
    await sendable.send(content=f"page {view.currentpage} of {view.maxpage}", view=view)


async def highscore(sendable: Sendable, clanname: str=None):
    initializedhighscores = {}
    for highscore in allhighscores:
        highscore = highscore()
        initializedhighscores[highscore.NAME] = highscore

    def highscoreselectionmaker(highscores):
        return HighscoreCommand(sendable, highscores, clanname=clanname)

    view = SelectsView(sendable, initializedhighscores.keys(), highscoreselectionmaker)
    await sendable.send(content=f"page {view.currentpage} of {view.maxpage}", view=view)


async def mapcontrol(sendable: Sendable, clanname: str=None):
    """
    shows the standings of all mapcontrol areas.
    :param ctx: discord context
    :param clanname: the name of the clan, optional.
    """
    mapcontrolhighscores = [(AncMapcontrol, "Ancient cave"), (BzMapcontrol, "Battle zone"),
                            (SafariMapcontrol, "Safari zone")]
    if clanname is None:
        clanname = ""
    messages = []
    for highscore, area in mapcontrolhighscores:
        highscore = highscore()
        values = tablify(highscore.LAYOUT, highscore.getDbValues(
            query=f"SELECT * FROM {highscore.NAME} WHERE rank < 10 or clan=?",
            clan=clanname.lower()))
        messages.append(area)
        messages += values
    messages = joinmessages(messages)
    view = ResultmessageShower(messages, sendable)
    await sendable.send(messages[0], view=view)


def get_clancommands():
    clancmds = {}
    for highscore in clanhighscores:
        highscore = highscore()

        def outer_cmd(score: Highscore) -> Command:
            async def cmd(sendable: Sendable, clanname=None):
                if clanname is None and ((clanname := await getdefaultclanname(sendable)) is None):
                    return
                messages = tablify(score.LAYOUT, score.getDbValues(clan=clanname.lower()))
                for i in messages:
                    await sendable.send(i)

            return cmd

        clancmds[highscore.NAME] = outer_cmd(highscore)
    return clancmds


def get_top10cmds():
    top10cmds = {}
    somelist = [RichestClans, BestClans]
    for highscore in somelist:
        highscore = highscore()
        def outer_cmd(score: Highscore):
            async def cmd(ctx, clanname=None):
                if clanname is None and ((clanname := await getdefaultclanname(ctx, comment=False)) is None):
                    clanname = ""
                values = score.getDbValues(query="SELECT * FROM {0} WHERE rank < 10 or name = ?".format(score.NAME),
                                           clan=clanname.lower())
                resultmessages = tablify(score.LAYOUT, values)
                for i in resultmessages:
                    await ctx.send(i)

            return cmd
        top10cmds[highscore.NAME] = outer_cmd(highscore)
    return top10cmds

