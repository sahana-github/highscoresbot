from highscores import *
from highscores.highscore import Highscore
from ppowebsession import PpoWebSession
import os


class HighscoresUpdater:
    def __init__(self, websession: PpoWebSession):
        self.__ppowebsession: PpoWebSession = websession

    def makebackup(self):
        for i in allhighscores:
            highscore: Highscore = i()
            highscore.updatetable(self.__ppowebsession)
            print("updated highscore", str(type(highscore)))

    def makehighscores(self, path: str):
        for i in allhighscores:
            highscore: Highscore = i()
            highscore.create(path)


if __name__ == "__main__":
    websession = PpoWebSession(os.environ.get("username"), os.environ.get("password"), 5)
    websession.login()
    updater = HighscoresUpdater(websession)
    #updater.makehighscores("main.db")
    updater.makebackup()
