"""
Інтерфейси репозиторіїв для роботи з даними
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar
from datetime import datetime

from .models import GameRecord, SavedGame, UserSetting
from ..models import Difficulty

# Узагальнені типи
T = TypeVar('T')  # Тип сутності
K = TypeVar('K')  # Тип ключа (ID)


class IRepository(ABC, Generic[T, K]):
    """Базовий інтерфейс репозиторію"""

    @abstractmethod
    def save(self, entity: T) -> K:
        """Зберігає сутність і повертає її ідентифікатор"""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: K) -> Optional[T]:
        """Отримує сутність за ідентифікатором"""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Отримує всі сутності"""
        pass

    @abstractmethod
    def delete(self, entity_id: K) -> bool:
        """Видаляє сутність за ідентифікатором"""
        pass


class IGameRecordRepository(IRepository[GameRecord, int], ABC):
    """Інтерфейс репозиторію для рекордів ігор"""

    @abstractmethod
    def get_by_difficulty(self, difficulty: Difficulty) -> List[GameRecord]:
        """Отримує записи за рівнем складності"""
        pass

    @abstractmethod
    def get_top_scores(self, limit: int = 10) -> List[GameRecord]:
        """Отримує топ результатів"""
        pass


class ISavedGameRepository(IRepository[SavedGame, int], ABC):
    """Інтерфейс репозиторію для збережених ігор"""

    @abstractmethod
    def get_latest(self) -> Optional[SavedGame]:
        """Отримує останню збережену гру"""
        pass

    @abstractmethod
    def update(self, game: SavedGame) -> bool:
        """Оновлює збережену гру"""
        pass


class IUserSettingsRepository(IRepository[UserSetting, str], ABC):
    """Інтерфейс репозиторію для налаштувань користувача"""

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[UserSetting]:
        """Отримує налаштування за назвою"""
        pass

    @abstractmethod
    def update(self, setting: UserSetting) -> bool:
        """Оновлює налаштування"""
        pass