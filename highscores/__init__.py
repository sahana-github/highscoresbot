from typing import Union, List

from .achievements import Achievements
from .ancmapcontrol import AncMapcontrol
from .bestclans import BestClans
from .btwins import Btwins
from .btwinstreak import Btwinstreak
from .bzmapcontrol import BzMapcontrol
from .cwplayers import Cwplayers
from .cwwins import Cwwins
from .dex import Dex
from .evoboxes import EvoBoxes
from .exp import Exp
from .fishing import Fishing
from .lle import Lle
from .mining import Mining
from .mysteryboxes import MysteryBoxes
from .philanthropist import Philanthropist
from .pokeboxes import PokeBoxes
from .richest import Richest
from .richestclans import RichestClans
from .safarimapcontrol import SafariMapcontrol
from .tmboxes import TmBoxes
from .weeklyexp import Weeklyexp
from .worldbossdamage import WorldbossDamage
from .mostgifts import MostGifts

allhighscores = [Achievements, AncMapcontrol, BestClans, Btwins, Btwinstreak, BzMapcontrol, Cwplayers, Cwwins,
           Dex, EvoBoxes, Exp, Fishing, Lle, Mining, MysteryBoxes, Philanthropist, PokeBoxes, Richest, RichestClans,
           SafariMapcontrol, TmBoxes, Weeklyexp, WorldbossDamage, MostGifts]

clanhighscores = [Achievements, Cwplayers, Cwwins, Dex, EvoBoxes, Exp, Fishing, Lle, Mining, MysteryBoxes, Philanthropist,
                PokeBoxes, Richest, TmBoxes, Weeklyexp, WorldbossDamage, MostGifts]


def getPlayerClan(playername: str) -> Union[str, None]:
    """
    gets the clan of a player.
    :param playername: the name of the player to get the clan from.
    :return: the clan of the player(can be empty string) or None if the player is not found at all.
    """
    for highscore in clanhighscores:
        highscore = highscore()
        result = highscore.getDbValues(f"SELECT clan FROM {highscore.NAME} WHERE username=?", params=[playername.lower()])
        if result:
            return result[0][0]
    return None


def getClanList(clanname: str) -> List[str]:
    clanlist = []
    for highscore in clanhighscores:
        highscore = highscore()
        result = highscore.getDbValues(query=f"SELECT username FROM {highscore.NAME} WHERE clan=?", clan=clanname)
        for row in result:
            if row[0] not in clanlist:
                clanlist.append(row[0])
    return clanlist

__all__ = ["Achievements", "AncMapcontrol", "BestClans", "Btwins", "Btwinstreak", "BzMapcontrol", "Cwplayers", "Cwwins",
           "Dex", "EvoBoxes", "Exp", "Fishing", "Lle", "Mining", "MysteryBoxes", "Philanthropist", "PokeBoxes",
           "Richest", "RichestClans", "SafariMapcontrol", "TmBoxes", "Weeklyexp", "WorldbossDamage", "allhighscores",
           "clanhighscores", "getClanList", "getPlayerClan", "MostGifts"]
