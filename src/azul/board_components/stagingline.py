from typing import MutableSequence
from .tileholder import Tileholder
from azul.tile import Tile, TileType


class StagingLine(Tileholder):
    """Fixed StagingLine class"""

    MIN_LENGTH = 1
    MAX_LENGTH = 5

    def __init__(self, length: int):
        super().__init__([])
        if not self.MIN_LENGTH <= length <= self.MAX_LENGTH:
            raise ValueError(
                f"length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH}, but {length} given."
            )
        self._max_length = length

    def add_tiles_safely(self, tiles: MutableSequence[Tile]) -> bool:
        """Fixed: takes Tile objects, not TileType"""
        if not self.can_add_tiles(tiles):
            return False
        self.extend(tiles)
        return True

    def add_partially(self, tiles: MutableSequence[Tile]) -> MutableSequence[Tile]:
        """Add as many tiles as possible, return remainder"""
        remaining = list(tiles)
        while len(self) < self._max_length and remaining:
            if not self.can_add_tile_type(remaining[0].type):
                break
            self._tiles.append(remaining.pop(0))
        return remaining

    def can_add_tiles(self, tiles: MutableSequence[Tile]) -> bool:
        """Check if all tiles can be added"""
        if len(tiles) > self._max_length - len(self):
            return False
        if not tiles:
            return True
        tile_type = tiles[0].type
        return all(tile.type == tile_type for tile in tiles) and self.can_add_tile_type(
            tile_type
        )

    def can_add_tile_type(self, tile_type: TileType) -> bool:
        """Check if tile type can be added"""
        if not self._tiles:
            return True
        return all(tile.type == tile_type for tile in self._tiles)

    def is_complete(self) -> bool:
        """Check if staging line is complete"""
        return len(self._tiles) == self._max_length
