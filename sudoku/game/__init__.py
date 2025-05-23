"""
Пакет для основних компонентів гри
"""
from .game import Game
from .states import IGameState, PlayingState, GameOverState, PausedState
from .timer import GameTimer

__all__ = ['Game', 'IGameState', 'PlayingState', 'GameOverState', 'PausedState', 'GameTimer']