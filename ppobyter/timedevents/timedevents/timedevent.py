import datetime


class TimedEvent:
    def __init__(self, cooldown: datetime.timedelta, start: datetime.datetime):
        self.lock = False
        self.cooldown: datetime.timedelta = cooldown
        self.start = start

    def setStart(self, start: datetime.datetime):
        self.start = start

    def __call__(self, eventscheduler):
        raise NotImplementedError


if __name__ == "__main__":
    print(type(datetime.timedelta(days=1)))
