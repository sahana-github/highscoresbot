class EventScheduler:
    """
    this class stores events in a list of functions, and handles those functions following the FIFO principle.
    """
    def __init__(self, client):
        """
        initializes the empty list of functions.
        """
        self.__client = client
        self.__events = []

    async def handleEvent(self):
        """
        handles the first event in the stack.
        """
        if self.__events:
            print(type(self.__events[0]))
            await self.__events[0](self.__client)
            del self.__events[0]

    def eventAvailable(self) -> bool:
        """
        :return: boolean if the list of events is not empty.
        """
        return bool(self.__events)

    def addEvent(self, event):
        """
        adds event to the stack.
        :param event: a function without parameters.
        """
        self.__events.append(event)

if __name__ == "__main__":
    e = EventScheduler()
    e.addEvent(lambda: print("hello world"))
    e.handleEvent()
    e.handleEvent()
    e.addEvent(lambda: print("bye world"))
    e.handleEvent()
