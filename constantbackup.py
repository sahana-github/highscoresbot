import sqlite3
import requests
import time
from bs4 import BeautifulSoup
import re
import datetime
import os
import datahandlers

class ConstantBackup:
    """
    this class logs in to the ppo website and stores stuff inside the database.
    """

    def __init__(self, username, password, interval):
        """

        :param username: pokemon planet username
        :param password: pokemon planet password
        :param interval: the time it sleeps between the extraction of a database. recommended not to set it too low.
        during normal backups i'd use 5 seconds, else 2.
        """
        self.conn = sqlite3.connect("..\highscores.db")
        self.interval = interval
        self.cookies = {}
        self.cookies["user"] = username
        self.cookies["passwrd"] = password
        self.cookies["cookielength"] = "-1"
        self.session = requests.Session()
        r = self.session.post("https://pokemon-planet.com/")
        time.sleep(self.interval)
        sourcecodesplitted = r.text.split("\n")
        cookieline = sourcecodesplitted[209]  # you need a cookie that changes every time to log in.
        self.cookies[cookieline.split('"')[3]] = cookieline.split('"')[5]
        r = self.session.post("https://pokemon-planet.com/forums/index.php?action=login2", data=self.cookies)
        r = self.session.post("https://pokemon-planet.com/forums/index.php?action=login2;sa=check;member=membernumber")
        print("login succesfull?")

    def relogin(self):
        logedin = False
        while not logedin:
            try:
                oldcookies = self.cookies

                self.cookies = {}
                self.cookies["user"] = oldcookies["user"]
                self.cookies["passwrd"] = oldcookies["passwrd"]
                self.cookies["cookielength"] = "-1"
                self.session = requests.Session()
                r = self.session.post("https://pokemon-planet.com/")
                time.sleep(self.interval)
                sourcecodesplitted = r.text.split("\n")
                cookieline = sourcecodesplitted[209]  # you need a cookie that changes every time to log in.
                self.cookies[cookieline.split('"')[3]] = cookieline.split('"')[5]
                r = self.session.post("https://pokemon-planet.com/forums/index.php?action=login2", data=self.cookies)
                r = self.session.post(
                    "https://pokemon-planet.com/forums/index.php?action=login2;sa=check;member=membernumber")
                print("login succesfull?")
                logedin = True
            except:
                print("relogin failed.")
                time.sleep(600)

    def main(self):
        """
        makes constant backup of the database in an infinite loop.
        :return:
        """
        while True:
            try:
                print("starting:" + str(datetime.datetime.now()))
                self.makeConstantBackup("https://pokemon-planet.com/btWins.php", "btwins", 1)
                self.makeConstantBackup("https://pokemon-planet.com/btWinStreak.php", "btwinstreak", 1)
                self.makeConstantBackup("https://pokemon-planet.com/topRichest.php", "richest", 10)
                self.makeConstantBackup("https://pokemon-planet.com/mostPokemonOwned.php", "dex", 10)
                self.makeConstantBackup("https://pokemon-planet.com/mostAchievements.php", "achievements", 10)
                self.makeConstantBackup("https://pokemon-planet.com/topPhilanthropists.php", "pp", 10)
                self.makeConstantBackup("https://pokemon-planet.com/topStrongest.php", "exp", 10)
                self.makeConstantBackup("https://pokemon-planet.com/topFishers.php", "fishing", 10)
                self.makeConstantBackup("https://pokemon-planet.com/topMiners.php", "mining", 10)
                self.makeConstantBackup("https://pokemon-planet.com/playerClanWarWins.php", "playercwwins", 10)
                print("50% at " + str(datetime.datetime.now()))
                self.makeConstantBackup("https://pokemon-planet.com/playerClanWarWinsLosses.php", "cwwins", 10)
                self.makeConstantBackup("https://pokemon-planet.com/mostWorldBossDamage.php", "wbdmg", 10)
                datahandler = datahandlers.Worldbossdatahandler()
                datahandler.addplayers()
                datahandler.close()
                self.makeConstantBackup("https://pokemon-planet.com/mostMysteryBoxes.php", "mysteryboxes", 10)
                self.makeConstantBackup("https://pokemon-planet.com/mostTMBoxes.php", "tmboxes", 10)
                self.makeConstantBackup("https://pokemon-planet.com/mostEvoBoxes.php", "evoboxes", 10)
                self.makeConstantBackup("https://pokemon-planet.com/mostPokemonBoxes.php", "pokeboxes", 10)
                self.makeConstantBackup("https://pokemon-planet.com/topLLE.php", "lle", 10)
                self.makeConstantBackup("https://pokemon-planet.com/weeklyTopStrongest.php", "weeklyexp", 10)
                self.makeConstantBackup("https://pokemon-planet.com/ancientCave.php", "ancmc", 1)
                self.makeConstantBackup("https://pokemon-planet.com/safariZoneMapControl.php", "safarimc", 1)
                self.makeConstantBackup("https://pokemon-planet.com/battleZoneMapControl.php", "bzmc", 1)
                self.makeConstantBackup("https://pokemon-planet.com/topStrongestClans.php", "bestclans", 1)
                self.makeConstantBackup("https://pokemon-planet.com/topRichestClans.php", "richestclans", 1)
                print("DONE!!" + str(datetime.datetime.now()))
            except Exception as e:
                print(e)
                print(
                    "exception occured. backup stopped for 10 minutes. after that a new attempt will be made to start the backup.")
                time.sleep(600)
                self.relogin()

    def makeConstantBackup(self, url, tablename, endpage, startpage=1):
        """

        :param url: the url to extract the data from
        :param tablename: the tablename to store the data in.
        :param page:the amount of pages to make backups from.
        """
        # need to load the first page anyway to get the layout of the page.
        r = self.session.get(str(url) + "?page=1")
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')
        layout = [ele.text.strip() for ele in rows[0].find_all('td')]
        insertquery = self.__createInsertQuery(layout, tablename)
        cur = self.conn.cursor()
        for i in range(startpage, endpage + 1):
            time.sleep(self.interval)
            r = self.session.get(str(url) + "?page=" + str(i))
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            rows = table.find_all('tr')
            for row in rows[1: len(rows)]:
                cols = row.find_all('td')
                columns = []
                for ele in cols:
                    columns.append(ele.text.strip().lower())
                try:
                    layout.index("Username")
                    deletequery = self.__createUpdateQuery(layout, tablename)
                    cur.execute(deletequery, (columns[layout.index('Username')],))
                except ValueError:
                    pass
                cur.execute(insertquery, tuple(columns) + (columns[layout.index("Rank")],))
            self.conn.commit()

    def __createUpdateQuery(self, layout, tablename):
        """
        creates query to prevent double playername in a highscore
        """
        query = "UPDATE {0} SET ".format(tablename)
        for i in layout[:-1]:
            if i != "Rank":
                query += "{0} = '', ".format(re.sub(r'( |/|-)', "_", str(i)))
        query += "{0}='' WHERE Username = ?".format(re.sub(r'( |/|-)', "_", str(layout[-1])))
        return query

    def __createInsertQuery(self, layout, tablename):
        """
        this method creates a insert query based on the layout
        :param layout: the layout of the table.
        :param tablename: the name of the table in the database.
        :return:
        """
        query = "UPDATE " + str(tablename) + " SET "
        for i in layout[:-1]:
            query += re.sub(r'( |/|-)', "_", str(i)) + " = ?,"
        query += re.sub(r'( |/|-)', "_", str(layout[-1])) + " = ? WHERE Rank = ?"
        return query


if __name__ == "__main__":
    c = ConstantBackup("playername", "playerpassword", 5)
    c.main()
