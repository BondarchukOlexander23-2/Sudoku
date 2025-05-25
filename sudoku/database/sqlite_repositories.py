"""
SQLite реалізації репозиторіїв
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from .repositories import IGameRecordRepository
from .models import GameRecord
from .database_manager import DatabaseManager
from ..models import Difficulty


class SQLiteGameRecordRepository(IGameRecordRepository):
    """SQLite реалізація репозиторію для рекордів ігор"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save(self, record: GameRecord) -> int:
        """Зберігає запис про гру і повертає ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            INSERT INTO game_records (difficulty, completion_time, hints_used, score, date_completed)
            VALUES (?, ?, ?, ?, ?)
        """, (
            record.difficulty.name,
            record.completion_time,
            record.hints_used,
            record.score,
            record.date_completed.isoformat()
        ))

        conn.commit()
        return cursor.lastrowid

    def get_by_id(self, record_id: int) -> Optional[GameRecord]:
        """Отримує запис за ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM game_records WHERE id = ?
        """, (record_id,))

        row = cursor.fetchone()
        if row:
            return GameRecord.from_dict(dict(row))
        return None

    def get_all(self) -> List[GameRecord]:
        """Отримує всі записи"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM game_records ORDER BY date_completed DESC
        """)

        return [GameRecord.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_by_difficulty(self, difficulty: Difficulty) -> List[GameRecord]:
        """Отримує записи за рівнем складності"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM game_records 
            WHERE difficulty = ? 
            ORDER BY score DESC, completion_time ASC
        """, (difficulty.name,))

        return [GameRecord.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_top_scores(self, limit: int = 10) -> List[GameRecord]:
        """Отримує топ результатів"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM game_records 
            ORDER BY score DESC, completion_time ASC 
            LIMIT ?
        """, (limit,))

        return [GameRecord.from_dict(dict(row)) for row in cursor.fetchall()]

    def delete(self, record_id: int) -> bool:
        """Видаляє запис"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            DELETE FROM game_records WHERE id = ?
        """, (record_id,))

        conn.commit()
        return cursor.rowcount > 0