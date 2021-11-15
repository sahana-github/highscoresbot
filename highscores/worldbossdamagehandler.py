import sqlite3

from highscores import WorldbossDamage
from pathmanager import PathManager


query = "CREATE TABLE worldboss_dmg(worldbossid INTEGER, playername TEXT, damage INTEGER, " \
        "PRIMARY KEY(worldbossid, playername))"





another = "CREATE TABLE playerdmg(playername TEXT PRIMARY KEY, damage INTEGER, adjusted INTEGER);"
"""
STEPS TO PERFORM WHEN ENTERING WORLDBOSS DATA.
#1 worldboss is added to the data table, adding a new worldboss id.
#2 all damage within top 1000 gets updated. 
If the damage is not equal to the previous damage add the player to that worldboss.

"""
class WorldbossDamageHandler:
    def __init__(self):
        self.worldbossid = self.getLatestWorldbossId()
        self.result = []

    def getLatestWorldbossId(self):
        dataconn = sqlite3.connect(PathManager().getpath("data.db"))
        try:
            datacur = dataconn.cursor()
            return datacur.execute("SELECT id FROM worldboss ORDER BY id DESC LIMIT 1").fetchall()[0][0]
        finally:
            dataconn.close()

    def update(self):
        """
        does the following:
        #1 sets the adjusted worldbossid to the then previous worldbossid if a new world boss got entered.
        #2 enters new record for players who have more than 0 damage on the worldboss, based on worldbossdmg table
        of highscores database and previous damage, which is in the playerdmg database. Also sets the adjusted integer
        to the current worldbossid when a record got added to the worldbossdmg table.
        #3
        """
        dataconn = sqlite3.connect(PathManager().getpath("data.db"))
        datacur = dataconn.cursor()
        if self.worldbossid != self.getLatestWorldbossId():
            self.__finalizedmg()

        self.result = WorldbossDamage().getDbValues()
        for _, username, _, total_damage in self.result:
            if old_dmg := self.__getTotalDamage(username, self.worldbossid-1):
                pass
            else:
                # the player was not in the playerdmg table last worldboss.
                if not self.__playerExists(username):
                    # the player has never been in the playerdmg table before.
                    datacur.execute("INSERT INTO playerdmg(playername, damage, adjusted) VALUES(?,?,?)",
                                    (username, total_damage, self.worldbossid))
                else:
                    # the player has been in the playerdmg table in the past, but disappeared for a while.
                    # Just updating adjusted id.
                    datacur.execute("UPDATE playerdmg SET adjusted=?, damage=? WHERE playername=?",
                                    (self.worldbossid, total_damage, username))
                dataconn.commit()
                continue

            total_damage = int(total_damage)
            if total_damage - old_dmg != 0:
                # damage changed.
                self.__enterworldboss(self.worldbossid, username, total_damage-old_dmg, total_damage)

    def __getTotalDamage(self, playername, id=None):
        dataconn = sqlite3.connect(PathManager().getpath("data.db"))
        datacur = dataconn.cursor()
        if id is not None:
            datacur.execute("SELECT damage FROM playerdmg WHERE playername=? AND adjusted=?",
                            (playername, id))
        else:
            datacur.execute("SELECT damage FROM playerdmg WHERE playername=?", (playername,))
        if result := datacur.fetchall():
            return result[0][0]
        return None

    def __playerExists(self, username):
        dataconn = sqlite3.connect(PathManager().getpath("data.db"))
        datacur = dataconn.cursor()
        datacur.execute("SELECT damage FROM playerdmg WHERE playername=?", (username,))
        return bool(datacur.fetchall())

    def __enterworldboss(self, worldbossid, playername, damage, new_total_dmg=None):
        dataconn = sqlite3.connect(PathManager().getpath("data.db"))
        datacur = dataconn.cursor()
        datacur.execute("INSERT INTO worldboss_dmg(worldbossid, playername, damage) VALUES(?,?,?)",
                        (worldbossid, playername, damage))
        if new_total_dmg is not None:
            datacur.execute("UPDATE playerdmg SET adjusted=?, damage=? WHERE playername=?",
                            (worldbossid, new_total_dmg, playername))
        dataconn.commit()

    def __finalizedmg(self):
        """
        sets all visible playerid's to self.worldbossid, before updating self.worldbossid to the latest worldboss id.
        :return:
        """
        dataconn = sqlite3.connect(PathManager().getpath("data.db"))
        datacur = dataconn.cursor()
        # finalize the latest damage.
        for _, username, _, _ in self.result:
            datacur.execute("UPDATE playerdmg SET adjusted=? WHERE playername=?", (self.worldbossid, username))
            dataconn.commit()
        self.worldbossid = self.getLatestWorldbossId()
