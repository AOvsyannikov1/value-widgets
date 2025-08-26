from time import monotonic


class Timer:

    def __init__(self, period, callback=None):
        self.period = period / 1000
        self.counter = monotonic()
        self.callback = callback

    def restart(self):
        self.counter = monotonic()

    def set_period(self, period):
        self.period = period / 1000

    def expired(self):
        return self.get() >= self.period * 1000

    def get(self):
        return int((monotonic() - self.counter) * 1000)

    def process(self):
        if self.expired() and self.callback:
            self.restart()
            self.callback()
