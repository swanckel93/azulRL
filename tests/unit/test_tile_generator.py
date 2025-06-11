import pytest

from azul.tile.tile import TileType, SpecialTileType, T
from azul.tile.tile_generator import TileGenerator
from tests.shared import tg


class TestGenerator:
    @pytest.mark.unit
    @pytest.mark.parametrize("n", [5, 10, 20])
    def test_random_tile_generation(self, tg: TileGenerator, n):
        tiles = tg.create_random_tiles(n)  #
        assert n == len(tiles)
        for t in tiles:
            assert t.type in [x for x in TileType]
        tile_ids = [t.id for t in tiles]
        assert len(set(tile_ids)) == len(tile_ids)
        assert max(tile_ids) == tg.next_id - 1

    @pytest.mark.unit
    def test_game_tile_creation(self, tg: TileGenerator):
        game_tiles = tg.create_game_tiles()
        for t in TileType:
            assert len([x.type for x in game_tiles if x.type == t]) == 20
        assert set([x.type for x in game_tiles]) == set([t for t in TileType])
        assert len(game_tiles) == tg.next_id - 1

    @pytest.mark.unit
    def test_special_tile_creation(self, tg: TileGenerator):
        special_tile = tg.create_game_special_tile()
        assert special_tile.type == SpecialTileType.TILE_1
        assert tg.next_id == 2

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "type,n", [(TileType.BLACK, 5), (TileType.BLUE, 10), (TileType.YELLOW, 20)]
    )
    def test_tile_creation(self, type: TileType, n: int, tg: TileGenerator):
        tiles = tg.create_tiles_of_type(n, type)
        assert all(t.type == type for t in tiles)
        assert len(tiles) == n
        assert tg.next_id - 1 == len(tiles)
