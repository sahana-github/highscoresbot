from highscores import *
from highscores.highscore import Highscore
from ppowebsession import PpoWebSession
import os
import datetime


class HighscoresUpdater:
    def __init__(self, websession: PpoWebSession, debug=True):
        # @todo make it survive connection issues.
        self.__ppowebsession: PpoWebSession = websession
        self.DEBUG = debug

    def updateHighscores(self):
        if self.DEBUG:
            print(f"starting update at {datetime.datetime.now()}")
        for i in allhighscores:
            highscore: Highscore = i()
            self.makeBackup(highscore)
        if self.DEBUG:
            print(f"update done at {datetime.datetime.now()}")

    def makeBackup(self, highscore: Highscore):
        highscore.updatetable(self.__ppowebsession)
        if self.DEBUG:
            print("updated highscore", highscore.NAME, f"at {datetime.datetime.now()}")

    def makeHighscores(self, path: str):
        for i in allhighscores:
            highscore: Highscore = i()
            highscore.create(path)


if __name__ == "__main__":
    websession = PpoWebSession(os.environ.get("username"), os.environ.get("password"), 5)
    websession.login()
    updater = HighscoresUpdater(websession)
    #updater.makehighscores("main.db")
    updater.updateHighscores()
