import time
from highscores import *
from highscores.highscore import Highscore
from highscores.worldbossdamagehandler import WorldbossDamageHandler
from ppowebsession import PpoWebSession
import os
import datetime
from commands.utils.utils import getworldbosstime
from highscores.mostgifts import MostGifts

class HighscoresUpdater:
    def __init__(self, websession: PpoWebSession, debug=True, timeout=600):
        # @todo make it survive connection issues.
        self.__ppowebsession: PpoWebSession = websession
        self.DEBUG = debug
        self.timeout = timeout
        self.worldbossDamageHandler = WorldbossDamageHandler()

    def updateHighscores(self):
        if self.DEBUG:
            print(f"starting update at {datetime.datetime.now()}")
        for i in allhighscores:
            highscore: Highscore = i()
            try:
                self.makeBackup(highscore)
            except Exception as e:
                print(e)

        if self.DEBUG:
            print(f"update done at {datetime.datetime.now()}")

    def makeBackup(self, highscore: Highscore):
        exceptionhappened = False
        while True:
            try:
                if exceptionhappened:
                    self.__ppowebsession.login()
                highscore.updatetable(self.__ppowebsession)
                if type(highscore) == WorldbossDamage and getworldbosstime() >= datetime.datetime.now():
                    self.worldbossDamageHandler.update()
                elif type(highscore) == WorldbossDamage:
                    print("NOT UPDATING worldbossDamage, possible crash!!")
                if self.DEBUG:
                    print("updated highscore", highscore.NAME, f"at {datetime.datetime.now()}")
                break
            except Exception as e:
                print(e)
                exceptionhappened = True
                time.sleep(self.timeout)

    @staticmethod
    def makeHighscores(path: str):
        for i in allhighscores:
            highscore: Highscore = i()
            highscore.create(path)


if __name__ == "__main__":

    websession = PpoWebSession(os.environ.get("username"), os.environ.get("password"), 4)
    websession.login()
    updater = HighscoresUpdater(websession)
    updater.makeHighscores("highscores.db")

    while True:
        updater.updateHighscores()
