"""
Інтерфейси репозиторіїв для роботи з даними
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .models import GameRecord
from ..models import Difficulty


class IGameRecordRepository(ABC):
    """Інтерфейс репозиторію для рекордів ігор"""

    @abstractmethod
    def save(self, record: GameRecord) -> int:
        """Зберігає запис про гру і повертає ID"""
        pass

    @abstractmethod
    def get_by_id(self, record_id: int) -> Optional[GameRecord]:
        """Отримує запис за ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[GameRecord]:
        """Отримує всі записи"""
        pass

    @abstractmethod
    def get_by_difficulty(self, difficulty: Difficulty) -> List[GameRecord]:
        """Отримує записи за рівнем складності"""
        pass

    @abstractmethod
    def get_top_scores(self, limit: int = 10) -> List[GameRecord]:
        """Отримує топ результатів"""
        pass

    @abstractmethod
    def delete(self, record_id: int) -> bool:
        """Видаляє запис"""
        pass
