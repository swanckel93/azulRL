from typing import TypeVar, Self
from enum import Enum


class TileType(Enum):
    RED = 1
    BLUE = 2
    BLACK = 3
    WHITE = 4
    YELLOW = 5


class SpecialTileType(Enum):
    TILE_1 = 6


T = TypeVar("T", bound=TileType | SpecialTileType)


class Tile:
    def __init__(self, type: TileType | SpecialTileType, tile_id: int):
        self.id = tile_id
        self.type = type

    def __repr__(self):
        return f"Tile(id={self.id}, type={self.type})"

    def __str__(self):
        return f"Tile({self.type.name})"

    def __eq__(self, other):
        # allow for direct comparison to enum
        if isinstance(other, Enum):
            return self.type == other
        # allow comparison to other Tile
        if isinstance(other, Tile):
            return self.type == other.type

    def __hash__(self):
        return hash(self.id)
