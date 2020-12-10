import time


class Stats:
    def __init__(self, name):
        self._name: str = name
        self._count: int = 0
        self._time: int = time.monotonic()
        self._trip: int = 5000

    def incr(self, amount=1):
        self._count += amount
        if self._count > self._trip:
            end_time = time.monotonic()
            print(f"{self._name} {self._count / (end_time-self._time)}/s")
            self._count = 0
            self._time = end_time
