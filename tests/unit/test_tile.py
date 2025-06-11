import pytest
from azul.tile import Tile, TileType, SpecialTileType


class TestTile:
    @pytest.mark.unit
    def test_tile_equality(self):
        t1 = Tile(TileType.BLACK, tile_id=1)
        t2 = Tile(TileType.BLUE, tile_id=2)
        assert not t1 == t2
        t3 = Tile(TileType.BLACK, tile_id=3)
        assert t1 == t3
        t4 = Tile(TileType.BLUE, tile_id=3)
        assert not t3 == t4
