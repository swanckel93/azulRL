import pytest

from azul.data_model import TileType, ActionType, Action
from azul.components import Tile, Container, Bag, Factory, PatternLine, PlayerBoard


@pytest.mark.unit
class TestTile:
    def test_tile_creation(self):
        tile = Tile(TileType.BLUE)
        assert tile.type == TileType.BLUE

    def test_tile_equality(self):
        tile1 = Tile(TileType.BLUE)
        tile2 = Tile(TileType.BLUE)
        tile3 = Tile(TileType.RED)

        assert tile1 == tile2
        assert tile1 != tile3

    def test_tile_hash(self):
        tile1 = Tile(TileType.BLUE)
        tile2 = Tile(TileType.BLUE)

        assert hash(tile1) == hash(tile2)


@pytest.mark.unit
class TestContainer:
    @pytest.fixture
    def container(self):
        return Container()

    def test_empty_container(self, container):
        assert container.is_empty()
        assert len(container.tiles) == 0

    def test_add_tile(self, container):
        tile = Tile(TileType.BLUE)
        container.add_tile(tile)

        assert not container.is_empty()
        assert len(container.tiles) == 1
        assert container.tiles[0] == tile

    def test_add_tiles(self, container):
        tiles = [Tile(TileType.BLUE), Tile(TileType.RED)]
        container.add_tiles(tiles)

        assert len(container.tiles) == 2
        assert container.tiles == tiles

    def test_remove_tile(self, container):
        blue_tile = Tile(TileType.BLUE)
        red_tile = Tile(TileType.RED)
        container.add_tiles([blue_tile, red_tile])

        removed = container.remove_tile(TileType.BLUE)

        assert removed == blue_tile
        assert len(container.tiles) == 1
        assert container.tiles[0] == red_tile

    def test_remove_tile_not_found(self, container):
        removed = container.remove_tile(TileType.BLUE)
        assert removed is None

    def test_remove_all_tiles(self, container):
        tiles = [Tile(TileType.BLUE), Tile(TileType.RED), Tile(TileType.BLUE)]
        container.add_tiles(tiles)

        removed = container.remove_all_tiles(TileType.BLUE)

        assert len(removed) == 2
        assert len(container.tiles) == 1
        assert container.tiles[0].type == TileType.RED

    def test_count_by_type(self, container):
        tiles = [Tile(TileType.BLUE), Tile(TileType.RED), Tile(TileType.BLUE)]
        container.add_tiles(tiles)

        assert container.count_by_type(TileType.BLUE) == 2
        assert container.count_by_type(TileType.RED) == 1
        assert container.count_by_type(TileType.WHITE) == 0

    def test_get_unique_types(self, container):
        tiles = [Tile(TileType.BLUE), Tile(TileType.RED), Tile(TileType.BLUE)]
        container.add_tiles(tiles)

        unique_types = container.get_unique_types()

        assert set(unique_types) == {TileType.BLUE, TileType.RED}

    def test_clear(self, container):
        tiles = [Tile(TileType.BLUE), Tile(TileType.RED)]
        container.add_tiles(tiles)

        cleared = container.clear()

        assert cleared == tiles
        assert container.is_empty()


@pytest.mark.unit
class TestBag:
    def test_bag_initialization(self):
        bag = Bag()

        # Should have 100 tiles total (20 of each color)
        assert len(bag.tiles) == 100

        # Count each color
        for tile_type in [
            TileType.BLUE,
            TileType.YELLOW,
            TileType.RED,
            TileType.BLACK,
            TileType.WHITE,
        ]:
            assert bag.count_by_type(tile_type) == 20

    def test_draw_tiles(self):
        bag = Bag()
        initial_count = len(bag.tiles)

        drawn = bag.draw_tiles(4)

        assert len(drawn) == 4
        assert len(bag.tiles) == initial_count - 4

    def test_draw_more_than_available(self):
        bag = Bag()
        bag.tiles = [Tile(TileType.BLUE), Tile(TileType.RED)]  # Only 2 tiles

        drawn = bag.draw_tiles(5)

        assert len(drawn) == 2
        assert bag.is_empty()


