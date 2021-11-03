import discord

from ppobyter.events.clanevent import ClanEvent


class ItemBomb:
    def __init__(self, players, prizes):
        self.hitplayers = []
        for index, player in enumerate(players):
            self.hitplayers.append(IndividualBomb(player, prizes[index]))

    async def __call__(self, client):
        for hit in self.hitplayers:
            await hit(client)

class IndividualBomb(ClanEvent):
    def __init__(self, player, item):
        self.item = item
        self.EVENTNAME = "itembomb"
        super(IndividualBomb, self).__init__(player)

    def determineRecipients(self):
        self._determinechannelrecipients()

    def makeMessage(self) -> discord.Embed:
        embed = discord.Embed(title=f"🎉Congratulations {self.player}!🎉",
                              description=f"{self.player} has received {self.item[1]} {self.item[0]}!",
                              colour=discord.Colour.magenta())
        return embed
if __name__ == "__main__":
    text = "('itembomb', {'players': ['ferb', 'paulwalker', 'blackangelbr', 'n3tr0xx', 'kiencuibap1472', 'acex93', 'benmin', 'curtbertmoon', 'pokemongame2', 'ndginferno'], 'prizesamount': [['Mystery Box', '1'], ['Evolutional Stone Box', '1'], ['Evolutional Stone Box', '1'], ['Max Repel', '1'], ['Ultra Ball', '6'], ['1 Day GM Ticket', '1'], ['Ultra Ball', '1'], ['Evolutional Stone Box', '1'], ['30 Day GM Ticket', '1'], ['1 Day GM Ticket', '1']]})"