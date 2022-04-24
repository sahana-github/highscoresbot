from ppobyter.ingame_commands.ppochat import PPOChat


class Context:
    """
    message context of a ppo message.
    """
    def __init__(self, user: str, message: str, chat: PPOChat, ppomap=None):
        self.user = user
        self.message = message
        self.chat = chat
        self.ppomap = ppomap
