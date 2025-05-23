"""
Пакет для основних компонентів гри
"""
from .game import Game
from .states import IGameState, PlayingState, GameOverState

__all__ = ['Game', 'IGameState', 'PlayingState', 'GameOverState']