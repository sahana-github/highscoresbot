import sqlite3

import discord

from commands.sendable import Sendable


class DiscordBinder(discord.ui.View):
    def __init__(self, ppousername, discord_user_id):
        super().__init__(timeout=6000)
        self.discord_user_id = discord_user_id
        self.ppousername = ppousername

    @discord.ui.button(label='accept account binding', style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("button!!!!")
        with sqlite3.connect("../eventconfigurations.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO discord_bindings(discordid, pponame) VALUES(?, ?)",
                        (self.discord_user_id, self.ppousername))
            conn.commit()
        sendable = Sendable(interaction)
        await sendable.send(f"{self.ppousername} has been bound to your discord account!")
        self.stop()

    @discord.ui.button(label='deny user from (future) binding', style=discord.ButtonStyle.red)
    async def deny_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("button!!!!")
        with sqlite3.connect("../eventconfigurations.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO discord_blocked(pponame, discordid) VALUES(?,?)",
                        (self.ppousername, self.discord_user_id))
            conn.commit()
        sendable = Sendable(interaction)
        await sendable.send(f"{self.ppousername} can't request to bind to your discord account "
                                                f"anymore.")
        self.stop()

    @discord.ui.button(label='prevent all accountbinding in the future', style=discord.ButtonStyle.danger)
    async def deny_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("button!!!!")
        with sqlite3.connect("../eventconfigurations.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO everything_discord_blocked(discordid) VALUES(?)",
                        (self.discord_user_id,))
            conn.commit()
        sendable = Sendable(interaction)
        await sendable.send("You won't receive requests to bind a ppo account with your discord "
                                                "account anymore.")
        self.stop()
