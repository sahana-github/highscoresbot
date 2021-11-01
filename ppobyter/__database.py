import sqlite3


def eventconfigdatabase():
    """
    This method makes the eventconfig database.
    """
    conn = sqlite3.connect("./eventconfigurations.db")
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS pmswarm(playerid INTEGER, pokemon TEXT, location TEXT, comparator TEXT, PRIMARY KEY (playerid, pokemon, location, comparator))")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS eventconfig(guildid INTEGER, eventname TEXT, channel INTEGER, pingrole INTEGER DEFAULT null, alivetime INTEGER DEFAULT null, PRIMARY KEY (guildid, eventname))")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS pmworldboss(playerid INTEGER, boss TEXT, location TEXT, comparator TEXT, PRIMARY KEY (playerid, boss, location, comparator))")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS pmgoldrush(playerid INTEGER, location TEXT, PRIMARY KEY (playerid, location))")
    cur.execute("CREATE TABLE IF NOT EXISTS pmhoney(playerid INTEGER, location TEXT, PRIMARY KEY (playerid, location))")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS pmtournament(playerid INTEGER, tournament TEXT, prize TEXT, comparator TEXT, PRIMARY KEY (playerid, tournament, prize, comparator))")
    cur.execute("CREATE TABLE IF NOT EXISTS clanconfig(guildid INTEGER, clan TEXT, PRIMARY KEY (guildid, clan))")
    cur.execute("CREATE TABLE IF NOT EXISTS permissions(guildid INTEGER, roleid INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS eventnames(eventname TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()


def datadb():
    """
    This function makes the data database.
    """
    conn = sqlite3.connect("./data.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS worldboss(id INTEGER PRIMARY KEY AUTOINCREMENT, worldbossname TEXT, date TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS worldbossdmg(id INTEGER PRIMARY KEY AUTOINCREMENT, playername TEXT, totaldamage INTEGER, worldbossint INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS honeylocations(location TEXT PRIMARY KEY)")
    cur.execute("CREATE TABLE IF NOT EXISTS tournamentprizes(prize TEXT PRIMARY KEY)")
    cur.execute("CREATE TABLE IF NOT EXISTS worldbosslocations(location TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    pass