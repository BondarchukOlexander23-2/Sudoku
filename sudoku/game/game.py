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

class Game:
    """Основний клас гри з підтримкою бази даних"""

    def __init__(self, db_path: Optional[str] = None):
        pygame.init()

        self._init_pygame_ui()
        self._init_fonts()
        self._init_database(db_path)
        self._init_game_components()
        self._load_user_settings()

        self.selected_cell: Optional[Tuple[int, int]] = None
        self.difficulty = self._get_preferred_difficulty()
        self.state: IGameState = MainMenuState()
        self.game_initialized = False

    # ─────────────────────────────────────────────────────────────────────────────
    # ІНІЦІАЛІЗАЦІЯ

    def _init_pygame_ui(self):
        self.window_size = WINDOW_SIZE
        self.surface = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Судоку')

    def _init_fonts(self):
        self.font = pygame.font.SysFont('Comic Sans MS', 32)
        self.small_font = pygame.font.SysFont('Comic Sans MS', 16)

    def _init_database(self, db_path: Optional[str]):
        try:
            self.db_manager = GameDatabaseManager(db_path)
            logging.info("Database integration initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            self.db_manager = None

    def _init_game_components(self):
        self.generator = SudokuGenerator()
        self.board = SudokuBoard(self.generator)
        self.renderer = SudokuRenderer(self.font, self.small_font)
        self.button_manager = ButtonManager(self.small_font)
        self.timer = GameTimer()

    def _load_user_settings(self):
        if self.db_manager:
            try:
                max_hints = self.db_manager.get_max_hints()
                # можна встановити self.board.max_hints тут, якщо хочемо зберігати глобально
                logging.info("User settings loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load user settings: {e}")

    def _get_preferred_difficulty(self) -> Difficulty:
        if self.db_manager:
            try:
                pref = self.db_manager.get_user_setting('preferred_difficulty')
                if pref:
                    return Difficulty[pref]
            except Exception as e:
                logging.error(f"Failed to get preferred difficulty: {e}")
        return Difficulty.MEDIUM

    def _initialize_game_ui(self):
        if not self.game_initialized:
            self.button_manager.initialize_buttons()
            if self.db_manager:
                self.board.max_hints = self.db_manager.get_max_hints()
            self.game_initialized = True

    # ─────────────────────────────────────────────────────────────────────────────
    # ОСНОВНІ ДІЇ

    def new_game(self):
        self._initialize_game_ui()
        self.board.initialize(self.difficulty)
        self.selected_cell = None
        self.timer.reset()

    def save_current_game(self) -> bool:
        if not self.db_manager:
            logging.warning("Database not available for saving game")
            return False

        try:
            return self.db_manager.save_current_game(
                self.difficulty,
                self.board.grid,
                self.board.solution,
                self.timer.get_time() // 1000,
                self.board.hints_used
            )
        except Exception as e:
            logging.error(f"Failed to save current game: {e}")
            return False

    def load_saved_game(self, game_id: Optional[int] = None) -> bool:
        if not self.db_manager:
            logging.warning("Database not available for loading game")
            return False

        try:
            saved = (self.db_manager.saved_game_service.load_game(game_id)
                     if game_id else self.db_manager.load_latest_game())

            if not saved:
                logging.info("No saved game found")
                return False

            from ..models import Cell
            self.difficulty = saved.difficulty
            self.board.difficulty = saved.difficulty
            self.board.solution = saved.solution
            self.board.hints_used = saved.hints_used

            self.board.grid = [[Cell.from_dict(c) for c in row] for row in saved.current_state]

            self.timer.elapsed_time = saved.elapsed_time * 1000
            self.timer.start()

            self.set_state(PlayingState())
            logging.info(f"Game loaded successfully: {saved.id}")
            return True

        except Exception as e:
            logging.error(f"Failed to load saved game: {e}")
            return False

    def complete_game(self):
        if not self.db_manager:
            logging.warning("Database not available for saving game record")
            return

        try:
            success = self.db_manager.save_game_record(
                self.difficulty,
                self.timer.get_time() // 1000,
                self.board.hints_used
            )
            if success:
                logging.info("Game record saved successfully")
            else:
                logging.warning("Failed to save game record")
        except Exception as e:
            logging.error(f"Error saving game record: {e}")

    def get_leaderboard(self, difficulty: Optional[Difficulty] = None, limit: int = 10):
        return self.db_manager.get_leaderboard(difficulty, limit) if self.db_manager else []

    def get_personal_stats(self):
        return self.db_manager.get_personal_stats() if self.db_manager else {}

    def has_saved_games(self) -> bool:
        return self.db_manager.has_saved_games() if self.db_manager else False

    # ─────────────────────────────────────────────────────────────────────────────
    # СТАНИ ГРИ

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

    # ─────────────────────────────────────────────────────────────────────────────
    # ІГРОВА ЛОГІКА

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

    # ─────────────────────────────────────────────────────────────────────────────
    # ОСНОВНИЙ ЦИКЛ

    def _handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        else:
            self.state.handle_event(event, self)
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
                for event in pygame.event.get():
                    if not self._handle_event(event):
                        running = False
                        break
                self._render_frame()
                clock.tick(30)
        finally:
            if self.db_manager:
                self.db_manager.close()
            pygame.quit()