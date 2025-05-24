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
        self.button_height = 35
        self.button_y = GRID_SIZE * CELL_SIZE + 50  # Рядок для кнопок

    def initialize_buttons(self):
        """Ініціалізує кнопки інтерфейсу в один рядок"""
        margin_left = 10
        spacing = 10
        current_x = margin_left
        y = self.button_y

        # Кнопка нової гри (тепер веде до вибору складності)
        new_game_text = self.small_font.render("Нова гра", True, WHITE)
        new_game_rect = pygame.Rect(current_x, y, 90, self.button_height)
        self.buttons["new_game"] = (new_game_rect, new_game_text)
        current_x += 90 + spacing

        # Кнопка підказки
        hint_text = self.small_font.render("Підказка", True, WHITE)
        hint_rect = pygame.Rect(current_x, y, 80, self.button_height)
        self.buttons["hint"] = (hint_rect, hint_text)
        current_x += 80 + spacing

        # Кнопка паузи
        pause_text = self.small_font.render("Пауза", True, WHITE)
        pause_rect = pygame.Rect(current_x, y, 70, self.button_height)
        self.buttons["pause"] = (pause_rect, pause_text)
        current_x += 70 + spacing

        # Кнопка авто-заміток
        auto_notes_text = self.small_font.render("Авто-замітки", True, WHITE)
        auto_notes_rect = pygame.Rect(current_x, y, 110, self.button_height)
        self.buttons["auto_notes"] = (auto_notes_rect, auto_notes_text)
        current_x += 110 + spacing

        # Кнопка меню (замість кнопки складності)
        menu_text = self.small_font.render("Меню", True, WHITE)
        menu_rect = pygame.Rect(current_x, y, 70, self.button_height)
        self.buttons["menu"] = (menu_rect, menu_text)

    def update_pause_button(self, text: str):
        """Оновлює текст кнопки паузи"""
        pause_text = self.small_font.render(text, True, WHITE)
        pause_rect = pygame.Rect(10 + 90 + 10 + 80, self.button_y, 70, self.button_height)
        self.buttons["pause"] = (pause_rect, pause_text)

    def get_clicked_button(self, x: int, y: int) -> str:
        """Повертає назву кнопки, на яку натиснули, або пусту строку"""
        for button_name, (rect, _) in self.buttons.items():
            if rect.collidepoint(x, y):
                return button_name
        return ""