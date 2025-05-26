import pygame
import sys
from typing import TYPE_CHECKING

from .i_game_state import IGameState
from ...config import WINDOW_SIZE, WHITE, BLACK, BLUE, GRAY

if TYPE_CHECKING:
    from ..game import Game


class MainMenuState(IGameState):
    """Стан головного меню"""
    def __init__(self):
        self.menu_buttons = {}
        self.button_width = 200
        self.button_height = 50
        self.button_spacing = 20

    def _initialize_menu_buttons(self, font):
        """Ініціалізує кнопки головного меню"""
        center_x = WINDOW_SIZE[0] // 2
        start_y = WINDOW_SIZE[1] // 2 - 100

        buttons_data = [
            ("play", "Грати"),
            ("continue", "Продовжити"),
            ("records", "Рекорди"),
            ("exit", "Вийти")
        ]

        for i, (key, text) in enumerate(buttons_data):
            y = start_y + i * (self.button_height + self.button_spacing)
            rect = pygame.Rect(
                center_x - self.button_width // 2,
                y,
                self.button_width,
                self.button_height
            )
            text_surface = font.render(text, True, WHITE)
            self.menu_buttons[key] = (rect, text_surface)

    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Ініціалізуємо кнопки, якщо вони ще не створені
            if not self.menu_buttons:
                self._initialize_menu_buttons(game.font)

            for button_name, (rect, _) in self.menu_buttons.items():
                if rect.collidepoint(x, y):
                    self._handle_menu_click(button_name, game)
                    break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def _handle_menu_click(self, button_name: str, game: 'Game') -> None:
        """Обробка натискання кнопок меню"""
        if button_name == "play":
            # Імпортуємо тут, щоб уникнути циркулярного імпорту
            from .difficulty_select_state import DifficultySelectState
            game.set_state(DifficultySelectState())
        elif button_name == "continue":
            # TODO: Реалізувати завантаження збереженої гри з БД
            pass
        elif button_name == "records":
            # TODO: Реалізувати показ таблиці рекордів з БД
            pass
        elif button_name == "exit":
            pygame.quit()
            sys.exit()

    def update(self, game: 'Game') -> None:
        """Оновлення стану меню"""
        pass

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення головного меню"""
        surface.fill(WHITE)

        # Ініціалізуємо кнопки, якщо вони ще не створені
        if not self.menu_buttons:
            self._initialize_menu_buttons(game.font)

        # Заголовок
        title_text = game.font.render("СУДОКУ", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 100))
        surface.blit(title_text, title_rect)

        # Малювання кнопок меню
        for button_name, (rect, text_surface) in self.menu_buttons.items():
            # Вибір кольору кнопки
            button_color = BLUE
            if button_name in ["continue", "records"]:
                button_color = GRAY  # Неактивні кнопки

            pygame.draw.rect(surface, button_color, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)

            # Центрування тексту на кнопці
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)
