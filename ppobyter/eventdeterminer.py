import re
from typing import Tuple, Union


class EventDeterminer:
    """
    This class determines what event the given message is.
    """
    def __init__(self, message: str):
        """
        Sets the message.
        :param message: A message of which the event must be determined.
        """
        self.message = message

    def determineEvent(self) -> Union[Tuple[str, dict], None]:
        """
        Determines the eventtype with regular expression and filters out important info about the event.
        :return: A tuple with eventtype and a dict of info about the event.
                Example: ("honey", {"player": "me", "location": "vermillion city"})
        """
        pattern = r"(?<=<\/var><var n='d' t='s'>)([0-9]+:[0-9]+)(?=<\/var><var n='a' t='n'>1.1</var><var n='_cmd' t='s'>" \
                  r"worldBlessing<\/var><\/dataObj>]]><\/body><\/msg>)"
        if re.search(pattern, self.message):
            return "worldblessing", {}
        if "`xt`sr`-1`" in self.message:
            return "serverrestart", {}
        pattern = r"``````Next World Boss in (?P<hours>[0-9]+) hours, (?P<minutes>[0-9]+) minutes.``````"
        if match := re.search(pattern, self.message):
            return "powerticketpress", match.groupdict()

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
    #EventDeterminer("`xt`r17`-1`'>A group of wild snivy and abra have been spotted at route 11.").determineEvent()
    #EventDeterminer("`xt`r17`-1`'>Henkjan spread some Honey in cerulean cave f4!").determineEvent()
    e = EventDeterminer(r"`xt`r17`-1`'>Kevin has received a Lv 79 [S]Gyarados!").determineEvent()
    print(e)
   # EventDeterminer("`xt`r17`-1`'>The Little Cup Tournament will start in 30 minutes at the Vermilion City PvP Arena. Tournament prize: PvP Token (250), Credits (400), Honey (2)`").determineEvent()