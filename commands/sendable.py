from typing import Union

from discord import Interaction, User
from discord.abc import Messageable


class Sendable:
    def __init__(self, inputsrc: Union[Messageable, Interaction]):
        self.inputsrc = inputsrc
        attributes = ["guild", "channel", "user"]
        for attribute in attributes:
            try:
                inputsrc.__getattribute__(attribute)
            except AttributeError:
                self.__setattr__(attribute, None)
        if type(inputsrc) == User:
            self.__setattr__("user", inputsrc)

    async def send(self, *args, **kwargs):
        if type(self.inputsrc) == Interaction:
            if not self.inputsrc.response.is_done():
                send = self.inputsrc.response.send_message
            elif self.inputsrc.channel is not None:
                send = self.inputsrc.channel.send
            else:
                send = self.inputsrc.user.send
        else:
            send = self.inputsrc.__getattribute__("send")

        await send(*args, **kwargs)

    def __getattribute__(self, item, get_from_sendable=False):
        """

        :param item:
        :param get_from_sendable: explicitely request and attribute from the inputsource.
        :return:
        """
        if get_from_sendable:
            return self.inputsrc.__getattribute__(item)
        try:
            attr = super(Sendable, self).__getattribute__(item)  # isn't
        except AttributeError:
            attr = self.inputsrc.__getattribute__(item)
        return attr
