"""
Facade для спрощення взаємодії з підсистемами гри
"""
import logging
from typing import Optional
from ..models import Difficulty, Cell


class GameFacade:
    """Facade для об'єднання операцій з різними підсистемами гри"""

    def __init__(self, db_helper, board, timer):
        self.db = db_helper
        self.board = board
        self.timer = timer

    def initialize_game_settings(self):
        """Ініціалізує налаштування гри з бази даних"""
        max_hints = self.db.execute(lambda db: db.get_max_hints())
        if max_hints is not None:
            self.board.max_hints = max_hints

    def get_preferred_difficulty(self) -> Difficulty:
        """Отримує збережену складність або повертає значення за замовчуванням"""
        pref = self.db.execute(lambda db: db.get_user_setting('preferred_difficulty'))
        if pref:
            try:
                return Difficulty[pref]
            except KeyError:
                logging.warning(f"Invalid difficulty setting: {pref}")
        return Difficulty.MEDIUM

    def save_game_state(self, difficulty: Difficulty) -> bool:
        """Зберігає поточний стан гри"""
        return self.db.execute(lambda db: db.save_current_game(
            difficulty,
            self.board.grid,
            self.board.solution,
            self.timer.get_time() // 1000,
            self.board.hints_used
        ), False)

    def load_game_state(self, game_id: Optional[int] = None):
        """Завантажує збережений стан гри"""

        def load(db):
            saved = (db.saved_game_service.load_game(game_id)
                     if game_id else db.load_latest_game())
            if not saved:
                return None
            return saved

        return self.db.execute(load, None)

    def complete_game(self, difficulty: Difficulty):
        """Обробляє завершення гри"""
        self.db.execute(lambda db: db.save_game_record(
            difficulty,
            self.timer.get_time() // 1000,
            self.board.hints_used
        ))

    def setup_board_from_saved(self, saved_data, difficulty: Difficulty):
        """Налаштовує дошку з збережених даних"""
        self.board.difficulty = difficulty
        self.board.solution = saved_data.solution
        self.board.hints_used = saved_data.hints_used
        self.board.grid = [[Cell.from_dict(c) for c in row] for row in saved_data.current_state]

    def setup_timer_from_saved(self, saved_data):
        """Налаштовує таймер з збережених даних"""
        self.timer.elapsed_time = saved_data.elapsed_time * 1000
        self.timer.start()