"""
Модуль для рівнів складності гри
"""
from enum import Enum


class Difficulty(Enum):
    """Перелік рівнів складності гри"""
    EASY = 80  # Кількість відкритих клітинок
    MEDIUM = 25
    HARD = 20