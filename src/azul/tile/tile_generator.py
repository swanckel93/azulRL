import random
from typing import MutableSequence
from .tile import Tile, TileType, SpecialTileType


class TileGenerator:
    def __init__(self, seed=42):
        self.n_tiles_per_type = 20
        self.next_id = 1  # Track the next ID to assign
        random.seed(seed)

    def _get_next_id(self) -> int:
        """Get the next available tile ID and increment the counter."""
        current_id = self.next_id
        self.next_id += 1
        return current_id

    def create_random_tiles(self, n: int) -> MutableSequence[Tile]:
        return [
            Tile(random.choice(list(TileType)), self._get_next_id()) for _ in range(n)
        ]

    def create_tiles_of_type(
        self, n: int, tile_type: TileType
    ) -> MutableSequence[Tile]:
        return [Tile(tile_type, self._get_next_id()) for _ in range(n)]

    def create_game_tiles(self) -> MutableSequence[Tile]:
        tiles = []
        for tile_type in TileType:
            tiles.extend(
                [
                    Tile(tile_type, self._get_next_id())
                    for _ in range(self.n_tiles_per_type)
                ]
            )
        return tiles

    def create_game_special_tile(self) -> Tile:
        return Tile(SpecialTileType.TILE_1, self._get_next_id())

    def get_current_id_count(self) -> int:
        """Return the number of IDs that have been issued."""
        return self.next_id - 1


# Singleton tile generator
TG = TileGenerator()


def get_tile_generator():
    return TG
