"""
Модуль для станів гри
"""
from abc import ABC, abstractmethod
import pygame
from typing import TYPE_CHECKING

from ..config import GRID_SIZE, CELL_SIZE, BLACK, WHITE
from ..models import Difficulty

if TYPE_CHECKING:
    from .game import Game


class IGameState(ABC):
    """Інтерфейс для стану гри"""
    @abstractmethod
    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        """Обробляє подію гри"""
        pass

    @abstractmethod
    def update(self, game: 'Game') -> None:
        """Оновлює стан гри"""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображує стан гри"""
        pass


class PlayingState(IGameState):
    """Стан гри під час гри"""
    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Перевірка натискання на кнопки
            clicked_button = game.button_manager.get_clicked_button(x, y)
            if clicked_button:
                self._handle_button_click(clicked_button, game)
                return

            # Вибір клітинки
            if y < GRID_SIZE * CELL_SIZE:  # У межах сітки
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                game.select_cell(row, col)

        elif event.type == pygame.KEYDOWN:
            self._handle_key_press(event.key, game)

    def _handle_button_click(self, button_name: str, game: 'Game') -> None:
        """Обробка натискання кнопок"""
        if button_name == "new_game":
            game.new_game()
        elif button_name == "hint":
            game.use_hint()
        elif button_name == "auto_notes":
            game.board.auto_notes()
        elif button_name == "difficulty":
            # Циклічна зміна складності
            difficulties = list(Difficulty)
            current_index = difficulties.index(game.difficulty)
            next_index = (current_index + 1) % len(difficulties)
            game.difficulty = difficulties[next_index]
            game.button_manager.update_difficulty_button(game.difficulty.name)

    def _handle_key_press(self, key: int, game: 'Game') -> None:
        """Обробка натискання клавіш"""
        if game.selected_cell:
            row, col = game.selected_cell

            if key == pygame.K_BACKSPACE or key == pygame.K_DELETE or key == pygame.K_0:
                game.board.clear_cell(row, col)
            elif pygame.K_1 <= key <= pygame.K_9:
                number = key - pygame.K_0

                # Якщо натиснуто Shift, додаємо/видаляємо замітку
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    game.board.toggle_note(row, col, number)
                else:
                    game.board.set_value(row, col, number)

                    # Перевірка на завершення гри
                    if game.board.is_complete():
                        game.set_state(GameOverState())

            # Навігація стрілками
            elif key == pygame.K_UP and row > 0:
                game.select_cell(row - 1, col)
            elif key == pygame.K_DOWN and row < GRID_SIZE - 1:
                game.select_cell(row + 1, col)
            elif key == pygame.K_LEFT and col > 0:
                game.select_cell(row, col - 1)
            elif key == pygame.K_RIGHT and col < GRID_SIZE - 1:
                game.select_cell(row, col + 1)

        # Гарячі клавіші
        if key == pygame.K_n:  # Нова гра
            game.new_game()
        elif key == pygame.K_h:  # Підказка
            game.use_hint()
        elif key == pygame.K_a:  # Автозаповнення заміток
            game.board.auto_notes()

    def update(self, game: 'Game') -> None:
        """Оновлення стану гри"""
        pass

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення стану гри"""
        surface.fill(WHITE)

        # Відображення сітки
        game.renderer.draw_grid(surface, game.board.grid, game.selected_cell)

        # Відображення кнопок
        game.renderer.draw_buttons(surface, game.button_manager.buttons)

        # Відображення кількості використаних підказок
        hints_text = game.small_font.render(
            f"Підказки: {game.board.hints_used}/{game.board.max_hints}",
            True, BLACK
        )
        surface.blit(hints_text, (10, game.window_size[1] - 30))


class GameOverState(IGameState):
    """Стан гри після завершення"""
    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                game.new_game()
                game.set_state(PlayingState())

    def update(self, game: 'Game') -> None:
        pass

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        # Спочатку відображаємо ігрову дошку
        surface.fill(WHITE)
        game.renderer.draw_grid(surface, game.board.grid, None)
        game.renderer.draw_buttons(surface, game.button_manager.buttons)

        # Потім відображаємо повідомлення про завершення
        game.renderer.draw_game_over(surface)