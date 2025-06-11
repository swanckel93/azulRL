from typing import MutableSequence
import pytest
from azul.board_components import Tileholder
from azul.tile import TileGenerator, TileType, Tile
from tests.shared import tg


class TestTileholder:
    @pytest.mark.unit
    def test_holds_tiles(self, tg: TileGenerator):
        tiles_to_hold: MutableSequence[Tile] = tg.create_random_tiles(10)
        th1 = Tileholder()
        th1.extend((tiles_to_hold))
        assert th1._tiles == tiles_to_hold

    @pytest.mark.unit
    def test_equality(self, tg: TileGenerator):
        tiles_to_hold: MutableSequence[Tile] = tg.create_random_tiles(10)
        th1 = Tileholder(tiles_to_hold)
        th2 = Tileholder(tiles_to_hold)
        assert th1 == th2

    @pytest.mark.unit
    def test_valid_move_all_to(self, tg: TileGenerator):
        tiles_to_move = tg.create_random_tiles(10)
        th1 = Tileholder(tiles_to_move)
        th2 = Tileholder()
        th1.move_all_to(th2)
        assert th2._tiles == tiles_to_move
        assert not th1._tiles

    @pytest.mark.unit
    def test_move_all_of_type(self, tg: TileGenerator):
        n_tiles = 50
        tiles_to_move = tg.create_random_tiles(n_tiles)
        n_black_tiles = tiles_to_move.count(TileType.BLACK)
        th1 = Tileholder(tiles_to_move)
        th2 = Tileholder()
        th1.move_all_of_tile_type_to(th2, TileType.BLACK)
        assert all(t.type == TileType.BLACK for t in th2)
        assert len(th2) == n_black_tiles
        assert all(t.type != TileType.BLACK for t in th1)
        assert len(th1) == n_tiles - n_black_tiles

    @pytest.mark.unit
    def test_take_all_from(self, tg: TileGenerator):
        n_tiles = 50
        tiles = tg.create_random_tiles(n_tiles)
        th1 = Tileholder(tiles)
        th2 = Tileholder()
        th2.take_all_from(th1)
        assert len(th1) == 0
        assert len(th2) == n_tiles

    @pytest.mark.unit
    def test_tyle_all_of_type_from(self, tg: TileGenerator):
        n_tiles = 50
        tiles = tg.create_random_tiles(n_tiles)
        n_black_tiles = tiles.count(TileType.BLACK)
        th1 = Tileholder(tiles)
        th2 = Tileholder()
        th2.take_all_of_type_from(th1, TileType.BLACK)
        assert all(t.type == TileType.BLACK for t in th2)
        assert len(th2) == n_black_tiles
        assert all(t.type != TileType.BLACK for t in th1)
        assert len(th1) == n_tiles - n_black_tiles
