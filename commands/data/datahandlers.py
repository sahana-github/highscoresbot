import sqlite3
import datetime


class Worldbossdatahandler:
    def __init__(self):
        self.datadb = sqlite3.connect("data.db")
        self.highscoresdb = sqlite3.connect("highscores.db")

    def addworldboss(self, worldboss):
        
        datacur = self.datadb.cursor()
        datacur.execute("INSERT INTO worldboss(worldbossname, date) VALUES(?,?)", (worldboss, str(datetime.datetime.now(tz=datetime.timezone.utc)).split(" ")[0]))
        self.datadb.commit()
        
    def addplayers(self):
        datacur = self.datadb.cursor()
        highscorescur = self.highscoresdb.cursor()
        id = datacur.execute("SELECT id FROM worldboss ORDER BY id DESC LIMIT 1").fetchall()[0][0]  #get the id from the last worldboss
        #return 0
        highscorescur.execute("SELECT Username, Total_Damage FROM wbdmg")
        result = highscorescur.fetchall()
        if len(datacur.execute("SELECT * FROM worldbossdmg WHERE worldbossint = ?", (id,)).fetchall()) < 1000:
            print("insert called")
            for i in result:
                datacur.execute("INSERT INTO worldbossdmg(playername, totaldamage, worldbossint) VALUES(?,?,?)", (i[0], int(i[1].replace(",","")), id))
            self.datadb.commit()
        else:
            print("update called")
            for i in result:
                datacur.execute("UPDATE worldbossdmg SET totaldamage = ? WHERE playername = ? and worldbossint = ?", (int(i[1].replace(",","")), i[0], id))
            self.datadb.commit()

    def calcdifference(self, worldbossnumber):
        datacur = self.datadb.cursor()
        before = datacur.execute("SELECT playername, totaldamage FROM worldbossdmg WHERE worldbossint = ?", (worldbossnumber - 1,)).fetchall()
        after = datacur.execute("SELECT playername, totaldamage FROM worldbossdmg WHERE worldbossint = ?", (worldbossnumber,)).fetchall()
        beforedict = {}
        for i in before:
            beforedict[i[0]] = int(i[1])
        afterdict = {}
        for i in after:
            afterdict[i[0]] = int(i[1])
        differencedict = {}
        for i in afterdict.keys():
            try:
                differencedict[i] = afterdict[i] - beforedict[i]
            except KeyError:
                pass
        differencedict = dict(sorted(differencedict.items(), key=lambda item: item[1], reverse=True))
        return differencedict

    def calcallworldbosses(self):
        datacur = self.datadb.cursor()
        id = datacur.execute("SELECT id FROM worldboss ORDER BY id DESC LIMIT 1").fetchall()[0][0]  #get the id of the last world boss
        alldicts = []
        for i in range(1, id+1):
            alldicts.append(self.calcdifference(i))
        return alldicts

    def getplayerworldbosses(self, playername):
        # this is written quite inefficient, will require rewrite later.
        datacur = self.datadb.cursor()
        id = datacur.execute("SELECT id FROM worldboss ORDER BY id DESC LIMIT 1").fetchall()[0][0]  #get the id of the last world boss
        datalist = []  # this list consists of lists of [world boss, dmg, date, position, participants]
        alldicts = self.calcallworldbosses()
        count = 1
        for i in alldicts:
            try:
                if i[playername] != 0:
                    datacur.execute("SELECT worldbossname, date FROM worldboss WHERE id = ?", (count,))
                    temp = datacur.fetchall()[0]
                    datalist.append([temp[0], i[playername], temp[1], list(i).index(playername)+1, len({j for j in i.items() if j[1] != 0})])
            except KeyError:
                pass
            count += 1
        return datalist

    def close(self):
        self.datadb.close()
        self.highscoresdb.close()
if __name__ == "__main__":
    wb = Worldbossdatahandler()
    print(wb.getplayerworldbosses("panda2jzn"))
