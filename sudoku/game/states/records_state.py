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
        difficulties = [None] + list(Difficulty)  # None = "Всі рівні"
        button_count = len(difficulties)
        total_spacing = 20  # Загальний простір між кнопками

        # Визначаємо ширину кнопки як частину від загальної ширини вікна
        max_total_button_width = WINDOW_SIZE[0] * 0.9  # 90% ширини вікна
        spacing = 10
        button_width = (max_total_button_width - spacing * (button_count - 1)) // button_count
        start_x = (WINDOW_SIZE[0] - ((button_width + spacing) * button_count - spacing)) // 2

        # Відображувані назви
        difficulty_names = {
            None: "Всі рівні",
            Difficulty.EASY: "Легкий",
            Difficulty.MEDIUM: "Середній",
            Difficulty.HARD: "Важкий"
        }

        # Створюємо кнопки
        self.difficulty_buttons = {}
        for i, difficulty in enumerate(difficulties):
            x = start_x + i * (button_width + spacing)
            rect = pygame.Rect(x, 80, button_width, self.button_height)

            if difficulty is not None:
                text = difficulty_names.get(difficulty, difficulty.name.capitalize())
            else:
                text = "Всі рівні"

            text_surface = small_font.render(text, True, WHITE)
            self.difficulty_buttons[difficulty] = (rect, text_surface)

        # Кнопка "Назад" — фіксовано зліва внизу
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

    def _format_date(self, record) -> str:
        """Форматує дату у читабельний вигляд"""
        # Спочатку отримуємо дату з правильного атрибута
        date_value = None

        # Пробуємо різні атрибути в порядку пріоритету
        if hasattr(record, 'date_completed') and record.date_completed:
            date_value = record.date_completed
        elif hasattr(record, 'created_at') and record.created_at:
            date_value = record.created_at
        elif hasattr(record, 'date_played') and record.date_played:
            date_value = record.date_played
        elif hasattr(record, 'timestamp') and record.timestamp:
            date_value = record.timestamp

        if not date_value or str(date_value) == "None":
            return "--"

        try:
            # Якщо це вже об'єкт datetime
            if isinstance(date_value, datetime):
                return date_value.strftime("%d.%m.%Y %H:%M")

            # Якщо це рядок, пробуємо його парсити
            date_str = str(date_value)

            # ISO формат з T
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Пробуємо стандартний формат SQLite
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        # Без часу
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        # Якщо нічого не спрацювало, повертаємо скорочений рядок
                        return date_str[:16] if len(date_str) > 16 else date_str

            return date_obj.strftime("%d.%m.%Y %H:%M")

        except Exception as e:
            print(f"Error formatting date {date_value}: {e}")
            return str(date_value)[:16] if len(str(date_value)) > 16 else str(date_value)

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

        # ✅ Ініціалізація кнопок при першому рендері
        if not self.difficulty_buttons:
            self._initialize_buttons(game.font, game.small_font)

        # ✅ Винесено в окремі методи для читабельності
        self._render_title(surface, game.font)  # додано метод для заголовка
        self._render_difficulty_buttons(surface, game.small_font)  #  кнопки рівня складності
        self._render_personal_stats(surface, game.small_font)  #  персональна статистика
        self._render_table_headers(surface, game.small_font)  #  заголовки таблиці
        self._render_records(surface, game.small_font)  #  самі записи
        self._render_back_button(surface)  #  кнопка "Назад"
        self._render_scroll_info(surface, game.small_font)  #  інформація про прокрутку

    # ✅ Відображення заголовка таблиці
    def _render_title(self, surface, font):
        title_text = font.render("ТАБЛИЦЯ РЕКОРДІВ", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 30))
        surface.blit(title_text, title_rect)

    # ✅ Відображення кнопок вибору складності (Easy, Medium, Hard)
    def _render_difficulty_buttons(self, surface, font):
        for difficulty, (rect, text_surface) in self.difficulty_buttons.items():
            color = GREEN if difficulty == self.selected_difficulty else BLUE  # 👉 підсвітка вибраної складності
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

    # ✅ Персональна статистика гравця (ігри + середній час)
    def _render_personal_stats(self, surface, font):
        if self.personal_stats and self.personal_stats.get('total_games', 0) > 0:
            stats_y = 130
            total_games = self.personal_stats.get('total_games', 0)
            avg_time = self.personal_stats.get('average_time', 0)
            stats_text = f"Ваша статистика: Зіграно ігор: {total_games}, Середній час: {self._format_time(avg_time)}"
            stats_surface = font.render(stats_text, True, BLACK)
            surface.blit(stats_surface, (50, stats_y))

    # ✅ Заголовки колонок таблиці ("#", "Час", тощо)
    def _render_table_headers(self, surface, font):
        headers = ["#", "Час", "Рівень", "Підказок", "Дата"]
        header_positions = [80, 150, 220, 320, 400]
        headers_y = self.header_height + 20

        for header, x_pos in zip(headers, header_positions):
            header_surface = font.render(header, True, BLACK)
            surface.blit(header_surface, (x_pos, headers_y))

        #  лінія під заголовками
        pygame.draw.line(surface, GRAY, (50, headers_y + 25), (WINDOW_SIZE[0] - 50, headers_y + 25), 2)

    # ✅ Основна таблиця рекордів
    def _render_records(self, surface, font):
        if not self.records:
            # 👉 Повідомлення, якщо записів немає
            no_records_text = font.render("Рекордів поки немає", True, GRAY)
            no_records_rect = no_records_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            surface.blit(no_records_text, no_records_rect)
            return

        records_start_y = self.header_height + 55
        difficulty_names = {
            Difficulty.EASY: "Легкий",
            Difficulty.MEDIUM: "Середній",
            Difficulty.HARD: "Важкий"
        }
        header_positions = [80, 150, 220, 320, 400]

        for i, record in enumerate(self.records[self.scroll_offset:self.scroll_offset + self.records_per_page]):
            y_pos = records_start_y + i * self.record_height

            if i % 2 == 1:
                #  Чергування кольору рядків для зручності читання
                row_rect = pygame.Rect(50, y_pos - 2, WINDOW_SIZE[0] - 100, self.record_height)
                pygame.draw.rect(surface, (245, 245, 245), row_rect)

            #  Дані для кожного запису
            rank_text = font.render(str(self.scroll_offset + i + 1), True, BLACK)
            surface.blit(rank_text, (header_positions[0], y_pos))

            time_text = font.render(self._format_time(record.completion_time), True, BLACK)
            surface.blit(time_text, (header_positions[1], y_pos))

            # Перевірка .get() у разі None, щоб уникнути AttributeError
            difficulty = difficulty_names.get(record.difficulty, str(record.difficulty))
            diff_text = font.render(difficulty, True, BLACK)
            surface.blit(diff_text, (header_positions[2], y_pos))

            hints_text = font.render(str(record.hints_used), True, BLACK)
            surface.blit(hints_text, (header_positions[3], y_pos))

            date_text = font.render(self._format_date(record), True, BLACK)
            surface.blit(date_text, (header_positions[4], y_pos))

    # ✅ Відображення кнопки "Назад"
    def _render_back_button(self, surface):
        if self.back_button:
            rect, text_surface = self.back_button
            pygame.draw.rect(surface, BLUE, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

    # ✅ Інформація про поточну сторінку (наприклад: Записи 1–10 з 25)
    def _render_scroll_info(self, surface, font):
        if len(self.records) > self.records_per_page:
            scroll_text = f"Записи {self.scroll_offset + 1}-{min(self.scroll_offset + self.records_per_page, len(self.records))} з {len(self.records)}"
            scroll_surface = font.render(scroll_text, True, GRAY)
            surface.blit(scroll_surface, (WINDOW_SIZE[0] - 250, WINDOW_SIZE[1] - 30))
