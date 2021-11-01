import re
import sqlite3
from commands.utils import tablify
from discord.ext import commands
from commands.highscores_database import Database

class Highscores(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.databasepath = "highscores.db"

    @commands.command(name="exp")
    async def exp(self, ctx, clanname=None):
        """
        shows highscore of top exp
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("exp", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="richestclans")
    async def richestclans(self, ctx, clanname=None):
        """
        position of a clan in the top richest clans
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx, comment=False)) is None):
            clanname = ""
        db = Database()
        resultmessages = tablify(["Rank", "Name", "Founder", "Clan Bank"],
                                 db.executeQuery("SELECT Rank, Name, Founder, Clan_Bank FROM richestclans "
                                                 "WHERE Rank < 10 or Name = '{0}'".format(clanname)))
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
        db = Database()
        resultmessages = tablify(["Rank", "Name", "Founder", "Clan Experience"],
                                 db.executeQuery("SELECT Rank, Name, Founder, Clan_Experience FROM bestclans WHERE Rank < 10 or Name = '{0}'".format(clanname)))
        for i in resultmessages:
            await ctx.send(i)

    @commands.command(name="getplayer")
    async def getplayer(self, ctx, username):
        """
        gets a collection of highscores a player is in.
        :param username:
        """
        username = username.lower()
        db = Database()
        messages = []
        for i in db.getTables():
            if "Username" not in i[1]:
                continue
            query = "SELECT {0}".format(re.sub(r'( |/|-)', "_", str(i[1][0])))
            for j in i[1][1:]:
                query += ", {0}".format(re.sub(r'( |/|-)', "_", j))
            query += " FROM {0} WHERE Username = '{1}'".format(str(i[0]), username)
            messages += tablify(i[1], db.executeQuery(query))
        sendmessages = []
        newmsg = ""
        for i in messages:
            if i.count("\n") < 3:
                continue
            if len(newmsg + i) < 2000:
                newmsg += i
            else:
                sendmessages.append(newmsg)
                newmsg = str(i)
        sendmessages.append(newmsg)
        if len(sendmessages) == 1 and sendmessages[0] == "":
            await ctx.send("or {0} is not in any highscore or he does not exist.".format(username))
        else:
            for i in sendmessages:
                await ctx.send(i)

    @commands.command(name="toprichest")
    async def toprichest(self, ctx, clanname=None):
        """
        gets the highscore of the top richest players
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("richest", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    async def pokeboxes(self, ctx, clanname=None):
        """
        gets the highscore of most opened pokemon boxes
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("pokeboxes", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="evoboxes")
    async def evoboxes(self, ctx, clanname=None):
        """
        gets the highscore of most opened evolution boxes.
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("evoboxes", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="mysteryboxes")
    async def mysteryboxes(self, ctx, clanname=None):
        """
        gets the highsore of most opened mystery boxes
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("mysteryboxes", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="tmboxes")
    async def tmboxes(self, ctx, clanname=None):
        """
        gets the highscore of most opened tm boxes
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("tmboxes", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="btwins")
    async def btwins(self, ctx, clanname=None):
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        clanname = clanname.lower()
        db = Database()
        query = open("query.txt").read()
        query += "'" + str(clanname) + "'"
        result = db.executeQuery(query)
        clanlist = [i[0] for i in result]
        rows = db.executeQuery("SELECT Rank, Username, Wins, Win_Streak FROM btwins")
        adjustedrows = []
        for row in rows:
            if row[1] in clanlist:
                adjustedrows.append(row)
        resultmessages = tablify(["Rank", "Username", "Wins", "Win Streak"], adjustedrows)
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

    @commands.command(name="wbdmg")
    async def wbdmg(self, ctx, clanname=None):
        """
        gets the highscore of worldboss damage
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("wbdmg", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="cwplayers")
    async def cwplayers(self, ctx, clanname=None):
        """
        gets the best clanwar players
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("playercwwins", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="cwwins")
    async def cwwins(self, ctx, clanname=None):
        """
        gets the clanwar wins of a clan
        :param clanname:
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("cwwins", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="achievements")
    async def achievements(self, ctx, clanname=None):
        """
        gets the highscore of achievements
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("achievements", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="pp")
    async def pp(self, ctx, clanname=None):
        """
        gets the philanthropists highscores
        :param clanname: clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("pp", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="weeklyexp")
    async def weeklyexp(self, ctx, clanname=None):
        """
        gets weeklyexp highscores
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("weeklyexp", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="lle")
    async def lle(self, ctx, clanname=None):
        """
        gets legendless encounters highscores
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("lle", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="fishing")
    async def fishing(self, ctx, clanname=None):
        """
        gets fishing highscores
        :param clanname
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("fishing", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="mining")
    async def mining(self, ctx, clanname=None):
        """
        gets mining highscores
        :param clanname:
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("mining", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

    @commands.command(name="dex")
    async def dex(self, ctx, clanname=None):
        """
        gets the top dex highscore of a clan.
        :param clanname:
        """
        if clanname is None and ((clanname := await self.getdefaultclanname(ctx)) is None):
            return
        result = Database().getValues("dex", clanname)
        # layout, values
        messages = tablify(result[1], result[0])
        for i in messages:
            await ctx.send(i)

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
