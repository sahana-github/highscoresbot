import asyncio
import io
from threading import Thread
from typing import Union, List, Callable

import discord
import discord_components
from PIL import Image
from discord.ext.commands import Context
from discord_components import Button, ButtonStyle, Select, SelectOption


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
        await self.edit_source(self.__pageTurner.changePage(0))
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
                await self.originmsg.edit(f"```page {self.__pageTurner.page} of {self.__pageTurner.MAXPAGE}```\n",
                                          components=self.__buttons)
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


class DropdownScroller:
    def __init__(self, options: List[str], ctx, action: Callable, client, selectiontext="Select below:"):
        self.client = client
        self.ctx = ctx
        self.action = action
        self.selectiontext = selectiontext
        self.__buttonids = []
        self.__selectids = []
        self.selects = {}
        self.buttons = []
        self.buildSelectPages(options)
        self.buildbuttons()
        self.page = 1

    def buildSelectPages(self, options):
        temp = []
        page = 1
        for option in options:
            temp.append(option)
            if len(temp) == 25:
                self.selects[page] = Select(placeholder=self.selectiontext,
                                            options=[SelectOption(label=option,
                                                                  value=option)
                                                     for option in temp], )
                temp = []
                page += 1
        if len(temp) != 0:
            self.selects[page] = Select(placeholder=self.selectiontext,
                                        options=[SelectOption(label=option,
                                                              value=option)
                                                 for option in temp], )
        for select in self.selects.values():
            self.__selectids.append(select.id)

    def buildbuttons(self):
        self.buttons = [Button(style=ButtonStyle.blue, label="<<"),
                        Button(style=ButtonStyle.blue, label="<"),
                        Button(style=ButtonStyle.red, label=">"),
                        Button(style=ButtonStyle.red, label=">>")]

        for button in self.buttons:
            self.__buttonids.append(button.id)

    async def mainloop(self):
        self.originmsg = await self.ctx.send(f"```page {self.page} of {max(self.selects.keys())}```\n",
                                             components=[self.selects[self.page], self.buttons])
        asyncio.create_task(self.__buttonClickResponseHandler())
        asyncio.create_task(self.__selectOptionResponseHandler())

    async def __buttonClickResponseHandler(self):
        while True:
            res = await self.client.wait_for("button_click",
                                                 check=lambda response:
                                                 response.component.id in self.__buttonids,
                                                 timeout=1000)
            await self.__processResponse(res)

    async def __selectOptionResponseHandler(self):
        while True:
            res = await self.client.wait_for("select_option",
                                         check=lambda response:
                                         response.component.id in self.__selectids,
                                         timeout=1000)
            await self.__processResponse(res)

    async def __processResponse(self, res):
        if res.component.id in self.__buttonids:
            if res.component.label == "<" and self.page > 1:
                self.page -= 1
            elif res.component.label == ">" and self.page < max(self.selects.keys()):
                self.page += 1
            elif res.component.label == "<<":
                self.page = 1
            elif res.component.label == ">>":
                self.page = max(self.selects.keys())
            await res.edit_origin(f"```page {self.page} of {max(self.selects.keys())}```\n",
                                  components=[self.selects[self.page], self.buttons])
        elif res.component.id in self.__selectids:
            await self.originmsg.delete()
            await self.action(res.values[0])

        else:
            print("ok")