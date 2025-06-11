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

        # Check wall is empty
        for row in range(5):
            for col in range(5):
                assert not board.wall[row][col]

    def test_wall_pattern_correct(self, board: PlayerBoard):
        """Test that wall pattern is correctly defined"""
        expected_pattern = [
            [
                TileType.BLUE,
                TileType.YELLOW,
                TileType.RED,
                TileType.BLACK,
                TileType.WHITE,
            ],
            [
                TileType.WHITE,
                TileType.BLUE,
                TileType.YELLOW,
                TileType.RED,
                TileType.BLACK,
            ],
            [
                TileType.BLACK,
                TileType.WHITE,
                TileType.BLUE,
                TileType.YELLOW,
                TileType.RED,
            ],
            [
                TileType.RED,
                TileType.BLACK,
                TileType.WHITE,
                TileType.BLUE,
                TileType.YELLOW,
            ],
            [
                TileType.YELLOW,
                TileType.RED,
                TileType.BLACK,
                TileType.WHITE,
                TileType.BLUE,
            ],
        ]
        assert board.WALL_PATTERN == expected_pattern

    def test_can_place_in_pattern_line_valid(self, board: PlayerBoard):
        # First pattern line (capacity 1) can take blue tile
        assert board.can_place_in_pattern_line(0, TileType.BLUE)
        # Second pattern line can take white tile
        assert board.can_place_in_pattern_line(1, TileType.WHITE)
        # Test different tile types in different lines
        assert board.can_place_in_pattern_line(2, TileType.BLACK)

    def test_can_place_in_pattern_line_wall_occupied(self, board: PlayerBoard):
        # Place blue tile on wall at position (0, 0)
        board.wall[0][0] = True

        # Should not be able to place blue tile in first pattern line
        assert not board.can_place_in_pattern_line(0, TileType.BLUE)

        # Other tiles should still be placeable
        assert board.can_place_in_pattern_line(0, TileType.YELLOW)

    def test_can_place_in_pattern_line_wrong_type(self, board: PlayerBoard):
        # Add blue tile to first pattern line
        board.pattern_lines[1].tiles = [Tile(TileType.BLUE)]

        # Should not be able to add red tile
        assert not board.can_place_in_pattern_line(1, TileType.RED)
        # Should be able to add more blue tiles
        assert board.can_place_in_pattern_line(1, TileType.BLUE)

    def test_can_place_in_pattern_line_invalid_index(self, board: PlayerBoard):
        assert not board.can_place_in_pattern_line(-2, TileType.BLUE)
        assert not board.can_place_in_pattern_line(5, TileType.BLUE)
        assert not board.can_place_in_pattern_line(10, TileType.BLUE)

    def test_can_place_in_pattern_line_full_line(self, board: PlayerBoard):
        # Fill first pattern line completely
        board.pattern_lines[0].tiles = [Tile(TileType.BLUE)]

        # Should not be able to add more tiles
        assert not board.can_place_in_pattern_line(0, TileType.BLUE)

    def test_add_tiles_to_pattern_line(self, board: PlayerBoard):
        tiles = [Tile(TileType.BLUE)]
        board.add_tiles_to_pattern_line(0, tiles)

        assert len(board.pattern_lines[0].tiles) == 1
        assert board.pattern_lines[0].tiles[0].type == TileType.BLUE

    def test_add_multiple_tiles_to_pattern_line(self, board: PlayerBoard):
        # Add multiple tiles to larger pattern line
        tiles = [Tile(TileType.RED), Tile(TileType.RED)]
        board.add_tiles_to_pattern_line(2, tiles)  # Line with capacity 3

        assert len(board.pattern_lines[2].tiles) == 2
        assert all(tile.type == TileType.RED for tile in board.pattern_lines[2].tiles)

    def test_add_tiles_to_floor(self, board: PlayerBoard):
        tiles = [Tile(TileType.BLUE), Tile(TileType.RED)]
        board.add_tiles_to_pattern_line(-1, tiles)

        assert len(board.floor) == 2
        assert board.floor[0].type == TileType.BLUE
        assert board.floor[1].type == TileType.RED

    def test_add_tiles_with_overflow(self, board: PlayerBoard):
        # Fill first pattern line (capacity 1) with 2 tiles
        tiles = [Tile(TileType.BLUE), Tile(TileType.BLUE)]
        board.add_tiles_to_pattern_line(0, tiles)

        # One should go to pattern line, one to floor
        assert len(board.pattern_lines[0].tiles) == 1
        assert len(board.floor) == 1

    def test_add_tiles_with_large_overflow(self, board: PlayerBoard):
        # Try to add 5 tiles to pattern line with capacity 2
        tiles = [Tile(TileType.YELLOW)] * 5
        board.add_tiles_to_pattern_line(1, tiles)  # Capacity 2

        assert len(board.pattern_lines[1].tiles) == 2
        assert len(board.floor) == 3

    def test_move_completed_lines_to_wall_single_tile(self, board: PlayerBoard):
        # Fill first pattern line
        board.pattern_lines[0].tiles = [Tile(TileType.BLUE)]

        discarded = board.move_completed_lines_to_wall()

        # Wall should have tile placed
        assert board.wall[0][0]  # Blue tile goes to (0,0)
        # Pattern line should be empty
        assert board.pattern_lines[0].is_empty()
        # No tiles should be discarded (only 1 tile in line)
        assert len(discarded) == 0

    def test_move_completed_lines_to_wall_multiple_tiles(self, board: PlayerBoard):
        # Fill second pattern line (capacity 2) with 2 tiles
        board.pattern_lines[1].tiles = [Tile(TileType.WHITE), Tile(TileType.WHITE)]

        discarded = board.move_completed_lines_to_wall()

        # Wall should have tile placed at correct position for white in row 1
        assert board.wall[1][0]  # White tile goes to (1,0) in row 1
        # Pattern line should be empty
        assert board.pattern_lines[1].is_empty()
        # One tile should be discarded
        assert len(discarded) == 1
        assert discarded[0].type == TileType.WHITE

    def test_move_completed_lines_multiple_lines(self, board: PlayerBoard):
        # Fill multiple pattern lines
        board.pattern_lines[0].tiles = [Tile(TileType.BLUE)]
        board.pattern_lines[2].tiles = [
            Tile(TileType.BLUE),
            Tile(TileType.BLUE),
            Tile(TileType.BLUE),
        ]

        discarded = board.move_completed_lines_to_wall()

        # Both lines should be moved to wall
        assert board.wall[0][0]  # Blue in row 0
        assert board.wall[2][2]  # Blue in row 2
        # 2 tiles should be discarded from the 3-tile line
        assert len(discarded) == 2

    def test_move_incomplete_lines_unchanged(self, board: PlayerBoard):
        # Partially fill a pattern line
        board.pattern_lines[2].tiles = [Tile(TileType.BLACK)]  # Capacity 3, only 1 tile

        discarded = board.move_completed_lines_to_wall()

        # Nothing should change
        assert not any(any(row) for row in board.wall)
        assert len(board.pattern_lines[2].tiles) == 1
        assert len(discarded) == 0

    def test_calculate_tile_score_single_tile(self, board: PlayerBoard):
        # Place single tile
        board.wall[2][2] = True
        score = board._calculate_tile_score(2, 2)
        assert score == 1

    def test_calculate_tile_score_horizontal_adjacent(self, board: PlayerBoard):
        # Place tiles horizontally adjacent
        board.wall[2][1] = True
        board.wall[2][2] = True
        board.wall[2][3] = True

        score = board._calculate_tile_score(2, 2)  # Middle tile
        assert score == 3

    def test_calculate_tile_score_vertical_adjacent(self, board: PlayerBoard):
        # Place tiles vertically adjacent
        board.wall[1][2] = True
        board.wall[2][2] = True
        board.wall[3][2] = True

        score = board._calculate_tile_score(2, 2)  # Middle tile
        assert score == 3

    def test_calculate_tile_score_both_directions(self, board: PlayerBoard):
        # Place tiles in both directions
        board.wall[1][2] = True  # Above
        board.wall[2][1] = True  # Left
        board.wall[2][2] = True  # Center
        board.wall[2][3] = True  # Right
        board.wall[3][2] = True  # Below

        score = board._calculate_tile_score(2, 2)
        assert score == 5

    def test_calculate_round_score_no_tiles(self, board: PlayerBoard):
        score = board.calculate_round_score()
        assert score == 0

    def test_calculate_round_score_with_floor_penalties(self, board: PlayerBoard):
        # Add tiles to floor
        board.floor = [Tile(TileType.BLUE), Tile(TileType.RED)]

        score = board.calculate_round_score()
        # First two floor tiles: -1, -1
        assert score == -2

    def test_calculate_round_score_max_floor_penalties(self, board: PlayerBoard):
        # Fill floor beyond penalty limit
        board.floor = [Tile(TileType.BLUE)] * 10

        score = board.calculate_round_score()
        # Only first 7 tiles count: -1, -1, -2, -2, -2, -3, -3 = -14
        assert score == -14

    def test_clear_floor(self, board: PlayerBoard):
        # Add tiles to floor
        original_tiles = [Tile(TileType.BLUE), Tile(TileType.RED)]
        board.floor = original_tiles.copy()

        cleared_tiles = board.clear_floor()

        assert len(board.floor) == 0
        assert len(cleared_tiles) == 2
        assert cleared_tiles[0].type == TileType.BLUE
        assert cleared_tiles[1].type == TileType.RED

    def test_has_complete_row_false(self, board: PlayerBoard):
        assert not board.has_complete_row()

        # Partially fill a row
        board.wall[0][0] = True
        board.wall[0][1] = True
        assert not board.has_complete_row()

    def test_has_complete_row_true(self, board: PlayerBoard):
        # Fill entire first row
        for col in range(5):
            board.wall[0][col] = True

        assert board.has_complete_row()

    def test_has_complete_row_multiple_rows(self, board: PlayerBoard):
        # Fill multiple rows
        for col in range(5):
            board.wall[0][col] = True
            board.wall[2][col] = True

        assert board.has_complete_row()

    def test_count_complete_horizontal_lines_none(self, board: PlayerBoard):
        assert board.count_complete_horizontal_lines() == 0

    def test_count_complete_horizontal_lines_partial(self, board: PlayerBoard):
        # Partially fill rows
        board.wall[0][0] = True
        board.wall[1][0] = True
        board.wall[1][1] = True

        assert board.count_complete_horizontal_lines() == 0

    def test_count_complete_horizontal_lines_single(self, board: PlayerBoard):
        # Fill one complete row
        for col in range(5):
            board.wall[0][col] = True

        assert board.count_complete_horizontal_lines() == 1

    def test_count_complete_horizontal_lines_multiple(self, board: PlayerBoard):
        # Fill multiple complete rows
        for row in [0, 2, 4]:
            for col in range(5):
                board.wall[row][col] = True

        assert board.count_complete_horizontal_lines() == 3

    def test_count_complete_vertical_lines_none(self, board: PlayerBoard):
        assert board.count_complete_vertical_lines() == 0

    def test_count_complete_vertical_lines_single(self, board: PlayerBoard):
        # Fill one complete column
        for row in range(5):
            board.wall[row][0] = True

        assert board.count_complete_vertical_lines() == 1

    def test_count_complete_vertical_lines_multiple(self, board: PlayerBoard):
        # Fill multiple complete columns
        for col in [0, 2, 4]:
            for row in range(5):
                board.wall[row][col] = True

        assert board.count_complete_vertical_lines() == 3

    def test_count_complete_color_sets_none(self, board: PlayerBoard):
        assert board.count_complete_color_sets() == 0

    def test_count_complete_color_sets_partial(self, board: PlayerBoard):
        # Place some blue tiles but not all 5
        board.wall[0][0] = True  # Blue
        board.wall[1][1] = True  # Blue
        board.wall[2][2] = True  # Blue

        assert board.count_complete_color_sets() == 0

    def test_count_complete_color_sets_single(self, board: PlayerBoard):
        # Place all 5 blue tiles
        blue_positions = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        for row, col in blue_positions:
            board.wall[row][col] = True

        assert board.count_complete_color_sets() == 1

    def test_count_complete_color_sets_multiple(self, board: PlayerBoard):
        # Place all tiles of blue and red colors
        # Blue: diagonal positions
        blue_positions = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        for row, col in blue_positions:
            board.wall[row][col] = True

        # Red: positions where red appears in wall pattern
        red_positions = [(0, 2), (1, 3), (2, 4), (3, 0), (4, 1)]
        for row, col in red_positions:
            board.wall[row][col] = True

        assert board.count_complete_color_sets() == 2

    def test_calculate_final_score_no_bonuses(self, board: PlayerBoard):
        board.score = 25
        final_score = board.calculate_final_score()
        assert final_score == 25

    def test_calculate_final_score_with_horizontal_bonus(self, board: PlayerBoard):
        board.score = 20
        # Complete one row
        for col in range(5):
            board.wall[0][col] = True

        final_score = board.calculate_final_score()
        assert final_score == 22  # 20 + (1 * 2)

    def test_calculate_final_score_with_vertical_bonus(self, board: PlayerBoard):
        board.score = 15
        # Complete one column
        for row in range(5):
            board.wall[row][0] = True

        final_score = board.calculate_final_score()
        assert final_score == 22  # 15 + (1 * 7)

    def test_calculate_final_score_with_color_bonus(self, board: PlayerBoard):
        board.score = 10
        # Complete blue color set
        blue_positions = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        for row, col in blue_positions:
            board.wall[row][col] = True

        final_score = board.calculate_final_score()
        assert final_score == 20  # 10 + (1 * 10)

    def test_calculate_final_score_all_bonuses(self, board: PlayerBoard):
        board.score = 30

        # Complete first row (2 points)
        for col in range(5):
            board.wall[0][col] = True

        # Complete first column (7 points) - overlap with row
        for row in range(5):
            board.wall[row][0] = True

        # Complete blue color set (10 points) - includes (0,0)
        blue_positions = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        for row, col in blue_positions:
            board.wall[row][col] = True

        final_score = board.calculate_final_score()
        assert final_score == 49  # 30 + 2 + 7 + 10

    def test_calculate_final_score_negative_base_score(self, board: PlayerBoard):
        board.score = -5
        # Add some bonuses
        for col in range(5):
            board.wall[0][col] = True  # +2 points

        final_score = board.calculate_final_score()
        assert final_score == 0  # max(0, -5 + 2) = 0

    def test_calculate_final_score_large_bonuses_overcome_negative(
        self, board: PlayerBoard
    ):
        board.score = -10

        # Complete multiple rows and columns
        for i in range(3):
            for j in range(5):
                board.wall[i][j] = True  # 3 complete rows

        for j in range(2):
            for i in range(5):
                board.wall[i][j] = True  # 2 complete columns (overlap with rows)

        final_score = board.calculate_final_score()
        # -10 + (3 * 2) + (2 * 7) + (10 * 1) = -10 + 6 + 14 + 10 = 20
        assert final_score == 20

    def test_floor_penalties_constant(self, board: PlayerBoard):
        """Test that floor penalties are correctly defined"""
        expected_penalties = [-1, -1, -2, -2, -2, -3, -3]
        assert board.FLOOR_PENALTIES == expected_penalties


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
