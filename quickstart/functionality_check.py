import sqlite3

from pathmanager import PathManager
import highscores


class Functionality:
    def __init__(self, succes: bool, msg="", recommended_fix=None):
        self.SUCCES = succes
        self.MSG = msg
        self.RECOMMENDED_FIX = recommended_fix

    def fix(self):
        if self.RECOMMENDED_FIX is not None:
            self.RECOMMENDED_FIX()

    def hasFix(self):
        return self.RECOMMENDED_FIX is not None

    def __bool__(self):
        return self.SUCCES

    def __str__(self):
        return self.MSG


class FunctionalityCheck:
    def __init__(self):
        self.pathManager = PathManager()

    def checkHighscoreFunctionality(self) -> Functionality:
        try:
            open(self.pathManager.getpath("highscores.db"))
        except (KeyError, FileNotFoundError):
            return Functionality(False, "highscores database does not exist.")

        try:
            conn = sqlite3.connect(self.pathManager.getpath("highscores.db"))

        except Exception as e:
            return Functionality(False, str(e))
        finally:
            conn.close()

        for highscore in highscores.allhighscores:
            highscore = highscore()
            try:
                vals = highscore.getDbValues()
                if not vals:
                    raise ValueError(f"database created but is not initialized with values for {highscore.NAME}")
            except sqlite3.OperationalError:
                return Functionality(False, f"highscore {highscore.NAME} does not exist!!",
                                     lambda: highscore.create(self.pathManager.getpath("highscores.db")))
            except ValueError as e:
                return Functionality(False, str(e.args[0]),
                                     lambda: highscore.create(self.pathManager.getpath("highscores.db")))

        return Functionality(True, "succes!")



if __name__ == "__main__":
    f = FunctionalityCheck()
    while not (d := f.checkHighscoreFunctionality()) and d.hasFix():
        print(d)
        d.fix()