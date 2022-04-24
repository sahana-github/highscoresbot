import re

from ppobyter.ingame_commands.context import Context
from ppobyter.ingame_commands.ppochat import PPOChat


class MessageProcesser:
    chatmapping = {"l": PPOChat.LOCAL_CHAT}
    def __init__(self):
        pass

    def processMessage(self, message):
        # for now only works for local chat.
        regex = "`xt`pmsg`-1`<[a-zA-z]><(?P<chat>[l])><(?P<map>[a-zA-Z0-9 ]+)>(?P<message>[a-zA-Z0-9. ]+)`(?P<username>[a-zA-Z0-9]+)`"
        if match := re.search(regex, message):

            groupdict = match.groupdict()
            print("user:", groupdict['username'])
            return Context(user=groupdict["username"],
                    message=groupdict["message"],
                    chat=self.chatmapping.get(groupdict["chat"]),
                    ppomap=groupdict["map"]
                    )