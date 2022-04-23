import sqlite3

from discord import Interaction

from commands.interractions.highscore_command import HighscoreCommand
from commands.interractions.resultmessageshower import ResultmessageShower
from commands.interractions.selectsview import SelectsView
from commands.interractions.top_command import TopCommand
from commands.sendable import Sendable
from commands.utils.utils import joinmessages, tablify
from highscores import allhighscores, AncMapcontrol, BzMapcontrol, BestClans, RichestClans, SafariMapcontrol


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