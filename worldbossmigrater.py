import sqlite3

from highscores import WorldbossDamage
from highscores.worldbossdamagehandler import WorldbossDamageHandler


class WorldbossMigrater:
    def __init__(self):
        self.worldbossDamage = WorldbossDamage()
        self.damageHandler = WorldbossDamageHandler()
        self.__removeWorldbosses()
        self.worldbosses = []

    def __removeWorldbosses(self):
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM worldboss WHERE 1=1")
        conn.commit()
        conn.close()

    def addworldboss(self, id, name, date):
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO worldboss(id, worldbossname, date) VALUES(?,?,?)", (id, name, date))
        conn.commit()
        conn.close()

    def migrate(self):
        for id, name, date in self.worldbosses:
            print(id, name, date)
            self.addworldboss(id, name, date)
            print("added worldboss.")
            self.updateHighscore(id)
            print("updated highscore.")
            self.damageHandler.update()
            print("damagehandler done.")

    def updateHighscore(self, id):
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        cur.execute("SELECT id, playername, totaldamage FROM worldbossdmg WHERE worldbossint=?", (id,))
        for rank, playername, totaldamage in cur.fetchall():
            if rank % 1000 == 0:
                rank = 1000
            else:
                rank = rank % 1000

            self.worldbossDamage.insert([rank, playername, "tempclan", totaldamage])



if __name__ == "__main__":
    migrater = WorldbossMigrater()
    migrater.migrate()