@pytest.mark.unit
class TestFactory:
    def test_factory_creation(self):
        factory = Factory(id=1)
        assert factory.id == 1
        assert factory.is_empty()

    def test_fill_from_bag(self):
        bag = Bag()
        factory = Factory(id=1)

        factory.fill_from_bag(bag)

        assert len(factory.tiles) == 4
        assert len(bag.tiles) == 96  # 100 - 4

    def test_fill_from_empty_bag(self):
        bag = Bag()
        bag.tiles = []  # Empty bag
        factory = Factory(id=1)

        factory.fill_from_bag(bag)

        assert factory.is_empty()

    def test_fill_from_bag_with_few_tiles(self):
        bag = Bag()
        bag.tiles = [Tile(TileType.BLUE), Tile(TileType.RED)]  # Only 2 tiles
        factory = Factory(id=1)

        factory.fill_from_bag(bag)

        assert len(factory.tiles) == 2
        assert bag.is_empty()


@pytest.mark.unit
class TestPatternLine:
    def test_pattern_line_creation(self):
        line = PatternLine(capacity=3)
        assert line.capacity == 3
        assert line.is_empty()
        assert not line.is_full()

    def test_can_add_tile_empty_line(self):
        line = PatternLine(capacity=3)
        assert line.can_add_tile(TileType.BLUE)

    def test_can_add_tile_same_type(self):
        line = PatternLine(capacity=3)
        line.tiles = [Tile(TileType.BLUE)]

        assert line.can_add_tile(TileType.BLUE)
        assert not line.can_add_tile(TileType.RED)

    def test_can_add_tile_full_line(self):
        line = PatternLine(capacity=2)
        line.tiles = [Tile(TileType.BLUE), Tile(TileType.BLUE)]

        assert not line.can_add_tile(TileType.BLUE)

    def test_add_tiles_normal(self):
        line = PatternLine(capacity=3)
        tiles = [Tile(TileType.BLUE), Tile(TileType.BLUE)]

        overflow = line.add_tiles(tiles)

        assert overflow == 0
        assert len(line.tiles) == 2

    def test_add_tiles_overflow(self):
        line = PatternLine(capacity=2)
        tiles = [Tile(TileType.BLUE), Tile(TileType.BLUE), Tile(TileType.BLUE)]

        overflow = line.add_tiles(tiles)

        assert overflow == 1
        assert len(line.tiles) == 2
        assert line.is_full()

    def test_add_tiles_wrong_type(self):
        line = PatternLine(capacity=3)
        line.tiles = [Tile(TileType.BLUE)]
        red_tiles = [Tile(TileType.RED)]

        overflow = line.add_tiles(red_tiles)

        assert overflow == 1  # All tiles overflow
        assert len(line.tiles) == 1  # Original tile remains

    def test_get_tile_type(self):
        line = PatternLine(capacity=3)
        assert line.get_tile_type() is None

        line.tiles = [Tile(TileType.BLUE)]
        assert line.get_tile_type() == TileType.BLUE

    def test_clear(self):
        line = PatternLine(capacity=3)
        tiles = [Tile(TileType.BLUE), Tile(TileType.BLUE)]
        line.add_tiles(tiles)
        cleared = line.clear()

        assert cleared == tiles
        assert line.is_empty()


