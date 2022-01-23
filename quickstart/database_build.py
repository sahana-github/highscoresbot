import sqlite3

from highscoresupdater import HighscoresUpdater
from pathmanager import PathManager


class DatabaseBuild:
    def __init__(self):
        self.pathManager = PathManager()

    def highscoresDatabase(self):
        """
        tables needed for the highscores database.
        """
        HighscoresUpdater.makeHighscores(self.pathManager.getpath("highscores.db"))
        conn = sqlite3.connect(self.pathManager.getpath("highscores.db"))
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS clannames (id INTEGER, name TEXT, command_prefix TEXT, PRIMARY KEY(id))")
        conn.commit()
        conn.close()

    def ingame_data(self):
        """
        database for encounters, chests, rolls
        """
        conn = sqlite3.connect(self.pathManager.getpath("ingame_data.db"))
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Encounters (Name STRING DEFAULT None, Encounters STRING DEFAULT None, Date STRING, Id INTEGER PRIMARY KEY AUTOINCREMENT)")
        cur.execute("CREATE TABLE IF NOT EXISTS chests(id INTEGER PRIMARY KEY AUTOINCREMENT, location TEXT, player TEXT, date TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS rolls(id INTEGER PRIMARY KEY AUTOINCREMENT, player TEXT, pokemon TEXT, date TEXT)")
        conn.commit()
        conn.close()

    def data(self):
        """
        data database. Contains worldboss damage by players, and next to that data that has not directly has anything to
        do with players themselves. (example a table of locations where honey has been spread, table of tournament
        prizes)
        """
        conn = sqlite3.connect(self.pathManager.getpath("data.db"))
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS honeylocations(location TEXT PRIMARY KEY)")
        cur.execute("CREATE TABLE IF NOT EXISTS playerdmg(playername TEXT PRIMARY KEY, damage INTEGER, adjusted INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS tournamentprizes(prize TEXT PRIMARY KEY)")
        cur.execute("CREATE TABLE IF NOT EXISTS worldboss(id INTEGER PRIMARY KEY AUTOINCREMENT, worldbossname TEXT, date TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS worldboss_dmg(worldbossid INTEGER, playername TEXT, damage INTEGER, "
                    "PRIMARY KEY(worldbossid, playername))")
        cur.execute("CREATE TABLE IF NOT EXISTS worldbosslocations(location TEXT PRIMARY KEY)")
        conn.commit()
        conn.close()

    def eventconfiguration(self):
        conn = sqlite3.connect(self.pathManager.getpath("eventconfigurations.db"))
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS clanconfig(guildid INTEGER, clan TEXT, PRIMARY KEY (guildid, clan))")
        cur.execute("CREATE TABLE IF NOT EXISTS eventconfig(guildid INTEGER, eventname TEXT, channel INTEGER, pingrole INTEGER "
                    "DEFAULT null, alivetime INTEGER DEFAULT null, PRIMARY KEY (guildid, eventname))")
        cur.execute("CREATE TABLE IF NOT EXISTS eventnames(eventname TEXT PRIMARY KEY)")
        cur.execute("CREATE TABLE IF NOT EXISTS memberconfig(guildid INTEGER, playername TEXT, PRIMARY KEY(guildid, playername))")
        cur.execute("CREATE TABLE IF NOT EXISTS permissions(guildid INTEGER, roleid INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS pmgoldrush(playerid INTEGER, location TEXT, PRIMARY KEY (playerid, location))")
        cur.execute("CREATE TABLE IF NOT EXISTS pmhoney(playerid INTEGER, location TEXT, PRIMARY KEY (playerid, location))")
        cur.execute("CREATE TABLE IF NOT EXISTS pmswarm(playerid INTEGER, pokemon TEXT, location TEXT, comparator TEXT, PRIMARY KEY "
                    "(playerid, pokemon, location, comparator))")
        cur.execute("CREATE TABLE IF NOT EXISTS pmtournament(playerid INTEGER, tournament TEXT, prize TEXT, comparator TEXT, PRIMARY "
                    "KEY (playerid, tournament, prize, comparator))")
        cur.execute("CREATE TABLE IF NOT EXISTS pmworldboss(playerid INTEGER, boss TEXT, location TEXT, comparator TEXT, PRIMARY KEY "
                    "(playerid, boss, location, comparator))")

        eventnames = ['worldboss', 'honey', 'elite4', 'chest', 'serverrestart', 'arceusaltar', 'dianciealtar',
                      'kyogrealtar', 'encounter', 'worldblessing', 'swarm', 'goldrush', 'tournament', 'roll']
        for eventname in eventnames:
            try:
                cur.execute("INSERT INTO eventnames(eventname) VALUES(?)", (eventname,))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        conn.close()
