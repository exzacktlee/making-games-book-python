class SequenceCounter(object):
    def __init__(self):
        self._started = False
        self._count = -1

    @property
    def started(self):
        return self._started

    @property
    def count(self):
        return self._count

    def reset(self):
        self._started = False
        self._count = -1

    def increment(self):
        self._started = True
        self._count += 1