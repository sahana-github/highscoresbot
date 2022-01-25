import datetime
from typing import List

from ppobyter.events.timedevent import TimedEvent


class SettimeEvent(TimedEvent):
    def __init__(self, days: List[int], times: List[datetime.time], cooldown: datetime.timedelta):
        """
        :param days: List of days, like [1, 2] where 1 is monday and 2 is tuesday.
        :param times: List of times in a day the event should activate.
        :param cooldown: the cooldown after an event has been sent.
        """
        self.activationtimes = []
        self.days = []
        for day in days:
            self.setDay(day)
        self.times = times
        super().__init__(cooldown)
        self.weeknumber = self.getWeekNumber()
        self.generateActivationTimes()

    def getWeekNumber(self):
        now = datetime.datetime.now()
        return now.isocalendar()[1]

    def generateActivationTimes(self):
        now = datetime.datetime.now()
        weekday = now.isoweekday()
        self.activationtimes = []
        for day in self.days:
            for time in self.times:
                newday = now + datetime.timedelta(days=day-weekday)
                newdatetime = datetime.datetime(year=now.year, month=now.month, day=newday.day, hour=time.hour,
                                                minute=time.minute)
                if now >= newdatetime:
                    continue
                self.activationtimes.append(newdatetime)
        self.activationtimes.sort()
        if self.activationtimes:
            self.activationtime = self.activationtimes[0]

    def setDay(self, day):
        if 1 <= day <= 7:
            if not self.days.__contains__(day):
                self.days.append(day)
        else:
            raise ValueError("day should be between 1 and 7")

    async def __call__(self, client):
        await super().__call__(client)
        # go to the next activationtime.
        if self.activationtimes:  # should not be empty, but to be certain.
            self.activationtimes.pop(0)
        if self.activationtimes:
            self.activationtime = self.activationtimes[0]

    def __bool__(self):
        if self.weeknumber != self.getWeekNumber():
            self.weeknumber = self.getWeekNumber()
            self.generateActivationTimes()
        return self.activationtime is not None and not self.hasCooldown()

    def messageProcesser(self, message: str):
        pass


if __name__ == "__main__":
    s = SettimeEvent([6, 7], [datetime.time(hour=19, minute=15), datetime.time(hour=20, minute=15)], datetime.timedelta(minutes=10))