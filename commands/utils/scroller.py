import asyncio
import io
from typing import Union, List

import discord
import discord_components
from PIL import Image
from discord.ext.commands import Context
from discord_components import Button, ButtonStyle


class ImgWithText:
    def __init__(self, img: Image, text: Union[str, discord.Embed]):
        self.img = img
        self.text = text


class Scroller:
    def __init__(self, client: discord.Client, resultmessages: List[ImgWithText], ctx: Context, timeout: int=600,
                 startpage: Union[str, None]=None):
        self.client = client
        self.timeout = timeout
        self.__pageTurner = PageTurner(resultmessages)
        self.__buttons = [[Button(style=ButtonStyle.blue, label="<<"),
                           Button(style=ButtonStyle.blue, label="<"),
                           Button(style=ButtonStyle.red, label=">"),
                           Button(style=ButtonStyle.red, label=">>")]]
        self.__buttonids = []
        for row in self.__buttons:
            for button in row:
                self.__buttonids.append(button.id)
        if startpage is None:
            startpage = resultmessages[0]
        self.startpage = startpage
        self.ctx = ctx
        self.previousmsg = None

    async def loop(self):
        self.originmsg = await self.ctx.send(f"```page {self.__pageTurner.page} of {self.__pageTurner.MAXPAGE}```\n",
                                        components=self.__buttons)
        while True:
            try:
                res = await self.client.wait_for("button_click",
                                                 check=lambda response:
                                                 response.component.id in self.__buttonids,
                                                 timeout=self.timeout)
                if res.component.label == "<":
                    page = self.__pageTurner.changePage(-1)
                elif res.component.label == ">":
                    page = self.__pageTurner.changePage(1)
                elif res.component.label == "<<":
                    page = self.__pageTurner.changePage(self.__pageTurner.MINPAGE, True)
                elif res.component.label == ">>":
                    page = self.__pageTurner.changePage(self.__pageTurner.MAXPAGE, True)
                else:
                    page = self.__pageTurner.changePage(0)
                await res.edit_origin(f"```page {self.__pageTurner.page} of {self.__pageTurner.MAXPAGE}```")
                await self.edit_source(page)
            except asyncio.TimeoutError:
                for buttonrow in self.__buttons:
                    for button in buttonrow:
                        button.set_disabled(True)
                await self.originmsg.edit(f"```page {self.__pageTurner.page} of {self.__pageTurner.MAXPAGE}```\n" +
                               self.__pageTurner.changePage(0), components=self.__buttons)
                break

    async def edit_source(self, page: Union[ImgWithText, str]):
        img = None
        text = page if type(page) == str else ""
        embed = page.text if type(page) == ImgWithText and type(page.text) == discord.Embed else None

        if type(page) == ImgWithText and page.img is not None:
            if callable(page.img):
                generated_img = page.img()
            else:
                generated_img = page.img
            with io.BytesIO() as image_binary:
                generated_img.save(image_binary, 'PNG')
                image_binary.seek(0)
                img = discord.File(fp=image_binary, filename='image.png')

        msg = await self.ctx.send(text, file=img, embed=embed)
        if self.previousmsg is not None:
            await self.previousmsg.delete()
        self.previousmsg = msg

class PageTurner:
    def __init__(self, pages: List):
        self.pages: List[str] = pages
        self.MINPAGE = 1 if self.pages else 0
        self.MAXPAGE = len(self.pages)
        self.page = self.MINPAGE

    def changePage(self, movement, absolute=False):
        if absolute:
            newpage = movement
        else:
            newpage = self.page + movement
        if newpage > self.MAXPAGE or newpage < self.MINPAGE:
            return self.pages[self.page - 1]
        self.page = newpage
        return self.pages[self.page - 1]

    def add_page(self, page: str):
        self.pages.append(page)
        self.MAXPAGE = len(self.pages)

    def remove_page(self, index: int):
        self.pages.pop(index)
        self.MINPAGE = 1 if self.pages else 0
        self.MAXPAGE = len(self.pages)
        if self.page > self.MAXPAGE:
            self.page = self.MAXPAGE
