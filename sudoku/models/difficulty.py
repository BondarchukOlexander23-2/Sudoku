"""
Модуль для рівнів складності гри
"""
from enum import Enum


class Difficulty(Enum):
    """Перелік рівнів складності гри"""
    EASY = 40
    MEDIUM = 25
    HARD = 20