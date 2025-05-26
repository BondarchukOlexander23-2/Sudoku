import pygame
from typing import TYPE_CHECKING

from .i_game_state import IGameState
from ...config import WINDOW_SIZE, WHITE, BLUE, BLACK, GRAY
from ...models import Difficulty

if TYPE_CHECKING:
    from ..game import Game

class DifficultySelectState(IGameState):
    """Стан вибору складності"""
    def __init__(self):
        self.difficulty_buttons = {}
        self.back_button = None
        self.button_width = 200
        self.button_height = 50
        self.button_spacing = 20

    def _initialize_difficulty_buttons(self, font):
        """Ініціалізує кнопки вибору складності"""
        center_x = WINDOW_SIZE[0] // 2
        start_y = WINDOW_SIZE[1] // 2 - 80

        difficulties = [
            (Difficulty.EASY, "Легко"),
            (Difficulty.MEDIUM, "Середньо"),
            (Difficulty.HARD, "Важко")
        ]

        for i, (difficulty, text) in enumerate(difficulties):
            y = start_y + i * (self.button_height + self.button_spacing)
            rect = pygame.Rect(
                center_x - self.button_width // 2,
                y,
                self.button_width,
                self.button_height
            )
            text_surface = font.render(text, True, WHITE)
            self.difficulty_buttons[difficulty] = (rect, text_surface)

        # Кнопка повернення
        back_y = start_y + len(difficulties) * (self.button_height + self.button_spacing) + 20
        back_rect = pygame.Rect(
            center_x - 100,
            back_y,
            200,
            40
        )
        back_text = font.render("Назад", True, WHITE)
        self.back_button = (back_rect, back_text)

    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Ініціалізуємо кнопки, якщо вони ще не створені
            if not self.difficulty_buttons:
                self._initialize_difficulty_buttons(game.font)

            # Перевірка натискання на кнопки складності
            for difficulty, (rect, _) in self.difficulty_buttons.items():
                if rect.collidepoint(x, y):
                    game.difficulty = difficulty
                    game.new_game()
                    # Імпортуємо тут, щоб уникнути циркулярного імпорту
                    from .playing_state import PlayingState
                    game.set_state(PlayingState())
                    return

            # Перевірка натискання на кнопку "Назад"
            if self.back_button and self.back_button[0].collidepoint(x, y):
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())

    def update(self, game: 'Game') -> None:
        """Оновлення стану вибору складності"""
        pass

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення меню вибору складності"""
        surface.fill(WHITE)

        # Ініціалізуємо кнопки, якщо вони ще не створені
        if not self.difficulty_buttons:
            self._initialize_difficulty_buttons(game.font)

        # Заголовок
        title_text = game.font.render("Оберіть складність", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 150))
        surface.blit(title_text, title_rect)

        # Малювання кнопок складності
        for difficulty, (rect, text_surface) in self.difficulty_buttons.items():
            pygame.draw.rect(surface, BLUE, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)

            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

        # Малювання кнопки "Назад"
        if self.back_button:
            rect, text_surface = self.back_button
            pygame.draw.rect(surface, GRAY, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)

            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)