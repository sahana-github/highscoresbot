import re
from typing import Tuple, Union

from ppobyter.marketplace.item import Item
from ppobyter.marketplace.pokemon import Pokemon


class EventDeterminer:
    """
    This class determines what event the given message is.
    """
    def __init__(self, message: str):
        """
        Sets the message.
        :param message: A message of which the event must be determined
        """
        self.message: str = message

    def determineEvent(self) -> Union[Tuple[str, dict], None]:
        """
        Determines the eventtype with regular expression and filters out important info about the event.
        :return: A tuple with eventtype and a dict of info about the event.
                Example: ("honey", {"player": "me", "location": "vermillion city"})
        """

        if "`xt`sr`-1`" in self.message:
            return "serverrestart", {}
        if "`xt`r27`-1`" in self.message:
            d = self.message.replace("\n", "")
            gmsearch = d.split("`")[4:]
            gmitemcount = 0
            items = []
            for msg in gmsearch:
                if msg == "":
                    continue
                gmitemcount += 1
                splitted = msg.split(",")
                pokemon = None
                if splitted[2] != '':
                    try:
                        pokemon = Pokemon.fromString(",".join(splitted[2:-7]))
                    except ValueError as e:
                        print(e)
                        print(msg)
                items.append(Item(itemname=splitted[1], sellid=splitted[-1], seller=splitted[0], price=splitted[-6],
                                  amount=splitted[-7], intention=splitted[-4], pokemon=pokemon))
            return "gmsearch", {"searcheditems": items}

        if "`xt`b128`-1`" in self.message:
            splittedtext = self.message.split("`")
            players = [player.lower() for player in splittedtext[6][1:-1].split(",")]
            prizes_and_amount = []
            pattern = r"\[([A-Za-z0-9, ]+)\]"
            for value in re.findall(pattern, splittedtext[5]):
                prizes_and_amount.append(value.split(","))  # [prize, amount]
            return "itembomb", {"players": players, "prizesamount": prizes_and_amount}

        if "`xt`r17`-1`" not in self.message:
            return

        pattern = r"'>(?P<player>[0-9a-zA-Z]+) has encountered a Lv (?P<level>[0-9]+) (?P<pokemon>(\[S\])?(\[E\])?([0-9a-zA-Z-]+))( from mining)?!"
        if match := re.search(pattern, self.message):
            return "encounter", match.groupdict()

        pattern = r"'>(?P<player>[0-9a-zA-Z]+) opened a treasure chest on (?P<location>[0-9a-zA-Z ']+)!"
        if match := re.search(pattern, self.message):
            return "chest", match.groupdict()

        pattern = r"'>A (?P<pokemon>[A-Za-z]+) World Boss has been spotted at (?P<location>[a-zA-Z0-9 ']+)!"
        if match := re.search(pattern, self.message):
            return "worldboss", match.groupdict()

        pattern = r"A group of wild (?P<pokemon1>[a-zA-Z]+) and (?P<pokemon2>[a-zA-Z]+) have been spotted at (?P<location>[a-zA-Z0-9 ']+)\."
        if match := re.search(pattern, self.message):
            return "swarm", match.groupdict()

        pattern = r"'>A gold rush has started at (?P<location>[a-zA-Z0-9 ']+)!"
        if match := re.search(pattern, self.message):
            return "goldrush", match.groupdict()

        pattern = r"'>(?P<player>[0-9a-zA-Z]+) spread some Honey in (?P<location>[0-9a-zA-Z\(\) ]+)!"
        if match := re.search(pattern, self.message):
            return "honey", match.groupdict()

        pattern = r"'>The (?P<tournament>Little Cup|Self Caught|Ubers|Set Level 100|Monotype) Tournament will start in 30 minutes at the Vermilion City PvP Arena. Tournament prize: (?P<prizes>.+?)`"
        if match := re.search(pattern, self.message):
            return "tournament", match.groupdict()

        pattern = r"'><b>(?P<player>[0-9a-zA-Z]+) topped off the Legendary Altar \((?P<altartype>Arceus|Kyogre|Diancie)\) with a donation of (?P<amount>.+?)(<\/b>\.|\.<\/b>)"
        if match := re.search(pattern, self.message):
            groupdict = match.groupdict()
            if groupdict["altartype"] == "Arceus":
                return "arceusaltar", groupdict
            elif groupdict["altartype"] == "Kyogre":
                return "kyogrealtar", groupdict
            elif groupdict["altartype"] == "Diancie":
                return "dianciealtar", groupdict

        pattern = r"'>(?P<player>[0-9a-zA-Z]+) has beat the (?P<region>Kanto|Johto|Hoenn|Sinnoh|Unova) Elite Four!"
        if match := re.search(pattern, self.message):
            return "elite4", match.groupdict()

        pattern = r"'>(?P<player>[0-9a-zA-Z]+) has purchased a Lv (?P<level>[0-9]+) " \
                  r"(?P<pokemon>(\[S\])?([0-9a-zA-Z-]+)) for (.*?)?!"
        if match := re.search(pattern, self.message):
            return "roll", match.groupdict()

        pattern = r"'>(?P<player>[0-9a-zA-Z]+) has received a Lv (?P<level>[0-9]+) " \
                  r"(?P<pokemon>(\[S\])?([0-9a-zA-Z-]+))!"
        if match := re.search(pattern, self.message):
            return "roll", match.groupdict()


if __name__ == "__main__":
    pass
