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

allhighscores = [Achievements, AncMapcontrol, BestClans, Btwins, Btwinstreak, BzMapcontrol, Cwplayers, Cwwins,
           Dex, EvoBoxes, Exp, Fishing, Lle, Mining, MysteryBoxes, Philanthropist, PokeBoxes, Richest, RichestClans,
           SafariMapcontrol, TmBoxes, Weeklyexp, WorldbossDamage]

__all__ = ["Achievements", "AncMapcontrol", "BestClans", "Btwins", "Btwinstreak", "BzMapcontrol", "Cwplayers", "Cwwins",
           "Dex", "EvoBoxes", "Exp", "Fishing", "Lle", "Mining", "MysteryBoxes", "Philanthropist", "PokeBoxes",
           "Richest", "RichestClans", "SafariMapcontrol", "TmBoxes", "Weeklyexp", "WorldbossDamage", "allhighscores"]
