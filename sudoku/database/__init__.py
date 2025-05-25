"""
Пакет для роботи з базою даних
"""

from .models import GameRecord
from .repositories import IGameRecordRepository
from .sqlite_repositories import SQLiteGameRecordRepository
from .database_manager import DatabaseManager
from .services import GameRecordService


__all__ = [
    # Models
    'GameRecord',
    # Repository interfaces
    'IGameRecordRepository',
    # Repository implementations
    'SQLiteGameRecordRepository',
    # Database manager
    'DatabaseManager',
    # Services
    'GameRecordService'
]
