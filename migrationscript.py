import worldbossmigrater
from highscoresupdater import HighscoresUpdater
from ppowebsession import PpoWebSession
import os
import sqlite3

query = "CREATE TABLE worldboss_dmg(worldbossid INTEGER, playername TEXT, damage INTEGER, " \
        "PRIMARY KEY(worldbossid, playername))"
query2 = "CREATE TABLE playerdmg(playername TEXT PRIMARY KEY, damage INTEGER, adjusted INTEGER);"
if __name__ == "__main__":
    print("creating worldboss tables")
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute(query)
    cur.execute(query2)
    conn.commit()
    conn.close()
    print("worldboss tables created.")
    websession = PpoWebSession(os.environ.get("username"), os.environ.get("password"), 2)
    websession.login()
    print("logged in to highscores.")
    updater = HighscoresUpdater(websession)
    updater.makeHighscores("highscores.db")
    print("made highscores.")
    print("updating highscores.")
    updater.updateHighscores()
    print("highscores updated.")
    print("starting worldboss migration.")
    wbmigrater = worldbossmigrater.WorldbossMigrater()
    wbmigrater.migrate()
    print("worldboss migration done!")
