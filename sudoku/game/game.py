"""
Основний модуль гри з головним меню
"""
import pygame
from typing import Optional, Tuple

from ..config import WINDOW_SIZE, GRID_SIZE
from ..models import Difficulty
from ..core import SudokuGenerator, SudokuBoard
from ..ui import SudokuRenderer, ButtonManager
from .states import IGameState, MainMenuState, PlayingState, GameOverState, PausedState
from .timer import GameTimer


class Game:
    """Основний клас гри"""
    def __init__(self):
        pygame.init()
        self.window_size = WINDOW_SIZE
        self.surface = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Судоку')

        # Ініціалізація шрифтів
        self.font = pygame.font.SysFont('Comic Sans MS', 32)
        self.small_font = pygame.font.SysFont('Comic Sans MS', 16)

        # Ініціалізація компонентів гри
        self.generator = SudokuGenerator()
        self.board = SudokuBoard(self.generator)
        self.renderer = SudokuRenderer(self.font, self.small_font)
        self.button_manager = ButtonManager(self.small_font)
        self.timer = GameTimer()

        # Стан гри
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.difficulty = Difficulty.MEDIUM

        # Починаємо з головного меню
        self.state: IGameState = MainMenuState()

        # Прапорець для перевірки, чи була ініціалізована гра
        self.game_initialized = False

    def _initialize_game_ui(self):
        """Ініціалізує елементи ігрового інтерфейсу (викликається при першому запуску гри)"""
        if not self.game_initialized:
            self.button_manager.initialize_buttons()
            self.game_initialized = True

    def new_game(self):
        """Створює нову гру"""
        # Ініціалізуємо UI при необхідності
        self._initialize_game_ui()

        self.board.initialize(self.difficulty)
        self.selected_cell = None
        self.timer.reset()

    def pause_game(self):
        """Ставить гру на паузу"""
        if isinstance(self.state, PlayingState):
            self.timer.pause()
            self.state = PausedState()
            self.button_manager.update_pause_button("Продовжити")

    def resume_game(self):
        """Відновлює гру після паузи"""
        if isinstance(self.state, PausedState):
            self.timer.resume()
            self.state = PlayingState()
            self.button_manager.update_pause_button("Пауза")

    def select_cell(self, row: int, col: int):
        """Обирає клітинку"""
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self.selected_cell = (row, col)

    def use_hint(self):
        """Використовує підказку"""
        hint = self.board.get_hint()
        if hint:
            row, col, value = hint
            self.board.set_value(row, col, value)
            self.selected_cell = (row, col)

            # Перевірка на завершення гри після використання підказки
            if self.board.is_complete():
                self.timer.pause()
                self.state = GameOverState()

    def set_state(self, new_state: IGameState):
        """Встановлює новий стан гри"""
        if isinstance(new_state, GameOverState):
            self.timer.pause()
        self.state = new_state

    def run(self):
        """Головний цикл гри"""
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.state.handle_event(event, self)

            self.state.update(self)
            self.state.render(self.surface, self)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()