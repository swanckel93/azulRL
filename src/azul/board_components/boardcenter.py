from typing import MutableSequence
from azul.tile import Tile, SpecialTileType
from .tileholder import Tileholder


class BoardCenter(Tileholder):
    def __init__(
        self, tiles: MutableSequence[Tile] | None = None
    ):  # Fixed mutable default argument
        super().__init__(tiles)

    def contains_onetile(self) -> bool:
        return any(
            tile.type == SpecialTileType.TILE_1 for tile in self._tiles
        )  # Fixed logic
