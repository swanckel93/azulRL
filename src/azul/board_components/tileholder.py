from typing import MutableSequence, Generic
import random
from azul.tile import Tile, TileType, SpecialTileType, T


class Tileholder(Generic[T]):
    def __init__(
        self, tiles: MutableSequence[Tile] | None = None
    ):  # Fixed mutable default argument
        self._tiles = list(tiles) if tiles else []

    def __getitem__(self, index):
        return self._tiles[index]

    def __setitem__(self, index, value):
        self._tiles[index] = value

    def __delitem__(self, index):
        del self._tiles[index]

    def __len__(self):
        return len(self._tiles)

    def insert(self, index, value):
        self._tiles.insert(index, value)

    def __repr__(self):
        return f"TileHolder({self._tiles!r})"

    def __str__(self):
        return str(self._tiles)

    def __eq__(self, other: "Tileholder") -> bool:
        return self._tiles == other._tiles

    def extend(self, tiles: MutableSequence[Tile]):
        self._tiles.extend(tiles)

    def append(self, tile: Tile):
        """Add single tile"""
        self._tiles.append(tile)

    def count(self, tile_type: T):
        return [t.type for t in self._tiles].count(tile_type)

    def move_all_to(self, target: "Tileholder") -> None:
        tiles_to_move = list(self._tiles)  # creates copy
        self._tiles.clear()
        target.extend(tiles_to_move)

    def move_all_of_tile_type_to(self, target: "Tileholder", tile_type: T) -> None:
        tiles_to_move = [
            t for t in self._tiles if t.type == tile_type
        ]  # Fixed comparison
        self._tiles = [
            t for t in self._tiles if t.type != tile_type
        ]  # Fixed comparison
        target.extend(tiles_to_move)

    def take_all_from(self, source: "Tileholder") -> None:
        """Take all tiles from source container"""
        source.move_all_to(self)

    def take_all_of_type_from(self, source: "Tileholder", tile_type: T) -> None:
        """Take all tiles of specific type from source container."""
        source.move_all_of_tile_type_to(self, tile_type)


class BoardCenter(Tileholder):
    def __init__(self, tiles: MutableSequence[Tile] = []):
        super().__init__(tiles)

    def contains_onetile(self) -> bool:
        return True if SpecialTileType.TILE_1 in self else False


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


class StagingLine(Tileholder):
    MIN_LENGTH = 1
    MAX_LENGTH = 5

    def __init__(self, length: int):
        super().__init__([])
        if not self.MIN_LENGTH <= length <= self.MAX_LENGTH:
            raise ValueError(
                f"length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH}, but {length} given."
            )
        self._max_length = length

    def add_tiles_safely(self, tiles: MutableSequence[TileType]) -> bool | None:
        if not self.can_add_tiles(tiles):
            return False
        self.extend(tiles)
        return None

    def add_partially(
        self, tiles: MutableSequence[TileType]
    ) -> MutableSequence[TileType]:

        while len(self) < self._max_length and tiles:
            if not self.can_add_tile_type(tiles[-1]):
                raise ValueError("")
            self.append(tiles.pop())

        return []

    def can_add_tiles(self, tiles: MutableSequence[TileType]) -> bool:
        # check if
        if not len(tiles) <= self._max_length - len(self):
            return False
        return True

    def can_add_tile_type(self, tile: TileType) -> bool:
        if not self or all(x == tile for x in self):
            return True
        return False


class Floorline(Tileholder):
    pass


class Wall(Tileholder):
    pass
