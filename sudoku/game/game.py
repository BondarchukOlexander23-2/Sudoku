import pygame
import logging
from typing import Optional, Tuple

from sudoku.game.states.main_menu_state import MainMenuState
from sudoku.game.states.game_over_state import GameOverState
from sudoku.game.states.paused_state import PausedState
from sudoku.game.states.playing_state import PlayingState
from sudoku.game.states.i_game_state import IGameState

from sudoku.config import WINDOW_SIZE, GRID_SIZE
from sudoku.models import Difficulty, Cell
from sudoku.core import SudokuGenerator, SudokuBoard
from sudoku.ui import SudokuRenderer, ButtonManager
from sudoku.game.timer import GameTimer
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
        pygame.init()
        self._init_pygame_ui()
        self._init_fonts()

        self.db_manager = GameDatabaseManager(db_path) if db_path else None
        self.db = DatabaseHelper(self.db_manager)

        self._init_game_components()
        self._load_user_settings()

        self.selected_cell: Optional[Tuple[int, int]] = None
        self.difficulty = self._get_preferred_difficulty()
        self.state: IGameState = MainMenuState()
        self.game_initialized = False

    def _init_pygame_ui(self):
        self.window_size = WINDOW_SIZE
        self.surface = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Судоку')

    def _init_fonts(self):
        self.font = pygame.font.SysFont('Comic Sans MS', 32)
        self.small_font = pygame.font.SysFont('Comic Sans MS', 16)

    def _init_game_components(self):
        self.generator = SudokuGenerator()
        self.board = SudokuBoard(self.generator)
        self.renderer = SudokuRenderer(self.font, self.small_font)
        self.button_manager = ButtonManager(self.small_font)
        self.timer = GameTimer()

    def _load_user_settings(self):
        max_hints = self.db.execute(lambda db: db.get_max_hints())
        if max_hints is not None:
            self.board.max_hints = max_hints

    def _get_preferred_difficulty(self) -> Difficulty:
        pref = self.db.execute(lambda db: db.get_user_setting('preferred_difficulty'))
        if pref:
            return Difficulty[pref]
        return Difficulty.MEDIUM

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
        return self.db.execute(lambda db: db.save_current_game(
            self.difficulty,
            self.board.grid,
            self.board.solution,
            self.timer.get_time() // 1000,
            self.board.hints_used
        ), False)

    def load_saved_game(self, game_id: Optional[int] = None) -> bool:
        def load(db):
            saved = (db.saved_game_service.load_game(game_id)
                     if game_id else db.load_latest_game())
            if not saved:
                return False
            self._load_saved_data(saved)
            return True

        return self.db.execute(load, False)

    def _load_saved_data(self, saved):
        self.difficulty = saved.difficulty
        self.board.difficulty = saved.difficulty
        self.board.solution = saved.solution
        self.board.hints_used = saved.hints_used
        self.board.grid = [[Cell.from_dict(c) for c in row] for row in saved.current_state]

        self.timer.elapsed_time = saved.elapsed_time * 1000
        self.timer.start()
        self.set_state(PlayingState())

    def complete_game(self):
        self.db.execute(lambda db: db.save_game_record(
            self.difficulty,
            self.timer.get_time() // 1000,
            self.board.hints_used
        ))

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
