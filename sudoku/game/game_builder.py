"""
Builder для створення об'єкта гри з правильно налаштованими компонентами
"""
import pygame
import logging
from typing import Optional

from ..config import WINDOW_SIZE
from ..models import Difficulty
from ..core import SudokuGenerator, SudokuBoard
from ..ui import SudokuRenderer, ButtonManager
from .timer import GameTimer
from .database_integration import GameDatabaseManager


class GameBuilder:
    """Builder для поетапного створення гри"""

    def __init__(self):
        self.window_size = None
        self.surface = None
        self.font = None
        self.small_font = None
        self.generator = None
        self.board = None
        self.renderer = None
        self.button_manager = None
        self.timer = None
        self.db_manager = None

    def build_pygame(self):
        """Ініціалізує Pygame та створює вікно"""
        pygame.init()
        self.window_size = WINDOW_SIZE
        self.surface = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Судоку')
        return self

    def build_fonts(self):
        """Створює шрифти для гри"""
        self.font = pygame.font.SysFont('Comic Sans MS', 32)
        self.small_font = pygame.font.SysFont('Comic Sans MS', 16)
        return self

    def build_components(self):
        """Створює основні ігрові компоненти"""
        self.generator = SudokuGenerator()
        self.board = SudokuBoard(self.generator)
        self.renderer = SudokuRenderer(self.font, self.small_font)
        self.button_manager = ButtonManager(self.small_font)
        self.timer = GameTimer()
        return self

    def build_database(self, db_path: Optional[str] = None):
        """Ініціалізує базу даних"""
        if db_path:
            try:
                self.db_manager = GameDatabaseManager(db_path)
            except Exception as e:
                logging.error(f"Failed to initialize database: {e}")
                self.db_manager = None
        return self

    def build(self):
        """Створює та повертає словник з усіма компонентами"""
        return {
            'window_size': self.window_size,
            'surface': self.surface,
            'font': self.font,
            'small_font': self.small_font,
            'generator': self.generator,
            'board': self.board,
            'renderer': self.renderer,
            'button_manager': self.button_manager,
            'timer': self.timer,
            'db_manager': self.db_manager
        }