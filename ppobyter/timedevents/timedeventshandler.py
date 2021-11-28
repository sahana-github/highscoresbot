from typing import List

from ppobyter.eventscheduler import EventScheduler
from ppobyter.timedevents.timedevents.timedevent import TimedEvent


class TimedEventsHandler:
    def __init__(self, eventscheduler: EventScheduler):
        self.timedEvents: List[TimedEvent] = []
        self.eventscheduler = eventscheduler

    def handleEvents(self, time):
        for event in self.timedEvents:
            if time >= event:
                event(self.eventscheduler)