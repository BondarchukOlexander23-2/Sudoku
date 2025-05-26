import pygame
from typing import TYPE_CHECKING

from .i_game_state import IGameState
from ...config import WHITE

if TYPE_CHECKING:
    from ..game import Game


class GameOverState(IGameState):
    """Стан гри після завершення"""
    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                from .difficulty_select_state import DifficultySelectState
                game.set_state(DifficultySelectState())
            elif event.key == pygame.K_ESCAPE:
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Можна додати кнопки для нової гри або повернення в меню
            pass

    def update(self, game: 'Game') -> None:
        # Таймер не оновлюється після завершення гри
        pass

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        # Спочатку відображаємо ігрову дошку
        surface.fill(WHITE)
        game.renderer.draw_grid(surface, game.board.grid, None)
        game.renderer.draw_buttons(surface, game.button_manager.buttons)

        # Відображення фінального часу
        game.renderer.draw_timer(surface, game.timer.get_formatted_time())

        # Потім відображаємо повідомлення про завершення
        game.renderer.draw_game_over(surface)