import datetime
import ppobyter.events.worldblessing

from ppobyter.timedevents.timedevents.timedevent import TimedEvent


class Worldblessing(TimedEvent):
    def __init__(self):
        super(Worldblessing, self).__init__(datetime.timedelta(hours=1), None)

    def __call__(self, eventscheduler):
        self.start = self.start + self.cooldown
        self.lock = True
        eventscheduler.addEvent(ppobyter.events.worldblessing.WorldBlessing())

    def __le__(self, other):
        if type(other) == datetime.datetime:
            if not self.lock and other >= self.start:
                return True
        return False
