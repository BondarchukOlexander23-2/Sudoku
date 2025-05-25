"""
Пакет для роботи з базою даних
"""

from .models import GameRecord, SavedGame
from .repositories import IGameRecordRepository, ISavedGameRepository
from .sqlite_repositories import SQLiteGameRecordRepository, SQLiteSavedGameRepository
from .database_manager import DatabaseManager
from .services import GameRecordService, SavedGameService


__all__ = [
    # Models
    'GameRecord','SavedGame',
    # Repository interfaces
    'IGameRecordRepository', 'ISavedGameRepository',
    # Repository implementations
    'SQLiteGameRecordRepository', 'SQLiteSavedGameRepository',
    # Database manager
    'DatabaseManager',
    # Services
    'GameRecordService', 'SavedGameService',
]
