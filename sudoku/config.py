"""
Конфігураційний файл для гри судоку
"""

# Розміри гри
GRID_SIZE = 9
SUB_GRID_SIZE = 3
CELL_SIZE = 60
WINDOW_SIZE = (GRID_SIZE * CELL_SIZE + 150, GRID_SIZE * CELL_SIZE + 80 )  # 60 додаткових пікселів для кнопок

# Кольори
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 123, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (173, 216, 230)
LIGHT_BLUE_ALT = (220, 220, 255)

# Налаштування гри
MAX_HINTS = 3