@pytest.mark.unit
class TestPlayerBoard:
    @pytest.fixture
    def board(self):
        return PlayerBoard()

    def test_board_initialization(self, board: PlayerBoard):
        assert len(board.pattern_lines) == 5
        assert len(board.wall) == 5
        assert len(board.wall[0]) == 5
        assert board.score == 0
        assert len(board.floor) == 0

        # Check pattern line capacities
        for i, line in enumerate(board.pattern_lines):
            assert line.capacity == i + 1

    def test_can_place_in_pattern_line_valid(self, board: PlayerBoard):
        # First pattern line (capacity 1) can take blue tile
        assert board.can_place_in_pattern_line(0, TileType.BLUE)

    def test_can_place_in_pattern_line_wall_occupied(self, board: PlayerBoard):
        # Place blue tile on wall at position (0, 0)
        board.wall[0][0] = True

        # Should not be able to place blue tile in first pattern line
        assert not board.can_place_in_pattern_line(0, TileType.BLUE)

    def test_can_place_in_pattern_line_wrong_type(self, board: PlayerBoard):
        # Add blue tile to first pattern line
        board.pattern_lines[0].tiles = [Tile(TileType.BLUE)]

        # Should not be able to add red tile
        assert not board.can_place_in_pattern_line(0, TileType.RED)

    def test_can_place_in_pattern_line_invalid_index(self, board: PlayerBoard):
        assert not board.can_place_in_pattern_line(-2, TileType.BLUE)
        assert not board.can_place_in_pattern_line(5, TileType.BLUE)

    def test_add_tiles_to_pattern_line(self, board: PlayerBoard):
        tiles = [Tile(TileType.BLUE)]
        board.add_tiles_to_pattern_line(0, tiles)

        assert len(board.pattern_lines[0].tiles) == 1
        assert board.pattern_lines[0].tiles[0].type == TileType.BLUE

    def test_add_tiles_to_floor(self, board: PlayerBoard):
        tiles = [Tile(TileType.BLUE), Tile(TileType.RED)]
        board.add_tiles_to_pattern_line(-1, tiles)

        assert len(board.floor) == 2

    def test_add_tiles_with_overflow(self, board: PlayerBoard):
        # Fill first pattern line (capacity 1) with 2 tiles
        tiles = [Tile(TileType.BLUE), Tile(TileType.BLUE)]
        board.add_tiles_to_pattern_line(0, tiles)

        # One should go to pattern line, one to floor
        assert len(board.pattern_lines[0].tiles) == 1
        assert len(board.floor) == 1

    def test_move_completed_lines_to_wall(self, board: PlayerBoard):
        # Fill first pattern line
        board.pattern_lines[0].tiles = [Tile(TileType.BLUE)]

        discarded = board.move_completed_lines_to_wall()

        # Wall should have tile placed
        assert board.wall[0][0]  # Blue tile goes to (0,0)
        # Pattern line should be empty
        assert board.pattern_lines[0].is_empty()
        # No tiles should be discarded (only 1 tile in line)
        assert len(discarded) == 0

    def test_move_completed_lines_to_wall_with_discard(self, board: PlayerBoard):
        # Fill second pattern line (capacity 2) completely
        board.pattern_lines[1].tiles = [Tile(TileType.BLUE), Tile(TileType.BLUE)]

        discarded = board.move_completed_lines_to_wall()

        # Wall should have tile placed
        assert board.wall[1][1]  # Blue tile goes to (1,1) in second row
        # One tile should be discarded
        assert len(discarded) == 1

    def test_clear_floor(self, board: PlayerBoard):
        floor_tiles = [Tile(TileType.BLUE), Tile(TileType.RED)]
        board.floor.extend(floor_tiles)
        cleared = board.clear_floor()

        assert cleared == floor_tiles
        assert len(board.floor) == 0

    def test_has_complete_row(self, board: PlayerBoard):
        assert not board.has_complete_row()

        # Fill first row
        for col in range(5):
            board.wall[0][col] = True

        assert board.has_complete_row()


@pytest.mark.unit
class TestAction:
    def test_action_creation(self):
        action = Action(
            type=ActionType.TAKE_FROM_FACTORY,
            factory_id=1,
            tile_type=TileType.BLUE,
            pattern_line=0,
        )

        assert action.type == ActionType.TAKE_FROM_FACTORY
        assert action.factory_id == 1
        assert action.tile_type == TileType.BLUE
        assert action.pattern_line == 0

    def test_action_defaults(self):
        action = Action(type=ActionType.TAKE_FROM_CENTER)

        assert action.factory_id is None
        assert action.tile_type is None
        assert action.pattern_line is None
