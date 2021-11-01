from events.arceusaltar import ArceusAltar
from events.dianciealtar import DiancieAltar
from events.elite4 import Elite4
from events.goldrush import Goldrush
from events.kyogrealtar import KyogreAltar
from events.serverrestart import ServerRestart
from events.swarm import Swarm
from events.event import Event
from events.tournament import Tournament
from events.worldboss import Worldboss
from events.honey import Honey
from events.encounter import Encounter
from events.powerticketpress import Powerticketpress
from ppobyter.events.chest import Chest
from ppobyter.events.roll import Roll


class EventMaker:
    """
    this class makes an event.
    """
    @staticmethod
    def makeEvent(eventname: str, **kwargs) -> Event:
        """
        This class assembles an event.
        :param eventname: the name of the event.
        :param kwargs: location, pokemon, prizes, player etc. A dictionary.
        :return: an event.
        """
        print(kwargs)
        event = None
        if eventname == "swarm":
            event = Swarm(kwargs["location"], kwargs["pokemon1"], kwargs["pokemon2"])
        elif eventname == "worldboss":
            event = Worldboss(kwargs["location"], kwargs["pokemon"])
        elif eventname == "goldrush":
            event = Goldrush(kwargs["location"])
        elif eventname == "honey":
            event = Honey(kwargs["location"], kwargs["player"])
        elif eventname == "serverrestart":
            event = ServerRestart()
        elif eventname == "tournament":
            prizes = [prize.strip() for prize in kwargs["prizes"].split(",")]
            event = Tournament(kwargs["tournament"], prizes)
        elif eventname == "arceusaltar":
            event = ArceusAltar(kwargs["player"], kwargs["amount"])
        elif eventname == "kyogrealtar":
            event = KyogreAltar(kwargs["player"], kwargs["amount"])
        elif eventname == "dianciealtar":
            event = DiancieAltar(kwargs["player"], kwargs["amount"])
        elif eventname == "encounter":
            event = Encounter(kwargs["player"], kwargs["pokemon"], kwargs["level"])
        elif eventname == "elite4":
            event = Elite4(kwargs["player"], kwargs["region"])
        elif eventname == "powerticketpress":
            event = Powerticketpress(kwargs["hours"], kwargs["minutes"])
        elif eventname == "chest":
            event = Chest(kwargs["player"], kwargs["location"])
        elif eventname == "roll":
            event = Roll(kwargs["player"], kwargs["pokemon"], kwargs["level"])
        return event


if __name__ == "__main__":
    #print(EventMaker.makeEvent("swarm", location="route 45", pokemon1="abra", pokemon2="snivy"))
    print(EventMaker.makeEvent("swarm", **{'pokemon1': 'snivy', 'pokemon2': 'abra', 'location': 'route 11'}))
    #print(EventMaker.makeEvent("swarm", ))