import pygame

from . import events
from . import settings


class Model(object):
    """Tracks the game state."""
    def __init__(self, main_event_manager, input_event_manager):
        self._main_event_manager = main_event_manager
        self._main_event_manager.register_listener(self)
        input_event_manager.register_listener(self)
        self._running = False
        self._clock = pygame.time.Clock()
        self._score = 0

    @property
    def score(self):
        return self._score

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self._running = False

    def run(self):
        """Starts the game loop. Pumps a tick into the event manager for
        each loop."""
        self._running = True
        self._main_event_manager.post(events.InitializeEvent())
        while self._running:
            tick = events.TickEvent()
            self._main_event_manager.post(tick)
            self._clock.tick(settings.FPS)

