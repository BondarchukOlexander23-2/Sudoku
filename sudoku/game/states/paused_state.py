import pygame
from typing import TYPE_CHECKING

from i_game_state import IGameState
from .main_menu_state import MainMenuState
from ...config import WHITE, GRID_SIZE, CELL_SIZE, BLACK

if TYPE_CHECKING:
    from ..game import Game

class PausedState(IGameState):
    """Стан гри на паузі"""
    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Перевірка натискання на кнопки (тільки пауза та меню)
            clicked_button = game.button_manager.get_clicked_button(x, y)
            if clicked_button == "pause":
                game.resume_game()
            elif clicked_button == "menu":
                game.set_state(MainMenuState())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                game.resume_game()
            elif event.key == pygame.K_ESCAPE:
                game.set_state(MainMenuState())

    def update(self, game: 'Game') -> None:
        """Оновлення стану гри на паузі"""
        # Таймер не оновлюється під час паузи
        pass

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення стану гри на паузі"""
        surface.fill(WHITE)

        # Відображення розмитої сітки
        game.renderer.draw_blurred_grid(surface)

        # Відображення кнопок
        game.renderer.draw_buttons(surface, game.button_manager.buttons)

        # Відображення таймеру (зупиненого)
        game.renderer.draw_timer(surface, game.timer.get_formatted_time())

        # Відображення повідомлення про паузу
        game.renderer.draw_pause_message(surface)

        # Відображення кількості використаних підказок
        second_row_y = GRID_SIZE * CELL_SIZE + 95  # Під другим рядом кнопок
        hints_text = game.small_font.render(
            f"Підказки: {game.board.hints_used}/{game.board.max_hints}",
            True, BLACK
        )
        surface.blit(hints_text, (10, second_row_y))
