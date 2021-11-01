import sqlite3


class Database:
    """
    this class has some usefull methods to interact with the database.
    """

    def __init__(self):
        """
        creates sqlite connection to the database.
        """
        self.conn = sqlite3.connect("highscores.db")

    def executeQuery(self, query):
        """
        execute a query.
        :param query:
        :return result of a querya
        """
        cur = self.conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        # commiting has been removed due to sql injection being possible this way.
        return result

    def register(self, id, clanname):
        """
        sets a clanname for a guild so a user won't need to specify clanname in most commands.
        :param id: discord guildid
        :param clanname: clanname
        """
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO clannames(id, name) VALUES(?,?)", (id, clanname))
            self.conn.commit()
        except sqlite3.IntegrityError:
            cur = self.conn.cursor()
            cur.execute("UPDATE clannames SET name=? WHERE id=?", (clanname, id))
            self.conn.commit()

    def unregister(self, id):
        """
        remove default clanname for most commands.
        """
        cur = self.conn.cursor()
        cur.execute("UPDATE clannames SET name = NULL WHERE id=?", (id,))
        self.conn.commit()

    def getClanname(self, id):
        """
        gets the clanname with the given discord guildid
        :param id: guildid from discord
        :return: clanname or None
        """
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM clannames WHERE id=?", (id,))
        result = cur.fetchall()
        if len(result) == 1:
            return result[0][0]
        else:
            return -1

    def getTables(self):
        """
        gets all the tables
        :return: [[tablename, [layout]],[tablename, [anotherlayout]]]
        """
        newresult = []
        result = self.executeQuery("SELECT tablename, layout FROM allhighscorenames")
        for i in result:
            newresult.append([i[0], i[1].split(", ")])
        return newresult

    def getValues(self, tablename, clanname):
        """
        gets everything except the id from a table, also filters by clan if a clan exists in the table.
        :param tablename: name of the table in the database
        :param clanname:
        :return: values, layout
        """
        for i in self.getTables():
            if i[0] == tablename:
                layout = i[1]
                break

        cur = self.conn.cursor()
        try:
            layout.index("Clan")
            cur.execute("SELECT * FROM {0} WHERE Clan=?".format(tablename), (clanname.lower(),))
        except ValueError:
            cur.execute("SELECT * FROM {0}".format(tablename))
        vals = [list(i[1:]) for i in cur.fetchall()]
        return vals, layout