import random
from typing import MutableSequence
from azul.tile import Tile
from .tileholder import Tileholder


class Bag(Tileholder):
    def __init__(self, tiles: MutableSequence[Tile]):
        super().__init__(tiles)

    def pop_random(self, n) -> MutableSequence[Tile]:
        if len(self) < n:
            raise IndexError(
                f"Attempting to remove {n} Tile(s) from Bag, but only {len(self)} Tile(s) left in bag."
            )
        self._shuffle()
        return [self._tiles.pop() for _ in range(n)]

    def _shuffle(self) -> None:
        random.shuffle(self._tiles)
