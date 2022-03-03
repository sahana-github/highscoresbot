from typing import List, Union

import discord
from PIL.Image import Image
import io
from commands.interractions.browseselection import BrowseSelection


class ImgWithText:
    def __init__(self, img: Image, text: Union[str, discord.Embed]):
        self.img = img
        self.text = text


class GMSearch(BrowseSelection):
    def __init__(self, ctx, messages: List):
        super().__init__(ctx, len(messages))
        self.messages = messages
        self.previousmsg = None

    async def initial_send(self):
        await self._sendPage(None)

    async def _sendPage(self, interaction: discord.Interaction):
        page = self.messages[self.currentpage-1]
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

        msg = await self.ctx.send(f"page {self.currentpage} of {self.maxpage}\n" + text,
                                  file=img, embed=embed, view=self)
        if self.previousmsg is not None:
            await self.previousmsg.delete()
        self.previousmsg = msg
