import re
import sqlite3
from commands.utils import tablify
from discord.ext import commands
from commands.highscores_database import Database
from highscores import *


class Highscores(commands.Cog):
    def __init__(self, client):
        self.client: commands.bot.Bot = client
        self.databasepath = "highscores.db"
        self.makeClanCommands()

    def makeClanCommands(self):
        for highscore in clanhighscores:
            highscore = highscore()
            def outer_cmd(score):
                @commands.command(name=score.NAME)
                async def wut(ctx, clanname):
                    if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
                        return
                    messages = tablify(score.LAYOUT, score.getDbValues(clan=clanname))
                    for i in messages:
                        await ctx.send(i)
                return wut

            self.client.add_command(outer_cmd(highscore))

    @commands.command(name="richestclans")
    async def richestclans(self, ctx, clanname=None):
        """
        position of a clan in the top richest clans
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx, comment=False)) is None):
            clanname = ""
        richestclans = RichestClans()
        values = richestclans.getDbValues(query="SELECT * FROM richestclans WHERE Rank < 10 or Name = ?",
                                          clan=clanname.lower())
        resultmessages = tablify(richestclans.LAYOUT, values)
        for i in resultmessages:
            await ctx.send(i)

    @commands.command(name="bestclans")
    async def bestclans(self, ctx, clanname=None):
        """
        gets the postition of a clan in the top most exp of a clan.
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx, comment=False)) is None):
            clanname = ""
        bestclans = BestClans()
        values = bestclans.getDbValues(query="SELECT * FROM bestclans WHERE Rank < 10 or Name = ?",
                                       clan=clanname.lower())
        resultmessages = tablify(bestclans.LAYOUT, values)
        for i in resultmessages:
            await ctx.send(i)

    @commands.command(name="getplayer")
    async def getplayer(self, ctx, username):
        """
        gets a collection of highscores a player is in.
        :param username:
        """
        username = username.lower()
        allmessages = []
        for highscore in allhighscores:
            highscore = highscore()
            try:
                values = highscore.getDbValues(query="SELECT * FROM {0} WHERE username=?".format(highscore.NAME),
                                               params=[username])
                if (newmessages := tablify(highscore.LAYOUT, values))[0] != "No results found.":
                    allmessages += newmessages
            except sqlite3.OperationalError:
                pass

        sendmessages = []
        newmsg = ""
        for i in allmessages:
            if len(newmsg + i) < 2000:
                newmsg += i
            else:
                sendmessages.append(newmsg)
                newmsg = str(i)
        sendmessages.append(newmsg)
        if len(sendmessages) == 0:
            await ctx.send("or {0} is not in any highscore or he does not exist.".format(username))
        else:
            for i in sendmessages:
                await ctx.send(i)





    @commands.command(name="btwins")
    async def btwins(self, ctx, clanname=None):
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        players = []
        for highscore in allhighscores:
            highscore = highscore()
            try:
                vals = highscore.getDbValues(query="SELECT username FROM {0} WHERE clan=?", clan=clanname.lower())
            except sqlite3.OperationalError:
                continue
            for val in vals:
                if val not in players:
                    players.append(val)

        clanname = clanname.lower()
        btwins = Btwins()
        values = btwins.getDbValues()
        adjustedrows = []
        for row in values:
            if row[1] in players:
                adjustedrows.append(row)
        resultmessages = tablify(btwins.LAYOUT, adjustedrows)
        for message in resultmessages:
            await ctx.send(message)

    @commands.command(name="btwinstreak")
    async def btwinstreak(self, ctx, clanname=None):
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        clanname = clanname.lower()
        db = Database()
        query = open("query.txt").read()
        query += "'" + str(clanname) + "'"
        result = db.executeQuery(query)
        clanlist = [i[0] for i in result]
        rows = db.executeQuery("SELECT Rank, Username, Win_Streak, Wins FROM btwinstreak")
        adjustedrows = []
        for row in rows:
            if row[1] in clanlist:
                adjustedrows.append(row)
        resultmessages = tablify(["Rank", "Username", "Win Streak", "Wins"], adjustedrows)
        for message in resultmessages:
            await ctx.send(message)

    @commands.command(name="mapcontrol")
    async def mapcontrol(self, ctx, clanname = None):
        """
        shows the standings of all mapcontrol areas.
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            clanname = ""
        messages = ["Ancient Cave:"]
        db = Database()
        messages += tablify(["Rank", "Clan Name", "Pokemon Defeated"],
                db.executeQuery("SELECT Rank, Clan_Name, Pokemon_Defeated FROM ancmc WHERE Rank < 10 OR Clan_Name= '{0}'".format(clanname)))
        messages.append("Battle Zone:")
        messages +=tablify(["Rank", "Clan Name", "Pokemon Defeated"],
                db.executeQuery("SELECT Rank, Clan_Name, Pokemon_Defeated FROM bzmc WHERE Rank < 10 OR Clan_Name= '{0}'".format(clanname)))
        messages.append("Safari Zone:")
        messages += tablify(["Rank", "Clan Name", "Pokemon Defeated"],
                db.executeQuery("SELECT Rank, Clan_Name, Pokemon_Defeated FROM safarimc WHERE Rank < 10 OR Clan_Name= '{0}'".format(clanname)))

        allresultmessages = []
        totalresultmessage = ""
        for i in messages:
            if len(totalresultmessage + i) < 2000:
                totalresultmessage +=i
            else:
                allresultmessages.append(totalresultmessage)
                totalresultmessage = i
        allresultmessages.append(totalresultmessage)
        for i in allresultmessages:
            await ctx.send(i)

    @commands.command(name="top")
    async def top(self, ctx, highscoretype, clanname=None):
        """
        shows top 9 + the provided clan.
        :param highscoretype: the type of highscore
        :param clanname: the clanname, default none, clannamehandler gets clan from db if none.
        :return:
        """
        highscoresdict = {"dex": "dex",
                          "richest": "richest",
                          "pokeboxes": "pokeboxes",
                          "evoboxes": "evoboxes",
                          "mysteryboxes": "mysteryboxes",
                          "tmboxes": "tmboxes",
                          "wbdmg": "wbdmg",
                          "cwplayers": "playercwwins",
                          "cwwins": "cwwins",
                          "weeklyexp": "weeklyexp",
                          "lle": "lle",
                          "fishing": "fishing",
                          "mining": "mining",
                          "achievements": "achievements",
                          "pp": "pp",
                          "exp": "exp",
                          "btwins": "btwins",
                          "btwinstreak": "btwinstreak"
                          }
        highscoretype = highscoretype.lower()

        try:
            highscoresdict[highscoretype]
            if clanname is None:
                clanname = await self.getdefaultclanname(ctx, comment=False)
            if highscoretype == "btwinstreak" or highscoretype == "btwins":
                clanname = None
        except KeyError:
            allhighscores = ""
            for i in highscoresdict.keys():
                allhighscores += str(i) + "\n"
            await ctx.send("no valid highscore was given. possible highscores:\n" + str(allhighscores))
            return -1
        if clanname is not None:
            clanname = clanname.lower()
        db = Database()
        layout = db.executeQuery("SELECT layout FROM allhighscorenames WHERE tablename = '{0}'".format(highscoresdict[highscoretype]))[0][0].split(", ")
        textlayout = layout
        layout = [re.sub(r'( |/|-)', "_",str(i)) for i in layout]
        query = "SELECT "
        for i in layout[:-1]:
            query += str(i) + ", "
        query += layout[-1] + " FROM " + str(highscoresdict[highscoretype]) + " WHERE Rank < 10"
        if clanname is not None:
            query += " OR Clan = '" + str(clanname) + "'"
        result = db.executeQuery(query)
        messages = tablify(textlayout, result)
        for i in messages:
            await ctx.send(i)

    @commands.command(name="getclan")
    async def getclan(self, ctx, clanname):
        clanname = clanname.lower()
        queries = ["SELECT Rank, Clan_Name, Pokemon_Defeated FROM safarimc WHERE Clan_Name = ?",
            "SELECT Rank, Clan_Name, Pokemon_Defeated FROM ancmc WHERE Clan_Name = ?",
            "SELECT Rank, Clan_Name, Pokemon_Defeated FROM bzmc WHERE Clan_Name = ?",
            "SELECT Rank, Name, Founder, Clan_Experience FROM bestclans WHERE Name = ?",
            "SELECT Rank, Name, Founder, Clan_Bank FROM richestclans WHERE Name = ?"]
        allresults = []
        conn = sqlite3.connect("./highscores.db")
        cur = conn.cursor()
        for querie in queries:
            cur.execute(querie, (clanname,))
            allresults.append(cur.fetchall())
        resultmessage = ""
        if allresults[0] != []:
            resultmessage += "safari mapcontrol:\n"
            resultmessage += tablify(["Rank", "Clan Name", "Pokemon Defeated"], allresults[0])[0]
        if allresults[1] != []:
            resultmessage += "ancient cave map control:\n"
            resultmessage += tablify(["Rank", "Clan Name", "Pokemon Defeated"], allresults[1])[0]
        if allresults[2] != []:
            resultmessage += "battle zone map control:\n"
            resultmessage += tablify(["Rank", "Clan Name", "Pokemon Defeated"], allresults[2])[0]
        if allresults[3] != []:
            resultmessage += "top exp:\n"
            resultmessage += tablify(["Rank", "Name", "Founder", "Clan Experience"], allresults[3])[0]
        if allresults[4] != []:
            resultmessage += "top richest:\n"
            resultmessage += tablify(["Rank", "Name", "Founder", "Clan Bank"], allresults[4])[0]
        if resultmessage != "":
            await ctx.send(resultmessage)
        else:
            await ctx.send("clan is not in the highscores or does not exist.")

    async def getdefaultclanname(self, ctx, comment=True) -> str:
        if ctx.guild is None:
            return
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        cur.execute("SELECT name FROM clannames WHERE id=?", (ctx.guild.id,))
        try:
            clanname = cur.fetchall()[0][0]
        except IndexError:
            clanname = None
        if clanname is None and comment:
            await ctx.send("Please register a default clanname or provide a clan in the command.")
        elif clanname is not None:
            clanname = clanname.lower()
        return clanname


def setup(client):
    client.add_cog(Highscores(client))
