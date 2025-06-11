from enum import Enum, auto
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import random


class TileType(Enum):
    BLUE = "blue"
    YELLOW = "yellow"
    RED = "red"
    BLACK = "black"
    WHITE = "white"
    FIRST_PLAYER = "first_player"


class GameStateType(Enum):
    SETUP = auto()
    FACTORY_FILLING = auto()
    PLAYER_TURN = auto()
    ROUND_END = auto()
    GAME_END = auto()


class ActionType(Enum):
    TAKE_FROM_FACTORY = auto()
    TAKE_FROM_CENTER = auto()


@dataclass
class Action:
    type: ActionType
    factory_id: Optional[int] = None  # None for center pile
    tile_type: Optional[TileType] = None
    pattern_line: Optional[int] = None  # 0-4 for pattern lines, -1 for floor
