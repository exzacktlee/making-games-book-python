import enum
import logging
import pygame
import random
import time

from . import board
from . import constants
from . import events
from . import gamestate
from . import settings
from . import sequencecounter


class Model(object):
    """Tracks the game state."""
    def __init__(self, main_event_manager, input_event_manager):
        self._main_event_manager = main_event_manager
        self._main_event_manager.register_listener(self)
        input_event_manager.register_listener(self)
        self._running = False
        self._clock = pygame.time.Clock()
        self._board = board.Board()
        self._flash_queue = list()
        self._sequence_counter = sequencecounter.SequenceCounter()
        self._last_press_time = 0
        self._game_state = None

    @property
    def game_state(self):
        return self._game_state

    @property
    def score(self):
        return self._score

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self._running = False
        elif isinstance(event, events.TickEvent):
            self._update()
        elif isinstance(event, events.ButtonPressEvent):
            if isinstance(self._game_state, gamestate.WaitingForInput):
                self._handle_button_press(event.color)
            elif isinstance(self._game_state, gamestate.GameOver):
                if self._game_state.time_elapsed >= 1:
                    self._new_game()
        elif isinstance(event, events.InitializeEvent):
            self._new_game()

    def run(self):
        """Starts the game loop. Pumps a tick into the event manager for
        each loop."""
        self._running = True
        self._main_event_manager.post(events.InitializeEvent())
        while self._running:
            tick = events.TickEvent()
            self._main_event_manager.post(tick)
            self._clock.tick(settings.FPS)

    def flash(self, color):
        """Handle the details of doing a flash."""
        self._board.flash(color)
        color_index = constants.BASIC_COLORS.index(color)
        self._main_event_manager.post(events.SoundEvent(color_index))

    def get_flashing_buttons(self):
        flashing_buttons = list()
        for color in constants.BASIC_COLORS:
            button = self._board.get_button(color)
            if button.is_flashing:
                flashing_buttons.append(button)
        return flashing_buttons

    def play_sequence(self):
        for button_color in self._sequence:
            self._flash_queue.append(button_color)

    def _new_game(self):
        self._game_state = gamestate.PlayingSequence()
        self._sequence = list()
        self._score = 0
        self._new_round()

    def _new_round(self):
        self._game_state = gamestate.PlayingSequence()
        new_color = random.choice(constants.BASIC_COLORS)
        self._sequence.append(new_color)
        self._sequence_counter.reset()
        self.play_sequence()

    def _update(self):
        self._board.update()
        if isinstance(self._game_state, gamestate.WaitingForInput):
            self._check_for_successful_player_input()
            self._check_for_game_over()
        elif isinstance(self._game_state, gamestate.Idle):
            self._check_for_new_round()
        elif isinstance(self._game_state, gamestate.PlayingSequence):
            self._progress_sequence()

    def _check_for_successful_player_input(self):
        if self._sequence_counter.started:
            if self._sequence_counter.count >= len(self._sequence) - 1:
                self._score += 1
                self._game_state = gamestate.Idle()

    def _check_for_game_over(self):
        reached_timeout = time.time() - self._last_press_time >= \
                          settings.TIMEOUT
        if self._sequence_counter.started and reached_timeout:
            self._player_loses()

    def _check_for_new_round(self):
        if self._game_state.time_elapsed >= 1:
            self._new_round()

    def _progress_sequence(self):
        if len(self._flash_queue) > 0:
            self._attempt_next_flash()
        else:
            self._game_state = gamestate.WaitingForInput()

    def _player_loses(self):
        logging.info('Game Over!')
        self._game_state = gamestate.GameOver()

    def _attempt_next_flash(self):
        time_since_last_flash = self._board.time_since_last_flash
        if time_since_last_flash is not None:
            is_time_to_flash = time_since_last_flash >= settings.FLASH_DELAY
            if is_time_to_flash:
                button_color = self._flash_queue.pop(0)
                self.flash(button_color)

    def _handle_button_press(self, color):
        self.flash(color)
        self._sequence_counter.increment()
        if self._sequence[self._sequence_counter.count] == color:
            self._last_press_time = time.time()
        else:
            self._player_loses()
