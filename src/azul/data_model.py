from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from uuid import UUID
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


class GameMode(Enum):
    SELFPLAY = "SELFPLAY"
    PVP = "PVP"
    PVAI = "PVAI"


class PlayerStatus(Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    LEFT = "LEFT"


@dataclass
class Player:
    id: UUID
    name: Optional[str] = None
    status: PlayerStatus = PlayerStatus.CONNECTED
    player_index: Optional[int] = None  # 0, 1, 2, 3 - which player board they control


@dataclass
class Action:
    type: ActionType
    factory_id: Optional[int] = None  # None for center pile
    tile_type: Optional[TileType] = None
    pattern_line: Optional[int] = None  # 0-4 for pattern lines, -1 for floor
