import sqlite3
from sqlite3 import Cursor
from typing import List, Union

import discord

from ppobyter.events.event import Event
from ppobyter.marketplace.item import Item


class GMSearch(Event):
    def __init__(self, searcheditems: List[Item]):
        self.searchedItems = searcheditems
        super(GMSearch, self).__init__()
        self.responseid = self.__getResponseID()
        self.__insertItems()

    def determineRecipients(self): pass

    def __insertItems(self):
        """
        inserts all items in the database.
        :return:
        """
        conn = sqlite3.connect(self.pathManager.getpath("eventconfigurations.db"))
        cur = conn.cursor()
        if len(self.searchedItems) == 0:
            cur.execute("INSERT INTO gmsearchresult(responseid, page, content) VALUES(?,?,?)",
                        (self.responseid, 1, None))
        for index, item in enumerate(self.searchedItems):
            cur.execute("INSERT INTO gmsearchresult(responseid, page, content) VALUES(?,?,?)",
                        (self.responseid, index + 1, str(item.to_dict())))
        conn.commit()
        conn.close()

    def __getResponseID(self) -> Union[int, None]:
        with sqlite3.connect(self.pathManager.getpath("eventconfigurations.db")) as conn:
            cur = conn.cursor()
            cur.execute("SELECT min(id) FROM gmsearch")
            resp = cur.fetchone()
            if resp:
                return resp[0]

    async def __call__(self, client: discord.Client):
        """
        search done, so deleting request for search.
        :param client:
        :return:
        """
        conn = sqlite3.connect(self.pathManager.getpath("eventconfigurations.db"))
        cur = conn.cursor()
        cur.execute("DELETE FROM gmsearch WHERE id = ?", (self.responseid,))
        conn.commit()
        conn.close()
