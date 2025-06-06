import pygame
import logging
from typing import Optional, Tuple

from sudoku.game.states.main_menu_state import MainMenuState
from sudoku.game.states.game_over_state import GameOverState
from sudoku.game.states.paused_state import PausedState
from sudoku.game.states.playing_state import PlayingState
from sudoku.game.states.i_game_state import IGameState

from sudoku.config import GRID_SIZE
from sudoku.models import Difficulty
from sudoku.game.game_builder import GameBuilder
from sudoku.game.game_facade import GameFacade
from sudoku.game.database_integration import GameDatabaseManager

# Константа замість магічного числа
FPS = 30


# ✳️ Хелпер для безпечного доступу до бази даних
class DatabaseHelper:
    def __init__(self, db_manager: Optional[GameDatabaseManager]):
        self.db = db_manager

    def execute(self, action, default=None):
        if not self.db:
            logging.warning("Database not available")
            return default
        try:
            return action(self.db)
        except Exception as e:
            logging.error(e)
            return default


class Game:
    """Основний клас гри з підтримкою бази даних"""

    def __init__(self, db_path: Optional[str] = None):
        # Використовуємо Builder для створення компонентів
        components = (GameBuilder()
                      .build_pygame()
                      .build_fonts()
                      .build_components()
                      .build_database(db_path)
                      .build())

        # Ініціалізуємо атрибути з Builder
        self.window_size = components['window_size']
        self.surface = components['surface']
        self.font = components['font']
        self.small_font = components['small_font']
        self.generator = components['generator']
        self.board = components['board']
        self.renderer = components['renderer']
        self.button_manager = components['button_manager']
        self.timer = components['timer']
        self.db_manager = components['db_manager']

        # Створюємо хелпер та фасад
        self.db = DatabaseHelper(self.db_manager)
        self.facade = GameFacade(self.db, self.board, self.timer)

        # Ініціалізуємо налаштування через фасад
        self.facade.initialize_game_settings()

        # Ігрові атрибути
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.difficulty = self.facade.get_preferred_difficulty()
        self.state: IGameState = MainMenuState()
        self.game_initialized = False

    def _initialize_game_ui(self):
        if not self.game_initialized:
            self.button_manager.initialize_buttons()
            self.board.max_hints = self.db.execute(lambda db: db.get_max_hints(), 3)
            self.game_initialized = True

    def new_game(self):
        self._initialize_game_ui()
        self.board.initialize(self.difficulty)
        self.selected_cell = None
        self.timer.reset()

    def save_current_game(self) -> bool:
        return self.facade.save_game_state(self.difficulty)

    def load_saved_game(self, game_id: Optional[int] = None) -> bool:
        saved = self.facade.load_game_state(game_id)
        if not saved:
            return False

        self.difficulty = saved.difficulty
        self.facade.setup_board_from_saved(saved, saved.difficulty)
        self.facade.setup_timer_from_saved(saved)
        self.set_state(PlayingState())
        return True

    def complete_game(self):
        self.facade.complete_game(self.difficulty)

    def pause_game(self):
        if isinstance(self.state, PlayingState):
            self.timer.pause()
            self.state = PausedState()
            self.button_manager.update_pause_button("Продовжити")

    def resume_game(self):
        if isinstance(self.state, PausedState):
            self.timer.resume()
            self.state = PlayingState()
            self.button_manager.update_pause_button("Пауза")

    def set_state(self, new_state: IGameState):
        if isinstance(new_state, GameOverState):
            self.timer.pause()
            self.complete_game()
        self.state = new_state

    def select_cell(self, row: int, col: int):
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self.selected_cell = (row, col)

    def use_hint(self):
        hint = self.board.get_hint()
        if hint:
            row, col, value = hint
            self.board.set_value(row, col, value)
            self.selected_cell = (row, col)

            if self.board.is_complete():
                self.timer.pause()
                self.complete_game()
                self.state = GameOverState()

    def _handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        self.state.handle_event(event, self)
        return True

    def _process_events(self):
        for event in pygame.event.get():
            if not self._handle_event(event):
                return False
        return True

    def _render_frame(self):
        self.state.update(self)
        self.state.render(self.surface, self)
        pygame.display.flip()

    def run(self):
        running = True
        clock = pygame.time.Clock()

        try:
            while running:
                running = self._process_events()
                self._render_frame()
                clock.tick(FPS)
        finally:
            if self.db_manager:
                self.db_manager.close()
            pygame.quit()

    # Додаткові методи для сумісності з states
    def get_leaderboard(self, difficulty=None, limit=10):
        return self.db.execute(lambda db: db.get_leaderboard(difficulty, limit), [])

    def get_personal_stats(self):
        return self.db.execute(lambda db: db.get_personal_stats(), {})

    def has_saved_games(self):
        return self.db.execute(lambda db: db.has_saved_games(), False)