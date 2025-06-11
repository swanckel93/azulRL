# Fixed Factory class
from .tileholder import Tileholder, Bag
from typing import MutableSequence
from azul.tile import Tile


class Factory(Tileholder):
    MIN_SIZE = 1
    MAX_SIZE = 5

    def __init__(self, factory_size: int = 4):  # Default to 4 for Azul
        if not self.is_size_valid(factory_size):
            raise ValueError(
                f"Given length is {factory_size} but must be between {self.MIN_SIZE} and {self.MAX_SIZE}"
            )
        self.factory_size = factory_size
        super().__init__([])

    def is_size_valid(self, length: int) -> bool:
        return self.MIN_SIZE <= length <= self.MAX_SIZE

    def fill_from(self, source: Bag):
        """Fill factory from bag"""
        if len(source) >= self.factory_size:
            tiles = source.pop_random(self.factory_size)
            self.extend(tiles)
        else:
            # Take whatever is left
            remaining = source.pop_random(len(source))
            self.extend(remaining)

    def is_full(self) -> bool:
        """Check if factory is full"""
        return len(self._tiles) == self.factory_size

    def is_empty(self) -> bool:
        """Check if factory is empty"""
        return len(self._tiles) == 0
