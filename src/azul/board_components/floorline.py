from typing import MutableSequence
from azul.tile import Tile
from .tileholder import Tileholder


class Floorline(Tileholder):
    """Enhanced Floorline with penalty scoring"""

    PENALTIES = [-1, -1, -2, -2, -2, -3, -3]

    def __init__(self):
        super().__init__()
        self.max_size = 7

    def add_tiles(self, tiles: MutableSequence[Tile]) -> MutableSequence[Tile]:
        """Add tiles to floor line, return any overflow"""
        remaining = list(tiles)
        while len(self._tiles) < self.max_size and remaining:
            self._tiles.append(remaining.pop(0))
        return remaining

    def calculate_penalty(self) -> int:
        """Calculate penalty points for tiles in floor line"""
        penalty = 0
        for i in range(min(len(self._tiles), len(self.PENALTIES))):
            penalty += self.PENALTIES[i]
        return penalty
