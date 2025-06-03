"""
Модуль для валідації судоку
"""
from typing import List

from ..config import GRID_SIZE, SUB_GRID_SIZE
from ..models import Cell


class SudokuValidator:
    """Клас для валідації судоку"""

    @staticmethod
    def is_valid_move(grid: List[List[Cell]], row: int, col: int, value: int) -> bool:
        """Перевіряє, чи є хід правильним"""
        if value == 0:
            return True
        return all([
            SudokuValidator.__is_column_valid_move(grid, row, col, value),
            SudokuValidator.__is_row_valid_move(grid, row, col, value),
            SudokuValidator.__is_block_valid_move(grid, row, col, value)
        ])

    @staticmethod
    def is_board_valid(grid: List[List[Cell]]) -> bool:
        """Перевіряє, чи є поточний стан дошки правильним"""
        return all([
            SudokuValidator.__is_row_valid_board(grid),
            SudokuValidator.__is_column_valid_board(grid),
            SudokuValidator.__is_block_valid_board(grid)
        ])

    @staticmethod
    def is_board_complete(grid: List[List[Cell]]) -> bool:
        """Перевіряє, чи заповнена вся дошка без нулів"""
        return all(grid[row][col].value != 0 for row in range(GRID_SIZE) for col in range(GRID_SIZE))

    @staticmethod
    def __has_unique_values(values: List[int]) -> bool:
        return len(values) == len(set(values))

    @staticmethod
    def __is_column_valid_board(grid: List[List[Cell]]) -> bool:
        return all(SudokuValidator.__has_unique_values(
            [grid[row][col].value for row in range(GRID_SIZE) if grid[row][col].value != 0])
                   for col in range(GRID_SIZE))

    @staticmethod
    def __is_row_valid_board(grid: List[List[Cell]]) -> bool:
        return all(SudokuValidator.__has_unique_values(
            [grid[row][col].value for col in range(GRID_SIZE) if grid[row][col].value != 0])
                   for row in range(GRID_SIZE))

    @staticmethod
    def __is_block_valid_move(grid: List[List[Cell]], row: int, col: int, value: int) -> bool:
        start_row = row - row % SUB_GRID_SIZE
        start_col = col - col % SUB_GRID_SIZE
        for i in range(SUB_GRID_SIZE):
            for j in range(SUB_GRID_SIZE):
                r, c = start_row + i, start_col + j
                if (r != row or c != col) and grid[r][c].value == value:
                    return False
        return True

    @staticmethod
    def __is_column_valid_board(grid: List[List[Cell]]) -> bool:
        for col in range(GRID_SIZE):
            values = [grid[row][col].value for row in range(GRID_SIZE) if grid[row][col].value != 0]
            if len(values) != len(set(values)):
                return False
        return True

    @staticmethod
    def __is_row_valid_board(grid: List[List[Cell]]) -> bool:
        for row in range(GRID_SIZE):
            values = [grid[row][col].value for col in range(GRID_SIZE) if grid[row][col].value != 0]
            if len(values) != len(set(values)):
                return False
        return True

    @staticmethod
    def __is_block_valid_board(grid: List[List[Cell]]) -> bool:
        for block_row in range(0, GRID_SIZE, SUB_GRID_SIZE):
            for block_col in range(0, GRID_SIZE, SUB_GRID_SIZE):
                values = []
                for row in range(block_row, block_row + SUB_GRID_SIZE):
                    for col in range(block_col, block_col + SUB_GRID_SIZE):
                        if grid[row][col].value != 0:
                            values.append(grid[row][col].value)
                if len(values) != len(set(values)):
                    return False
        return True