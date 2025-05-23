"""
Модуль для відображення дошки судоку та інтерфейсу
"""
import pygame
from typing import List, Optional, Tuple, Dict

from ..config import (
    GRID_SIZE, SUB_GRID_SIZE, CELL_SIZE, WINDOW_SIZE,
    BLACK, WHITE, GRAY, BLUE, GREEN, LIGHT_BLUE, LIGHT_BLUE_ALT
)
from ..models import Cell


class SudokuRenderer:
    """Клас для відображення судоку"""
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.cell_size = CELL_SIZE

    def draw_grid(self, surface: pygame.Surface, grid: List[List[Cell]], selected_cell: Optional[Tuple[int, int]]):
        """Малює сітку судоку"""
        # Малювання клітинок
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = grid[row][col]
                rect = pygame.Rect(col * self.cell_size, row * self.cell_size,
                                   self.cell_size, self.cell_size)

                # Встановлення кольору фону клітинки
                bg_color = WHITE
                if selected_cell and selected_cell[0] == row and selected_cell[1] == col:
                    bg_color = LIGHT_BLUE  # Світло-блакитний для виділеної клітинки
                elif selected_cell and (selected_cell[0] == row or selected_cell[1] == col):
                    bg_color = LIGHT_BLUE_ALT  # Світло-синій для виділеного рядка/колонки

                pygame.draw.rect(surface, bg_color, rect)

                # Малювання значення клітинки
                if cell.value != 0:
                    color = BLACK if cell.is_fixed or cell.is_valid else pygame.Color("red")
                    text = self.font.render(str(cell.value), True, color)
                    text_rect = text.get_rect(
                        center=(col * self.cell_size + self.cell_size // 2,
                               row * self.cell_size + self.cell_size // 2)
                    )
                    surface.blit(text, text_rect)
                # Малювання заміток
                elif len(cell.notes) > 0:
                    for note in cell.notes:
                        # Визначення позиції для кожної примітки (3x3 сітка всередині клітинки)
                        note_row = (note - 1) // 3
                        note_col = (note - 1) % 3
                        note_x = col * self.cell_size + note_col * (self.cell_size // 3) + self.cell_size // 6
                        note_y = row * self.cell_size + note_row * (self.cell_size // 3) + self.cell_size // 6

                        text = self.small_font.render(str(note), True, GRAY)
                        text_rect = text.get_rect(center=(note_x, note_y))
                        surface.blit(text, text_rect)

        # Малювання ліній сітки
        for i in range(GRID_SIZE + 1):
            line_thickness = 3 if i % SUB_GRID_SIZE == 0 else 1

            # Горизонтальні лінії
            pygame.draw.line(
                surface,
                BLACK,
                (0, i * self.cell_size),
                (GRID_SIZE * self.cell_size, i * self.cell_size),
                line_thickness
            )

            # Вертикальні лінії
            pygame.draw.line(
                surface,
                BLACK,
                (i * self.cell_size, 0),
                (i * self.cell_size, GRID_SIZE * self.cell_size),
                line_thickness
            )

    def draw_blurred_grid(self, surface: pygame.Surface):
        """Малює розмиту сітку для стану паузи"""
        # Створюємо напівпрозорий overlay
        overlay = pygame.Surface((GRID_SIZE * self.cell_size, GRID_SIZE * self.cell_size))
        overlay.set_alpha(200)
        overlay.fill(GRAY)

        # Малюємо основну структуру сітки без значень
        for i in range(GRID_SIZE + 1):
            line_thickness = 3 if i % SUB_GRID_SIZE == 0 else 1

            # Горизонтальні лінії
            pygame.draw.line(
                overlay,
                BLACK,
                (0, i * self.cell_size),
                (GRID_SIZE * self.cell_size, i * self.cell_size),
                line_thickness
            )

            # Вертикальні лінії
            pygame.draw.line(
                overlay,
                BLACK,
                (i * self.cell_size, 0),
                (i * self.cell_size, GRID_SIZE * self.cell_size),
                line_thickness
            )

        surface.blit(overlay, (0, 0))

    def draw_buttons(self, surface: pygame.Surface, buttons: Dict):
        """Малює кнопки керування грою"""
        for button_name, button in buttons.items():
            rect, text = button
            pygame.draw.rect(surface, BLUE, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)  # Рамка кнопки
            surface.blit(text, text.get_rect(center=rect.center))

    def draw_timer(self, surface: pygame.Surface, time_str: str):
        """Малює таймер"""
        timer_text = self.font.render(f"Час: {time_str}", True, BLACK)
        timer_rect = timer_text.get_rect()
        # Розміщуємо таймер під сіткою, але над кнопками
        timer_rect.topleft = (10, GRID_SIZE * self.cell_size + 5)
        surface.blit(timer_text, timer_rect)

    def draw_pause_message(self, surface: pygame.Surface):
        """Малює повідомлення про паузу"""
        # Створюємо напівпрозорий фон для повідомлення
        message_width = 350
        message_height = 120
        message_bg = pygame.Surface((message_width, message_height))
        message_bg.set_alpha(240)
        message_bg.fill(WHITE)

        # Центруємо повідомлення відносно ігрової області (без UI)
        game_area_center_x = (GRID_SIZE * self.cell_size) // 2
        game_area_center_y = (GRID_SIZE * self.cell_size) // 2

        message_rect = message_bg.get_rect(center=(game_area_center_x, game_area_center_y))
        surface.blit(message_bg, message_rect)

        # Рамка навколо повідомлення
        pygame.draw.rect(surface, BLACK, message_rect, 3)

        # Текст повідомлення
        pause_text = self.font.render("ПАУЗА", True, BLACK)
        pause_rect = pause_text.get_rect(center=(game_area_center_x, game_area_center_y - 15))
        surface.blit(pause_text, pause_rect)

        # Інструкція
        instruction_text = self.small_font.render("Натисніть 'P' або 'Пробіл' для продовження", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(game_area_center_x, game_area_center_y + 15))
        surface.blit(instruction_text, instruction_rect)

    def draw_game_over(self, surface: pygame.Surface):
        """Малює повідомлення про завершення гри"""
        # Напівпрозорий overlay тільки для ігрової області
        overlay = pygame.Surface((GRID_SIZE * self.cell_size, GRID_SIZE * self.cell_size))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        # Центруємо повідомлення відносно ігрової області
        game_area_center_x = (GRID_SIZE * self.cell_size) // 2
        game_area_center_y = (GRID_SIZE * self.cell_size) // 2

        text = self.font.render("Вітаємо! Ви розв'язали Судоку!", True, GREEN)
        text_rect = text.get_rect(center=(game_area_center_x, game_area_center_y))
        surface.blit(text, text_rect)

        subtext = self.small_font.render("Натисніть 'Н', щоб почати нову гру", True, WHITE)
        subtext_rect = subtext.get_rect(center=(game_area_center_x, game_area_center_y + 40))
        surface.blit(subtext, subtext_rect)