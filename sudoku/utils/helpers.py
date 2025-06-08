"""
Допоміжні функції та утиліти
"""
from typing import List, Tuple
from ..config import GRID_SIZE, SUB_GRID_SIZE


def get_block_coordinates(row: int, col: int) -> List[Tuple[int, int]]:
    """Повертає координати всіх клітинок у блоці 3x3

    Args:
        row (int): Рядок клітинки
        col (int): Колонка клітинки

    Returns:
        List[Tuple[int, int]]: Список координат у блоці
    """
    start_row = row - row % SUB_GRID_SIZE
    start_col = col - col % SUB_GRID_SIZE

    return [
        (start_row + i, start_col + j)
        for i in range(SUB_GRID_SIZE)
        for j in range(SUB_GRID_SIZE)
    ]


def get_row_coordinates(row: int) -> List[Tuple[int, int]]:
    """Повертає координати всіх клітинок у рядку"""
    return [(row, col) for col in range(GRID_SIZE)]


def get_col_coordinates(col: int) -> List[Tuple[int, int]]:
    """Повертає координати всіх клітинок у колонці"""
    return [(row, col) for row in range(GRID_SIZE)]


def is_valid_coordinate(row: int, col: int) -> bool:
    """Перевіряє, чи є координати дійсними для сітки судоку"""
    return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE


def format_time(seconds: int) -> str:
    """Форматує час у хвилини:секунди"""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def calculate_difficulty_score(difficulty_name: str, time_seconds: int, hints_used: int) -> int:
    """Обчислює бал на основі складності, часу та використаних підказок

    Args:
        difficulty_name (str): Назва складності (EASY, MEDIUM, HARD)
        time_seconds (int): Час проходження у секундах
        hints_used (int): Кількість використаних підказок

    Returns:
        int: Розрахований фінальний бал
    """
    base_scores = {
        'EASY': 100,
        'MEDIUM': 200,
        'HARD': 300
    }

    base_score = base_scores.get(difficulty_name.upper())
    if base_score is None:
        print(f"[WARNING] Невідома складність: '{difficulty_name}', використовується EASY за замовчуванням.")
        base_score = base_scores['EASY']

    time_penalty = min(time_seconds // 60, base_score // 2)
    hint_penalty = hints_used * 20

    final_score = max(0, base_score - time_penalty - hint_penalty)
    return final_score
