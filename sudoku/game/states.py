"""
Модуль для станів гри з головним меню та вибором складності
"""
from abc import ABC, abstractmethod
import pygame
import sys
from typing import TYPE_CHECKING

from ..config import GRID_SIZE, CELL_SIZE, BLACK, WHITE, WINDOW_SIZE, BLUE, GRAY
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
        """Відображає стан гри"""
        pass


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
                    game.set_state(PlayingState())
                    return

            # Перевірка натискання на кнопку "Назад"
            if self.back_button and self.back_button[0].collidepoint(x, y):
                game.set_state(MainMenuState())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
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
            if event.key == pygame.K_ESCAPE:
                game.set_state(MainMenuState())
            else:
                self._handle_key_press(event.key, game)

    def _handle_button_click(self, button_name: str, game: 'Game') -> None:
        """Обробка натискання кнопок"""
        if button_name == "new_game":
            game.set_state(DifficultySelectState())
        elif button_name == "hint":
            game.use_hint()
        elif button_name == "auto_notes":
            game.board.auto_notes()
        elif button_name == "pause":
            game.pause_game()
        elif button_name == "menu":
            game.set_state(MainMenuState())

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
        if key == pygame.K_h:  # Підказка
            game.use_hint()
        elif key == pygame.K_a:  # Автозаповнення заміток
            game.board.auto_notes()
        elif key == pygame.K_p or key == pygame.K_SPACE:  # Пауза
            game.pause_game()

    def update(self, game: 'Game') -> None:
        """Оновлення стану гри"""
        # Оновлюємо таймер тільки якщо гра не на паузі
        game.timer.update()

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення стану гри"""
        surface.fill(WHITE)

        # Відображення сітки
        game.renderer.draw_grid(surface, game.board.grid, game.selected_cell)

        # Відображення кнопок
        game.renderer.draw_buttons(surface, game.button_manager.buttons)

        # Відображення таймеру
        game.renderer.draw_timer(surface, game.timer.get_formatted_time())

        # Відображення кількості використаних підказок
        second_row_y = GRID_SIZE * CELL_SIZE + 95  # Під другим рядом кнопок
        hints_text = game.small_font.render(
            f"Підказки: {game.board.hints_used}/{game.board.max_hints}",
            True, BLACK
        )
        surface.blit(hints_text, (10, second_row_y))


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


class GameOverState(IGameState):
    """Стан гри після завершення"""
    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                game.set_state(DifficultySelectState())
            elif event.key == pygame.K_ESCAPE:
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