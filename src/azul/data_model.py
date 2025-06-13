from enum import Enum
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
    SETUP = "SETUP"
    FACTORY_FILLING = "FACTORY_FILLING"
    PLAYER_TURN = "PLAYER_TURN"
    ROUND_END = "ROUND_END"
    GAME_END = "GAME_END"


class CompletionStatus(Enum):
    NOT_COMPLETED = "NOT_COMPLETED"
    ABORTED = "ABORTED"
    COMPLETED = "COMPLETED"


class ActionType(Enum):
    TAKE_FROM_FACTORY = "TAKE_FROM_FACTORY"
    TAKE_FROM_CENTER = "TAKE_FROM_CENTER"
    ABORT_GAME = "ABORT_GAME"


@dataclass
class Action:
    type: ActionType
    factory_id: Optional[int] = None  # None for center pile
    tile_type: Optional[TileType] = None
    pattern_line: Optional[int] = None  # 0-4 for pattern lines, -1 for floor
