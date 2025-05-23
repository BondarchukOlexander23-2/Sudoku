"""
Модуль для управління кнопками інтерфейсу
"""
import pygame
from typing import Dict, Tuple

from ..config import GRID_SIZE, CELL_SIZE, WHITE


class ButtonManager:
    """Клас для управління кнопками інтерфейсу"""
    def __init__(self, small_font: pygame.font.Font):
        self.small_font = small_font
        self.buttons: Dict[str, Tuple[pygame.Rect, pygame.Surface]] = {}
        self.button_height = 40
        self.button_y = GRID_SIZE * CELL_SIZE + 10

    def initialize_buttons(self):
        """Ініціалізує кнопки інтерфейсу"""
        # Кнопка нової гри
        new_game_text = self.small_font.render("Нова гра", True, WHITE)
        new_game_rect = pygame.Rect(10, self.button_y, 100, self.button_height)
        self.buttons["new_game"] = (new_game_rect, new_game_text)

        # Кнопка підказки
        hint_text = self.small_font.render("Підказка", True, WHITE)
        hint_rect = pygame.Rect(120, self.button_y, 100, self.button_height)
        self.buttons["hint"] = (hint_rect, hint_text)

        # Кнопка авто-заміток
        auto_notes_text = self.small_font.render("Авто-замітки", True, WHITE)
        auto_notes_rect = pygame.Rect(230, self.button_y, 120, self.button_height)
        self.buttons["auto_notes"] = (auto_notes_rect, auto_notes_text)


    def update_difficulty_button(self, difficulty_name: str):
        """Оновлює текст кнопки складності"""
        difficulty_text = self.small_font.render(f"Складність: {difficulty_name}", True, WHITE)
        difficulty_rect = pygame.Rect(360, self.button_y, 160, self.button_height)
        self.buttons["difficulty"] = (difficulty_rect, difficulty_text)

    def get_clicked_button(self, x: int, y: int) -> str:
        """Повертає назву кнопки, на яку натиснули, або пусту строку"""
        for button_name, (rect, _) in self.buttons.items():
            if rect.collidepoint(x, y):
                return button_name
        return ""