"""
Сервісний шар для бізнес-логіки роботи з базою даних
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from .repositories import IGameRecordRepository
from .models import GameRecord
from ..models import Difficulty, Cell
from ..utils.helpers import calculate_difficulty_score


class GameRecordService:
    """Сервіс для роботи з рекордами ігор"""

    def __init__(self, repository: IGameRecordRepository):
        self.repository = repository

    def save_game_record(self, difficulty: Difficulty, completion_time: int, hints_used: int) -> int:
        """Зберігає новий рекорд гри"""
        score = calculate_difficulty_score(difficulty.name, completion_time, hints_used)

        record = GameRecord(
            id=None,
            difficulty=difficulty,
            completion_time=completion_time,
            hints_used=hints_used,
            score=score,
            date_completed=datetime.now()
        )

        return self.repository.save(record)

    def get_leaderboard(self, difficulty: Optional[Difficulty] = None, limit: int = 10) -> List[GameRecord]:
        """Отримує таблицю лідерів"""
        if difficulty:
            records = self.repository.get_by_difficulty(difficulty)
            return records[:limit]
        else:
            return self.repository.get_top_scores(limit)

    def get_personal_stats(self) -> Dict[str, Any]:
        """Отримує персональну статистику гравця"""
        all_records = self.repository.get_all()

        if not all_records:
            return {
                'total_games': 0,
                'total_time': 0,
                'average_time': 0,
                'best_scores': {},
                'games_by_difficulty': {}
            }

        stats = {
            'total_games': len(all_records),
            'total_time': sum(r.completion_time for r in all_records),
            'average_time': sum(r.completion_time for r in all_records) // len(all_records),
            'best_scores': {},
            'games_by_difficulty': {}
        }

        # Статистика по складності
        for difficulty in Difficulty:
            difficulty_records = [r for r in all_records if r.difficulty == difficulty]
            if difficulty_records:
                best_record = max(difficulty_records, key=lambda x: x.score)
                stats['best_scores'][difficulty.name] = {
                    'score': best_record.score,
                    'time': best_record.completion_time,
                    'hints_used': best_record.hints_used
                }
                stats['games_by_difficulty'][difficulty.name] = len(difficulty_records)

        return stats

    def delete_record(self, record_id: int) -> bool:
        """Видаляє запис"""
        return self.repository.delete(record_id)

