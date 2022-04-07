import os
import sqlite3
from typing import Any, Tuple, List, Union

import discord
from discord import Client, Embed


class GlobalAnnouncement(Client):
    def __init__(self, embedmsg: Union[str, Embed], debug=True, **options: Any):
        self.embedmsg = embedmsg
        super().__init__(**options)
        self.DEBUG = debug

    async def on_ready(self):
        await self.wait_until_ready()
        await self.send_global_announcement()

    async def send_global_announcement(self):
        if not self.DEBUG:
            conn = sqlite3.connect("eventconfigurations.db")
            cur = conn.cursor()
            cur.execute("SELECT count(DISTINCT guildid) FROM eventconfig")
            if input(f"Warning: you are about to send a message to {cur.fetchone()[0]} discord servers. "
                  f"type 'yes' to proceed") != "yes":
                print("aborted.")
                return
            else:
                print("proceeding.")
        channels = await self.get_channels()
        guilds = []
        for guildid, channelid in channels:
            if guildid in guilds or guildid is None or channelid is None:
                continue
            try:
                channel = await self.fetch_channel(channelid)
                if not self.DEBUG:
                    if type(self.embedmsg) == Embed:
                        await channel.send(embed=self.embedmsg)
                    else:
                        await channel.send(self.embedmsg)
                else:
                    print(f"would've sent to channel {channelid}")
                guilds.append(guildid)
            except Exception as e:
                print(guildid, channelid, e)

    async def get_channels(self) -> List[Tuple[int, int]]:
        conn = sqlite3.connect("eventconfigurations.db")
        try:
            cur = conn.cursor()
            cur.execute("SELECT guildid, channel FROM eventconfig")
            return cur.fetchall()
        except Exception as e:
            print(e)
        finally:
            conn.close()


embed=discord.Embed(title="highscoresbot slash commands", description="highscoresbot will be moving to slash commands instead of normal commands.")
embed.add_field(name="why?", value="Discord is forcing all verified bots to make use of slash commands instead of normal commands. This has to do with privacy, bots no longer have access to [message content](https://support-dev.discord.com/hc/en-us/articles/4404772028055) starting on 31 August.", inline=False)
embed.add_field(name="what do servers need to change?", value="Servers might need to add highscoresbot again (or rather click on the `add to server` button on the profile of the bot)", inline=True)


if __name__ == "__main__":
    GlobalAnnouncement(embed, debug=True).run(token=os.environ.get("token"))
