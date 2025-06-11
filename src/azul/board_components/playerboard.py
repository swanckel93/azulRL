from .wall import Wall
from .stagingline import StagingLine
from .floorline import Floorline
from ..tile import TileType


class PlayerBoard:
    """Enhanced player board to track game state"""

    def __init__(self, player_id: int):
        self.player_id = player_id
        self.pattern_lines = [StagingLine(i + 1) for i in range(5)]  # Lines 1-5
        self.wall = Wall()
        self.floor_line = Floorline()
        self.score = 0

    def has_completed_horizontal_line(self) -> bool:
        """Check if any horizontal line on the wall is complete"""
        return self.wall.has_complete_horizontal_line()

    def can_place_tile_type_in_pattern_line(
        self, line_index: int, tile_type: TileType
    ) -> bool:
        """Check if tile type can be placed in pattern line"""
        if line_index < 0 or line_index >= 5:
            return False

        # Check if wall already has this color in corresponding row
        if self.wall.has_tile_type_in_row(line_index, tile_type):
            return False

        return self.pattern_lines[line_index].can_add_tile_type(tile_type)
