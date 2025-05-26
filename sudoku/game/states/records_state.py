import pygame
import sys
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from .i_game_state import IGameState
from ...config import WINDOW_SIZE, WHITE, BLACK, BLUE, GRAY, GREEN
from ...models import Difficulty

if TYPE_CHECKING:
    from ..game import Game


class RecordsState(IGameState):
    """Стан показу таблиці рекордів"""

    def __init__(self):
        self.selected_difficulty: Optional[Difficulty] = None
        self.records = []
        self.personal_stats = {}
        self.scroll_offset = 0
        self.max_scroll = 0
        self.difficulty_buttons = {}
        self.back_button = None
        self.records_loaded = False

        # Налаштування інтерфейсу
        self.button_height = 40
        self.record_height = 30
        self.records_per_page = 15
        self.header_height = 150

    def _initialize_buttons(self, font, small_font):
        """Ініціалізує кнопки інтерфейсу"""
        # Кнопки фільтрів по складності
        button_width = 120
        button_spacing = 10
        total_width = len(Difficulty) * button_width + (len(Difficulty) - 1) * button_spacing
        start_x = (WINDOW_SIZE[0] - total_width) // 2

        # Словник для перекладу назв рівнів складності
        difficulty_names = {
            Difficulty.EASY: "Легкий",
            Difficulty.MEDIUM: "Середній",
            Difficulty.HARD: "Важкий"
        }

        for i, difficulty in enumerate(Difficulty):
            x = start_x + i * (button_width + button_spacing)
            rect = pygame.Rect(x, 80, button_width, self.button_height)
            text = difficulty_names.get(difficulty, difficulty.name.capitalize())
            text_surface = small_font.render(text, True, WHITE)
            self.difficulty_buttons[difficulty] = (rect, text_surface)

        # Кнопка "Всі рівні"
        all_rect = pygame.Rect(start_x - button_width - button_spacing, 80, button_width, self.button_height)
        all_text = small_font.render("Всі рівні", True, WHITE)
        self.difficulty_buttons[None] = (all_rect, all_text)

        # Кнопка "Назад"
        self.back_button = (
            pygame.Rect(50, WINDOW_SIZE[1] - 60, 100, self.button_height),
            small_font.render("Назад", True, WHITE)
        )

    def _load_records(self, game: 'Game'):
        """Завантажує рекорди з бази даних"""
        if not game.db_manager:
            self.records = []
            self.personal_stats = {}
            return

        try:
            # Завантажуємо рекорди
            self.records = game.get_leaderboard(self.selected_difficulty, limit=50)

            # Завантажуємо персональну статистику
            self.personal_stats = game.get_personal_stats()

            # Розраховуємо максимальний скрол
            visible_records = min(len(self.records), self.records_per_page)
            self.max_scroll = max(0, len(self.records) - visible_records)

        except Exception as e:
            print(f"Помилка завантаження рекордів: {e}")
            self.records = []
            self.personal_stats = {}

    def _format_time(self, seconds: int) -> str:
        """Форматує час у читабельний вигляд"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _format_date(self, date_str: str) -> str:
        """Форматує дату у читабельний вигляд"""
        if not date_str or date_str == "None":
            return "--"

        try:
            # Спробуємо різні формати дати
            if 'T' in date_str:
                # ISO формат
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Спробуємо стандартний формат SQLite
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # Якщо не вдалося, спробуємо без часу
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

            return date_obj.strftime("%d.%m.%Y %H:%M")
        except:
            # Якщо нічого не спрацювало, повертаємо оригінальний рядок
            return date_str[:16] if len(date_str) > 16 else date_str

    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Ініціалізуємо кнопки, якщо потрібно
            if not self.difficulty_buttons:
                self._initialize_buttons(game.font, game.small_font)

            # Перевіряємо натискання на кнопки складності
            for difficulty, (rect, _) in self.difficulty_buttons.items():
                if rect.collidepoint(x, y):
                    if self.selected_difficulty != difficulty:
                        self.selected_difficulty = difficulty
                        self.records_loaded = False
                        self.scroll_offset = 0
                    break

            # Перевіряємо кнопку "Назад"
            if self.back_button and self.back_button[0].collidepoint(x, y):
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)

        elif event.type == pygame.MOUSEWHEEL:
            # Прокрутка колесом миші
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y))

    def update(self, game: 'Game') -> None:
        """Оновлення стану"""
        if not self.records_loaded:
            self._load_records(game)
            self.records_loaded = True

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення таблиці рекордів"""
        surface.fill(WHITE)

        # Ініціалізуємо кнопки, якщо потрібно
        if not self.difficulty_buttons:
            self._initialize_buttons(game.font, game.small_font)

        # Заголовок
        title_text = game.font.render("ТАБЛИЦЯ РЕКОРДІВ", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 30))
        surface.blit(title_text, title_rect)

        # Кнопки фільтрів
        for difficulty, (rect, text_surface) in self.difficulty_buttons.items():
            # Вибір кольору кнопки
            if difficulty == self.selected_difficulty:
                color = GREEN
            else:
                color = BLUE

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)

            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

        # Персональна статистика
        if self.personal_stats:
            stats_y = 130
            stats_text = f"Ваша статистика: Зіграно ігор: {self.personal_stats.get('total_games', 0)}, " \
                         f"Найкращий час: {self._format_time(self.personal_stats.get('best_time', 0))}"
            stats_surface = game.small_font.render(stats_text, True, BLACK)
            surface.blit(stats_surface, (50, stats_y))

        # Заголовки таблиці
        headers_y = self.header_height + 20
        header_font = game.small_font

        headers = ["#", "Час", "Рівень", "Підказок", "Дата"]
        header_positions = [80, 150, 220, 320, 400]

        for i, (header, x_pos) in enumerate(zip(headers, header_positions)):
            header_surface = header_font.render(header, True, BLACK)
            surface.blit(header_surface, (x_pos, headers_y))

        # Лінія під заголовками
        pygame.draw.line(surface, GRAY, (50, headers_y + 25), (WINDOW_SIZE[0] - 50, headers_y + 25), 2)

        # Відображення рекордів
        if self.records:
            records_start_y = headers_y + 35

            for i, record in enumerate(self.records[self.scroll_offset:self.scroll_offset + self.records_per_page]):
                y_pos = records_start_y + i * self.record_height

                # Номер у загальному рейтингу
                rank = self.scroll_offset + i + 1
                rank_text = header_font.render(str(rank), True, BLACK)
                surface.blit(rank_text, (header_positions[0], y_pos))

                # Час
                time_text = header_font.render(self._format_time(record.completion_time), True, BLACK)
                surface.blit(time_text, (header_positions[1], y_pos))

                # Рівень складності
                difficulty_names = {
                    Difficulty.EASY: "Легкий",
                    Difficulty.MEDIUM: "Середній",
                    Difficulty.HARD: "Важкий"
                }
                diff_text = header_font.render(
                    difficulty_names.get(record.difficulty, record.difficulty.name.capitalize()),
                    True, BLACK
                )
                surface.blit(diff_text, (header_positions[2], y_pos))

                # Кількість підказок
                hints_text = header_font.render(str(record.hints_used), True, BLACK)
                surface.blit(hints_text, (header_positions[3], y_pos))

                # Дата
                date_attr = getattr(record, 'created_at', None) or getattr(record, 'date_played', None) or getattr(
                    record, 'timestamp', None)
                if date_attr:
                    date_text = header_font.render(self._format_date(str(date_attr)), True, BLACK)
                else:
                    date_text = header_font.render("--", True, BLACK)
                surface.blit(date_text, (header_positions[4], y_pos))

                # Чергування кольору фону для кращої читабельності
                if i % 2 == 1:
                    row_rect = pygame.Rect(50, y_pos - 2, WINDOW_SIZE[0] - 100, self.record_height)
                    pygame.draw.rect(surface, (240, 240, 240), row_rect)
        else:
            # Повідомлення про відсутність рекордів
            no_records_text = game.font.render("Рекордів поки немає", True, GRAY)
            no_records_rect = no_records_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            surface.blit(no_records_text, no_records_rect)

        # Кнопка "Назад"
        if self.back_button:
            rect, text_surface = self.back_button
            pygame.draw.rect(surface, BLUE, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

        # Індикатор прокрутки, якщо потрібно
        if len(self.records) > self.records_per_page:
            scroll_info = game.small_font.render(
                f"Записи {self.scroll_offset + 1}-{min(self.scroll_offset + self.records_per_page, len(self.records))} з {len(self.records)}",
                True, GRAY
            )
            surface.blit(scroll_info, (WINDOW_SIZE[0] - 250, WINDOW_SIZE[1] - 30))