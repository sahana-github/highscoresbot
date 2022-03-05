import json
import sqlite3
from typing import List

from commands.interractions.selectsutility import SelectsUtility
import discord


class HelpCmd(SelectsUtility):
    def __init__(self, ctx, options: List[str]):
        """
        selectsutility of the help command.
        :param ctx:
        :param options:
        """
        super(HelpCmd, self).__init__(ctx, options=options, max_selectable=len(options), ownerOnly=False,
                                      placeholder="select the command you want help with:")

    async def callback(self, interaction: discord.Interaction):
        """
        send max 5 of the help messages of the selected commands in the server, send the rest in pm.
        :param interaction:
        :return:
        """
        conn = sqlite3.connect("eventconfigurations.db")
        cur = conn.cursor()
        count = 0
        for commandname in self.values:
            if len(commandname.split(" ")) > 1:  # remove category if it has one.
                commandname = commandname.split(" ")[0]
            cur.execute("SELECT helpcategories.name, helpcommands.commandname, helpcommands.embed"
                        " FROM helpcommands LEFT OUTER JOIN helpcategories ON helpcommands.category = helpcategories.id"
                        " WHERE helpcommands.commandname=?",
                        (commandname,))
            categoryname, helpcommandname, embedjson = cur.fetchone()
            embedjson = embedjson.replace("'", '"')
            embedjson = embedjson.replace("False", "0")
            embedjson = embedjson.replace("True", "1")
            embed = discord.Embed.from_dict(json.loads(embedjson))
            if categoryname is not None:
                embed.add_field(name="category", value=categoryname)
            if count > 5:
                await self.ctx.author.send(embed=embed)
            else:
                await self.ctx.send(embed=embed)
            count += 1
        conn.close()
