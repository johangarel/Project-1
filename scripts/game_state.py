from enum import Enum, auto


class GameState(Enum):
    """Possible states of the game."""
    MAIN_MENU      = auto()
    LEVEL_MENU     = auto()
    MAZE           = auto()
    VICTORY_MENU   = auto()
    FRENCH_TUTORIAL  = auto()
    ENGLISH_TUTORIAL = auto()
