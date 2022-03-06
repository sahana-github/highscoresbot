from typing import List
import sqlite3
import discord

from commands.interractions.selectsutility import SelectsUtility


class Register(SelectsUtility):
    def __init__(self, ctx, options: List[str], channel: discord.channel.TextChannel, databasepath: str):
        super().__init__(ctx=ctx, options=options, max_selectable=len(options),
                         placeholder="select events to register for:")
        self.channel = channel
        self.databasepath = databasepath

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="registration done!", view=None)
        conn = sqlite3.connect(self.databasepath)
        cur = conn.cursor()
        for event in self.values:
            try:
                result = cur.execute("UPDATE eventconfig SET channel=? WHERE guildid=? AND eventname=?",
                                     (self.channel.id, self.ctx.guild.id, event))
                if not result.rowcount:  # no rows affected by previous statement.
                    cur.execute("INSERT INTO eventconfig(guildid, eventname, channel) VALUES(?, ?, ?)",
                                (self.ctx.guild.id, event, self.channel.id))
                conn.commit()
                await self.channel.send(
                    f"This channel has been properly configured for sending the {event} event {self.ctx.author.mention}!")
            except sqlite3.IntegrityError:
                await self.ctx.send(f"{event} event already registered in this channel!")
        conn.close()
