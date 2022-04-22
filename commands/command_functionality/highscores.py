import sqlite3

from commands.interractions.resultmessageshower import ResultmessageShower
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
