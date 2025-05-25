"""
Сервісний шар для бізнес-логіки роботи з базою даних
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from .repositories import IGameRecordRepository, ISavedGameRepository
from .models import GameRecord, SavedGame
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



class SavedGameService:
    """Сервіс для роботи зі збереженими іграми"""

    def __init__(self, repository: ISavedGameRepository):
        self.repository = repository

    def save_game(self, difficulty: Difficulty, grid: List[List[Cell]],
                  solution: List[List[int]], elapsed_time: int, hints_used: int) -> int:
        """Зберігає поточну гру"""
        # Конвертуємо сітку клітинок у JSON-серіалізовану форму
        grid_data = [[cell.to_dict() for cell in row] for row in grid]

        saved_game = SavedGame(
            id=None,
            difficulty=difficulty,
            current_state=grid_data,
            solution=solution,
            elapsed_time=elapsed_time,
            hints_used=hints_used,
            date_saved=datetime.now()
        )

        return self.repository.save(saved_game)

    def load_game(self, game_id: int) -> Optional[SavedGame]:
        """Завантажує збережену гру"""
        return self.repository.get_by_id(game_id)

    def get_all_saves(self) -> List[SavedGame]:
        """Отримує всі збережені ігри"""
        return self.repository.get_all()

    def get_latest_save(self) -> Optional[SavedGame]:
        """Отримує останнє збереження"""
        return self.repository.get_latest()

    def update_save(self, saved_game: SavedGame) -> bool:
        """Оновлює збережену гру"""
        saved_game.date_saved = datetime.now()
        return self.repository.update(saved_game)

    def delete_save(self, game_id: int) -> bool:
        """Видаляє збережену гру"""
        return self.repository.delete(game_id)

    def has_saves(self) -> bool:
        """Перевіряє, чи є збережені ігри"""
        saves = self.repository.get_all()
        return len(saves) > 0
